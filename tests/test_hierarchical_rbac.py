from django.test import TestCase, RequestFactory
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from apps.accounts.models import SectorChoices, HierarchyLevel, UserSectorAssignment
from apps.accounts.permissions import require_role, has_role, RoleRequiredMixin
from django.views import View
from django.http import HttpResponse

User = get_user_model()

class HierarchicalMultiSectorRBACTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Usuario Multi-Setor: Coordenador Tecnico e Analista Financeiro
        self.user_multi = User.objects.create_user(
            email='engenheiro.financeiro@pangea.com.br',
            password='Password#2026'
        )
        # Limpa atribuicoes padrao do signal para controle preciso do teste
        self.user_multi.sector_assignments.all().delete()

        # Atribuicao 1: Tecnico - Coordenacao (Nivel 3)
        UserSectorAssignment.objects.create(
            user=self.user_multi,
            sector=SectorChoices.TECNICO,
            level=HierarchyLevel.COORDENACAO,
            is_primary=True
        )

        # Atribuicao 2: Financeiro - Operacional (Nivel 2)
        UserSectorAssignment.objects.create(
            user=self.user_multi,
            sector=SectorChoices.FINANCEIRO,
            level=HierarchyLevel.OPERACIONAL,
            is_primary=False
        )

        # Usuario Diretor: Nivel 4 em Comercial
        self.user_diretor = User.objects.create_user(
            email='diretor@pangea.com.br',
            password='Password#2026'
        )
        self.user_diretor.sector_assignments.all().delete()
        UserSectorAssignment.objects.create(
            user=self.user_diretor,
            sector=SectorChoices.COMERCIAL,
            level=HierarchyLevel.DIRETORIA,
            is_primary=True
        )

        # Superusuario
        self.admin = User.objects.create_superuser(
            email='admin.root@pangea.com.br',
            password='AdminPassword#2026'
        )

    def test_multi_sector_assignment_count(self):
        self.assertEqual(self.user_multi.sector_assignments.count(), 2)
        primary = self.user_multi.get_primary_assignment()
        self.assertEqual(primary.sector, SectorChoices.TECNICO)
        self.assertEqual(primary.level, HierarchyLevel.COORDENACAO)

    def test_cumulative_hierarchy_inheritance(self):
        # Nivel 3 (Coordenacao) deve herdar Nivel 1 e 2 no setor Tecnico
        self.assertTrue(has_role(self.user_multi, SectorChoices.TECNICO, HierarchyLevel.ASSISTENTE))
        self.assertTrue(has_role(self.user_multi, SectorChoices.TECNICO, HierarchyLevel.OPERACIONAL))
        self.assertTrue(has_role(self.user_multi, SectorChoices.TECNICO, HierarchyLevel.COORDENACAO))
        
        # Mas NAO possui Nivel 4 (Diretoria) no setor Tecnico
        self.assertFalse(has_role(self.user_multi, SectorChoices.TECNICO, HierarchyLevel.DIRETORIA))

    def test_cross_sector_independence(self):
        # No setor Financeiro, o usuario possui apenas Nivel 2
        self.assertTrue(has_role(self.user_multi, SectorChoices.FINANCEIRO, HierarchyLevel.OPERACIONAL))
        # Nao possui Nivel 3 (Coordenacao Financeira)
        self.assertFalse(has_role(self.user_multi, SectorChoices.FINANCEIRO, HierarchyLevel.COORDENACAO))

        # Nao possui vinculo algum no setor Comercial
        self.assertFalse(has_role(self.user_multi, SectorChoices.COMERCIAL, HierarchyLevel.ASSISTENTE))

    def test_require_role_decorator_authorization(self):
        @require_role(SectorChoices.TECNICO, min_level=HierarchyLevel.COORDENACAO)
        def despachar_os_tecnica(request):
            return "os_despachada"

        @require_role(SectorChoices.TECNICO, min_level=HierarchyLevel.DIRETORIA)
        def entrega_definitiva_obra(request):
            return "obra_entregue"

        req = self.factory.post('/tecnico/os/1/')
        req.user = self.user_multi

        # Deve passar pois possui Nivel 3 em Tecnico
        self.assertEqual(despachar_os_tecnica(req), "os_despachada")

        # Deve falhar com PermissionDenied pois exige Nivel 4
        with self.assertRaises(PermissionDenied):
            entrega_definitiva_obra(req)

    def test_require_role_multiple_alternatives_or_logic(self):
        # Permite: Liberacao por Coordenador Financeiro OU Diretor Comercial
        @require_role([
            (SectorChoices.FINANCEIRO, HierarchyLevel.COORDENACAO),
            (SectorChoices.COMERCIAL, HierarchyLevel.DIRETORIA)
        ])
        def aprovar_aditivo_contratual(request):
            return "aditivo_aprovado"

        req_multi = self.factory.post('/aditivo/')
        req_multi.user = self.user_multi

        # user_multi tem Financeiro Nivel 2 (nao atinge 3) e nao tem Comercial -> Bloqueia
        with self.assertRaises(PermissionDenied):
            aprovar_aditivo_contratual(req_multi)

        # user_diretor tem Comercial Nivel 4 -> Aprova
        req_diretor = self.factory.post('/aditivo/')
        req_diretor.user = self.user_diretor
        self.assertEqual(aprovar_aditivo_contratual(req_diretor), "aditivo_aprovado")

    def test_cbv_role_required_mixin(self):
        class DespesaView(RoleRequiredMixin, View):
            required_sector = SectorChoices.FINANCEIRO
            min_level = HierarchyLevel.COORDENACAO

            def get(self, request):
                return HttpResponse("autorizado_cbv")

        req = self.factory.get('/despesas/')
        req.user = self.user_multi

        view = DespesaView.as_view()
        with self.assertRaises(PermissionDenied):
            view(req)

    def test_superuser_bypass_hierarchy(self):
        req = self.factory.get('/qualquer/')
        req.user = self.admin

        @require_role(SectorChoices.ADMINISTRATIVO, min_level=HierarchyLevel.DIRETORIA)
        def view_super_restrita(request):
            return "super_ok"

        self.assertEqual(view_super_restrita(req), "super_ok")

    def test_primary_assignment_exclusivity(self):
        # Adiciona nova atribuicao como primaria
        assignment_comercial = UserSectorAssignment.objects.create(
            user=self.user_multi,
            sector=SectorChoices.COMERCIAL,
            level=HierarchyLevel.ASSISTENTE,
            is_primary=True
        )

        # O setor anterior (Tecnico) deve ter deixado de ser primario automaticamente
        assignment_tecnico = self.user_multi.sector_assignments.get(sector=SectorChoices.TECNICO)
        self.assertFalse(assignment_tecnico.is_primary)
        self.assertTrue(assignment_comercial.is_primary)
        self.assertEqual(self.user_multi.get_primary_assignment().sector, SectorChoices.COMERCIAL)
