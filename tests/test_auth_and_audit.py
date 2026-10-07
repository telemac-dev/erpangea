from django.test import TestCase, Client, RequestFactory
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.accounts.models import UserProfile, SectorChoices, HierarchyLevel
from apps.accounts.permissions import require_role, has_role
from apps.audit_log.models import AuditLog, AuditActionChoices
from apps.audit_log.tasks import record_audit_log_async

User = get_user_model()

class CustomUserAndRBACTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='engenheiro@pangea.com.br',
            password='SenhaSegura#2026',
            first_name='Carlos',
            last_name='Silva'
        )

    def test_user_creation_and_uuid(self):
        self.assertEqual(self.user.email, 'engenheiro@pangea.com.br')
        self.assertIsNotNone(self.user.pk)
        self.assertEqual(len(str(self.user.pk)), 36) # Formato UUIDv4
        self.assertTrue(self.user.check_password('SenhaSegura#2026'))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_superuser_creation(self):
        admin = User.objects.create_superuser(
            email='admin@pangea.com.br',
            password='AdminPassword#2026'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_profile_and_default_sector_provisioning(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        primary = self.user.get_primary_assignment()
        self.assertIsNotNone(primary)
        self.assertEqual(primary.sector, SectorChoices.TECNICO)
        self.assertEqual(primary.level, HierarchyLevel.OPERACIONAL)
        self.assertEqual(self.user.profile.user, self.user)

    def test_brute_force_protection_lockout(self):
        self.assertFalse(self.user.is_locked())
        for _ in range(5):
            self.user.register_failed_login(max_attempts=5, lock_duration_minutes=15)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_locked())
        self.assertGreater(self.user.locked_until, timezone.now())

        self.user.reset_failed_logins()
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_locked())
        self.assertEqual(self.user.failed_login_attempts, 0)

    def test_rbac_sector_access_control(self):
        self.assertTrue(has_role(self.user, SectorChoices.TECNICO, min_level=HierarchyLevel.OPERACIONAL))
        self.assertFalse(has_role(self.user, SectorChoices.FINANCEIRO, min_level=HierarchyLevel.OPERACIONAL))

        @require_role(SectorChoices.FINANCEIRO, min_level=HierarchyLevel.OPERACIONAL)
        def view_financeira(request):
            return "ok_financeiro"

        factory = RequestFactory()
        req = factory.get('/financeiro/')
        req.user = self.user

        with self.assertRaises(PermissionDenied):
            view_financeira(req)

class AuditTrailImmutabilityTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='auditor@pangea.com.br',
            password='AuditorPassword#2026'
        )
        self.client = Client()

    def test_audit_log_immutability_on_update(self):
        log = AuditLog.objects.create(
            user=self.user,
            action=AuditActionChoices.CREATE,
            app_label='accounts',
            model_name='user',
            object_id=str(self.user.pk),
            object_repr=str(self.user),
            changes={'info': 'Criacao inicial'}
        )
        
        log.object_repr = "Modificacao ilegal"
        with self.assertRaises(PermissionDenied):
            log.save()

    def test_audit_log_immutability_on_delete(self):
        log = AuditLog.objects.create(
            user=self.user,
            action=AuditActionChoices.CREATE,
            app_label='accounts',
            model_name='user',
            object_id=str(self.user.pk),
            object_repr=str(self.user)
        )
        
        with self.assertRaises(PermissionDenied):
            log.delete()

    def test_authentication_audit_event_logging(self):
        initial_count = AuditLog.objects.filter(action=AuditActionChoices.LOGIN).count()
        
        logged_in = self.client.login(username='auditor@pangea.com.br', password='AuditorPassword#2026')
        self.assertTrue(logged_in)
        
        login_logs = AuditLog.objects.filter(action=AuditActionChoices.LOGIN, user=self.user)
        self.assertEqual(login_logs.count(), initial_count + 1)

    def test_async_audit_task_via_celery(self):
        initial_count = AuditLog.objects.count()
        record_audit_log_async(
            action=AuditActionChoices.EXPORT,
            app_label='reporting',
            model_name='relatorio',
            object_id='100',
            object_repr='Relatorio Mensal',
            changes={'formato': 'PDF'},
            user_id=self.user.pk,
            ip_address='192.168.1.50',
            user_agent='Mozilla/5.0'
        )
        self.assertEqual(AuditLog.objects.count(), initial_count + 1)
        last_log = AuditLog.objects.first()
        self.assertEqual(last_log.action, AuditActionChoices.EXPORT)
        self.assertEqual(last_log.ip_address, '192.168.1.50')

    def test_django_admin_user_creation(self):
        admin = User.objects.create_superuser(
            email='admin.gestao@pangea.eng.br',
            password='AdminPassword#2026'
        )
        client = Client()
        client.force_login(admin)

        # GET na tela de adicionar
        res_get = client.get('/admin/accounts/user/add/')
        self.assertEqual(res_get.status_code, 200)
        self.assertContains(res_get, 'password1')
        self.assertContains(res_get, 'password2')

        # POST criando novo colaborador
        res_post = client.post('/admin/accounts/user/add/', {
            'email': 'novo.engenheiro.admin@pangea.eng.br',
            'password1': 'SenhaSegura#2026',
            'password2': 'SenhaSegura#2026',
            'first_name': 'Juliana',
            'last_name': 'Costas',
            'is_staff': True,
            'is_active': True,
            '_save': 'Salvar'
        })
        self.assertEqual(res_post.status_code, 302)

        new_user = User.objects.filter(email='novo.engenheiro.admin@pangea.eng.br').first()
        self.assertIsNotNone(new_user)
        self.assertTrue(new_user.check_password('SenhaSegura#2026'))
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertTrue(new_user.sector_assignments.exists())
