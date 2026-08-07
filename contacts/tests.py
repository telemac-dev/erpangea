from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Contact, ContactRole, ContactRoleChoices, Interaction

User = get_user_model()

class ContactsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='engineer', password='password123')
        self.client.login(username='engineer', password='password123')
        
        for role_choice in ContactRoleChoices.choices:
            ContactRole.objects.get_or_create(name=role_choice[0])
            
        self.role_client = ContactRole.objects.get(name=ContactRoleChoices.CLIENT)
        self.role_partner = ContactRole.objects.get(name=ContactRoleChoices.PARTNER)

    def test_contact_creation_valid_cnpj_unformatted(self):
        response = self.client.post(reverse('contact_create'), {
            'name': 'Construtora Exemplo Ltda',
            'trade_name': 'Exemplo Construtora',
            'person_type': 'PJ',
            'document': '11222333000181',
            'zip_code': '01001000',
            'email': 'contato@exemplo.com.br',
            'phone': '(11) 99999-8888',
            'roles': [self.role_client.pk],
            'is_active': True,
        })
        self.assertEqual(response.status_code, 302)
        
        contact = Contact.objects.get(name='Construtora Exemplo Ltda')
        self.assertEqual(contact.document, '11.222.333/0001-81')
        self.assertEqual(contact.zip_code, '01001-000')

    def test_contact_creation_valid_cpf_unformatted(self):
        response = self.client.post(reverse('contact_create'), {
            'name': 'Engenheiro Silva',
            'person_type': 'PF',
            'document': '11144477735',
            'is_active': True,
        })
        self.assertEqual(response.status_code, 302)
        
        contact = Contact.objects.get(name='Engenheiro Silva')
        self.assertEqual(contact.document, '111.444.777-35')

    def test_invalid_cpf_rejected(self):
        response = self.client.post(reverse('contact_create'), {
            'name': 'Engenheiro Falso',
            'person_type': 'PF',
            'document': '12345678900',
            'is_active': True,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'document', 'CPF inválido. Informe um número de CPF válido com 11 dígitos (ex: 123.456.789-00).')

    def test_htmx_format_document_cpf_on_blur(self):
        response = self.client.post(reverse('format_document_hx'), {
            'document': '11144477735',
            'person_type': 'PF',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '111.444.777-35')
        self.assertTemplateUsed(response, 'contacts/partials/document_field.html')

    @patch('urllib.request.urlopen')
    def test_htmx_lookup_cep_success(self, mock_urlopen):
        # Mock ViaCEP API response
        mock_response = MagicMock()
        mock_response.read.return_value = '{"cep": "01001-000", "logradouro": "Praça da Sé", "bairro": "Sé", "localidade": "São Paulo", "uf": "SP"}'.encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        response = self.client.post(reverse('lookup_cep_hx'), {
            'zip_code': '01001000',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Praça da Sé - Sé')
        self.assertContains(response, 'São Paulo')
        self.assertContains(response, 'SP')
        self.assertContains(response, '01001-000')
        self.assertTemplateUsed(response, 'contacts/partials/address_fields.html')

    def test_htmx_lookup_cep_invalid_length(self):
        response = self.client.post(reverse('lookup_cep_hx'), {
            'zip_code': '1234',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CEP inválido')

    def test_contact_list_filtering(self):
        c1 = Contact.objects.create(name='Alfa Geotecnia', person_type='PJ')
        c1.roles.add(self.role_client)

        c2 = Contact.objects.create(name='Beta Solos', person_type='PJ')
        c2.roles.add(self.role_partner)

        response = self.client.get(reverse('contact_list') + '?q=Alfa')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alfa Geotecnia')

    def test_add_interaction_to_contact(self):
        contact = Contact.objects.create(name='Prefeitura Municipal', person_type='PJ')
        
        response = self.client.post(reverse('contact_detail', args=[contact.pk]), {
            'interaction_type': 'REUNIAO',
            'subject': 'Apresentação de projeto geotécnico',
            'description': 'Reunião com secretário de obras sobre estabilidade de talude.',
            'next_action': 'Enviar proposta revisada',
        })
        self.assertEqual(response.status_code, 302)
        
        interaction = Interaction.objects.get(contact=contact)
        self.assertEqual(interaction.subject, 'Apresentação de projeto geotécnico')
