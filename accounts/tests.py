from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser, UserRoleChoices

class UserAccessLevelTests(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_user(
            username='admin_test', password='password123', role=UserRoleChoices.ADMINISTRATOR
        )
        self.manager_user = CustomUser.objects.create_user(
            username='manager_test', password='password123', role=UserRoleChoices.MANAGER
        )
        self.collab_user = CustomUser.objects.create_user(
            username='collab_test', password='password123', role=UserRoleChoices.COLLABORATOR
        )

    def test_role_properties(self):
        self.assertTrue(self.admin_user.is_admin)
        self.assertTrue(self.admin_user.is_manager)
        self.assertTrue(self.admin_user.can_access_financials)

        self.assertFalse(self.manager_user.is_admin)
        self.assertTrue(self.manager_user.is_manager)
        self.assertTrue(self.manager_user.can_access_financials)

        self.assertFalse(self.collab_user.is_admin)
        self.assertFalse(self.collab_user.is_manager)
        self.assertFalse(self.collab_user.can_access_financials)

    def test_collaborator_denied_financial_access(self):
        self.client.login(username='collab_test', password='password123')
        response = self.client.get(reverse('invoice_list'))
        # Should redirect to home with error message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_manager_allowed_financial_access(self):
        self.client.login(username='manager_test', password='password123')
        response = self.client.get(reverse('invoice_list'))
        self.assertEqual(response.status_code, 200)

    def test_admin_user_management(self):
        self.client.login(username='admin_test', password='password123')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'collab_test')

        # Edit user role
        response = self.client.post(reverse('user_edit', args=[self.collab_user.pk]), {
            'username': 'collab_test',
            'role': UserRoleChoices.MANAGER,
            'is_active': True,
        })
        self.assertEqual(response.status_code, 302)
        
        self.collab_user.refresh_from_db()
        self.assertEqual(self.collab_user.role, UserRoleChoices.MANAGER)
