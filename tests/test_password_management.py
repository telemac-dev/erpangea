from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail

User = get_user_model()

class PasswordManagementTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='colaborador.teste@pangea.eng.br',
            password='SenhaAntiga#123',
            first_name='Pedro',
            last_name='Alves'
        )
        self.client = Client()

    def test_authenticated_password_change_flow(self):
        # 1. Tentar acessar desautenticado redireciona para login
        res_anon = self.client.get('/accounts/password/change/')
        self.assertEqual(res_anon.status_code, 302)
        self.assertIn('/accounts/login/', res_anon.url)

        # 2. Autentica o usuario
        logged_in = self.client.login(username='colaborador.teste@pangea.eng.br', password='SenhaAntiga#123')
        self.assertTrue(logged_in)

        # 3. GET na tela de alteracao
        res = self.client.get('/accounts/password/change/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Definir Nova Senha')

        # 4. POST com senha antiga incorreta deve falhar
        res_fail = self.client.post('/accounts/password/change/', {
            'old_password': 'SenhaErrada#999',
            'new_password1': 'NovaSenhaSegura#2026',
            'new_password2': 'NovaSenhaSegura#2026',
        })
        self.assertEqual(res_fail.status_code, 200)
        self.assertTrue(self.user.check_password('SenhaAntiga#123'))

        # 5. POST com dados validos
        res_success = self.client.post('/accounts/password/change/', {
            'old_password': 'SenhaAntiga#123',
            'new_password1': 'NovaSenhaSegura#2026',
            'new_password2': 'NovaSenhaSegura#2026',
        })
        self.assertEqual(res_success.status_code, 302)
        self.assertIn('/accounts/profile/', res_success.url)

        # 6. Valida que a nova senha esta ativa
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NovaSenhaSegura#2026'))

        # 7. Novo login com a senha atualizada
        self.client.logout()
        new_login = self.client.login(username='colaborador.teste@pangea.eng.br', password='NovaSenhaSegura#2026')
        self.assertTrue(new_login)

    def test_forgotten_password_reset_flow(self):
        # 1. GET na tela de solicitacao de reset
        res_reset_get = self.client.get('/accounts/password/reset/')
        self.assertEqual(res_reset_get.status_code, 200)
        self.assertContains(res_reset_get, 'Recuperar Acesso')

        # 2. POST com o e-mail cadastrado
        res_reset_post = self.client.post('/accounts/password/reset/', {
            'email': 'colaborador.teste@pangea.eng.br'
        })
        self.assertEqual(res_reset_post.status_code, 302)
        self.assertIn('/accounts/password/reset/done/', res_reset_post.url)

        # 3. GET na tela de confirmacao de envio
        res_done = self.client.get('/accounts/password/reset/done/')
        self.assertEqual(res_done.status_code, 200)
        self.assertContains(res_done, 'Instruções Despachadas')

        # 4. Verifica disparo do e-mail no outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn('[ERPangea] Redefinição de Senha', mail.outbox[0].subject)

        # 5. Gera token e uid validos para simular clique no link
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        confirm_url = f'/accounts/password/reset/{uid}/{token}/'

        # O Django 5.x/6.x redireciona internamente para set-password para ocultar o token do Referrer
        res_confirm_get = self.client.get(confirm_url, follow=True)
        self.assertEqual(res_confirm_get.status_code, 200)
        self.assertContains(res_confirm_get, 'Nova Senha Corporativa')

        # 6. POST com a nova senha escolhida pelo usuario
        res_confirm_post = self.client.post(res_confirm_get.request['PATH_INFO'], {
            'new_password1': 'SenhaRedefinidaComSucesso#2026',
            'new_password2': 'SenhaRedefinidaComSucesso#2026',
        }, follow=True)
        self.assertEqual(res_confirm_post.status_code, 200)
        self.assertContains(res_confirm_post, 'Senha Redefinida!')

        # 7. Valida autenticacao do usuario com a nova senha redefinida
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('SenhaRedefinidaComSucesso#2026'))
        logged_in = self.client.login(username='colaborador.teste@pangea.eng.br', password='SenhaRedefinidaComSucesso#2026')
        self.assertTrue(logged_in)
