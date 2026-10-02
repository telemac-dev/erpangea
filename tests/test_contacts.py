import io
import csv
from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from apps.contacts.models import Contact, ContactTag, ContactTypeChoices, AddressTypeChoices, DocTypeChoices
from apps.audit_log.models import AuditLog, AuditActionChoices

User = get_user_model()

class ContactsModuleTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            email='admin.contacts@pangea.com.br',
            password='AdminPassword#2026'
        )
        self.client = Client()
        self.client.force_login(self.user)

        self.tag_vip = ContactTag.objects.create(name='VIP', color='#2563eb')
        self.tag_fornecedor = ContactTag.objects.create(name='Fornecedor', color='#10b981')

    # Cenário 1: Cadastro de Empresa com Validação de CNPJ
    def test_company_cnpj_validation(self):
        # 1.1 CNPJ matematicamente inválido deve ser rejeitado no clean()
        invalid_company = Contact(
            name='Empresa Inválida Ltda',
            contact_type=ContactTypeChoices.COMPANY,
            doc_type=DocTypeChoices.CNPJ,
            doc_number='11.111.111/1111-11' # Dígitos repetidos
        )
        with self.assertRaises(ValidationError):
            invalid_company.full_clean()

        # 1.2 CNPJ válido (ex: 11.222.333/0001-81) deve ser aceito e normalizado
        valid_company = Contact(
            name='Pangea Geotecnia e Fundações Ltda',
            trade_name='Pangea Fundações',
            contact_type=ContactTypeChoices.COMPANY,
            doc_type=DocTypeChoices.CNPJ,
            doc_number='11.222.333/0001-81',
            city='São Paulo',
            state='SP'
        )
        valid_company.full_clean()
        valid_company.save()
        self.assertEqual(valid_company.doc_number, '11222333000181')
        self.assertEqual(valid_company.formatted_doc_number, '11.222.333/0001-81')

        # 1.3 Endpoint assíncrono HTMX - Rejeição de CNPJ inválido
        res_htmx_invalid = self.client.post('/contacts/validate-document/', {
            'doc_number': '11111111111111',
            'doc_type': 'CNPJ'
        })
        self.assertContains(res_htmx_invalid, 'inválido')

        # 1.4 Endpoint assíncrono HTMX - Alerta de duplicidade quando o documento já existe
        res_htmx_duplicate = self.client.post('/contacts/validate-document/', {
            'doc_number': '11222333000181',
            'doc_type': 'CNPJ'
        })
        self.assertContains(res_htmx_duplicate, 'Documento já cadastrado')

        # 1.5 Endpoint assíncrono HTMX - Sucesso quando fornecido documento válido inédito (Filial 0002-62)
        res_htmx_valid = self.client.post('/contacts/validate-document/', {
            'doc_number': '11222333000262',
            'doc_type': 'CNPJ'
        })
        self.assertContains(res_htmx_valid, 'CNPJ Válido')

        # 1.6 Endpoint assíncrono HTMX - Sucesso ao editar o próprio contato titular
        res_htmx_self = self.client.post('/contacts/validate-document/', {
            'doc_number': '11222333000181',
            'doc_type': 'CNPJ',
            'contact_id': str(valid_company.pk)
        })
        self.assertContains(res_htmx_self, 'CNPJ Válido')

    # Cenário 2: Adição de Contato Subordinado
    def test_subordinate_contact_and_hierarchy(self):
        company = Contact.objects.create(
            name='Acme Obras Pesadas S.A.',
            contact_type=ContactTypeChoices.COMPANY,
            city='Belo Horizonte',
            state='MG'
        )
        
        # Cria contato subordinado
        sub = Contact.objects.create(
            name='Roberto Engenheiro',
            parent=company,
            contact_type=ContactTypeChoices.INDIVIDUAL,
            job_title='Coordenador de Canteiro',
            email='roberto@acmeobras.com.br'
        )

        self.assertEqual(sub.parent, company)
        self.assertEqual(sub.complete_name, 'Acme Obras Pesadas S.A., Roberto Engenheiro')
        self.assertIn(sub, company.subordinates.all())

        # Auto-referência na empresa mãe deve ser bloqueada
        company.parent = company
        with self.assertRaises(ValidationError):
            company.clean()

    # Cenário 3: Bloqueio de Duplicidade de Documento
    def test_duplicate_document_rejection(self):
        Contact.objects.create(
            name='Primeiro Titular',
            contact_type=ContactTypeChoices.INDIVIDUAL,
            doc_type=DocTypeChoices.CPF,
            doc_number='12345678909'
        )

        # Tentar cadastrar segundo contato ativo com o mesmo documento deve falhar
        duplicate = Contact(
            name='Segundo Titular',
            contact_type=ContactTypeChoices.INDIVIDUAL,
            doc_type=DocTypeChoices.CPF,
            doc_number='123.456.789-09'
        )
        with self.assertRaises(ValidationError) as cm:
            duplicate.clean()
        self.assertIn('doc_number', cm.exception.message_dict)

    # Cenário 4: Arquivamento e Desarquivamento (Soft Delete)
    def test_soft_delete_archive_and_unarchive(self):
        contact = Contact.objects.create(
            name='Consultoria Histórica Ltda',
            contact_type=ContactTypeChoices.COMPANY
        )
        self.assertTrue(contact.is_active)

        # Arquiva
        contact.archive()
        contact.refresh_from_db()
        self.assertFalse(contact.is_active)

        # Desaparece da listagem ativa
        res_active = self.client.get('/contacts/')
        self.assertNotContains(res_active, 'Consultoria Histórica Ltda')

        # Aparece na listagem com filtro de arquivados
        res_archived = self.client.get('/contacts/?filter=archived')
        self.assertContains(res_archived, 'Consultoria Histórica Ltda')

        # Desarquiva
        contact.unarchive()
        contact.refresh_from_db()
        self.assertTrue(contact.is_active)

    # Cenário 5: Assistente de Mesclagem de Contatos Duplicados
    def test_contact_merge_wizard(self):
        c1 = Contact.objects.create(name='Pangea Engenharia Principal', contact_type=ContactTypeChoices.COMPANY)
        c2 = Contact.objects.create(name='Pangea Engenharia Secundária', contact_type=ContactTypeChoices.COMPANY)
        
        # Subordinado vinculado a c2
        sub = Contact.objects.create(name='Cadista da Unidade 2', parent=c2, contact_type=ContactTypeChoices.INDIVIDUAL)

        # Dispara mesclagem elegendo c1 como destino
        res_merge = self.client.post('/contacts/merge/', {
            'contact_ids': f"{c1.pk},{c2.pk}",
            'destination_contact': str(c1.pk)
        })
        self.assertEqual(res_merge.status_code, 200)

        # c2 deve ter sido arquivado
        c2.refresh_from_db()
        self.assertFalse(c2.is_active)

        # O subordinado de c2 agora pertence a c1
        sub.refresh_from_db()
        self.assertEqual(sub.parent, c1)

    # Cenário 6: Exportação e Download de Modelo
    def test_export_and_template_download(self):
        Contact.objects.create(name='Contato Exportação Teste', email='export@pangea.com.br')
        
        # Teste Exportação CSV
        res_csv = self.client.get('/contacts/export/?format=csv')
        self.assertEqual(res_csv.status_code, 200)
        self.assertEqual(res_csv['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('Contato Exportação Teste', res_csv.content.decode('utf-8'))

        # Teste Exportação XLSX
        res_xlsx = self.client.get('/contacts/export/?format=xlsx')
        self.assertEqual(res_xlsx.status_code, 200)
        self.assertEqual(res_xlsx['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        # Teste Download Modelo de Importação
        res_template = self.client.get('/contacts/import/template/')
        self.assertEqual(res_template.status_code, 200)
        self.assertIn('nome_razao_social', res_template.content.decode('utf-8'))

    # Cenário 7: Trilha de Auditoria Imutável
    def test_contacts_audit_trail_logging(self):
        initial_logs = AuditLog.objects.filter(model_name='contact').count()

        c = Contact.objects.create(
            name='Auditada Engenharia Ltda',
            contact_type=ContactTypeChoices.COMPANY,
            city='Campinas'
        )

        # Verifica se o post_save gerou registro CREATE
        logs_after_create = AuditLog.objects.filter(model_name='contact', object_id=str(c.pk))
        self.assertTrue(logs_after_create.filter(action=AuditActionChoices.CREATE).exists())

        # Atualiza o contato
        c.city = 'Ribeirão Preto'
        c.save()

        # Verifica se gerou registro UPDATE
        self.assertTrue(logs_after_create.filter(action=AuditActionChoices.UPDATE).exists())

    # Cenário 8: Integração com API ViaCEP e Preenchimento Automático Opcional
    def test_cep_lookup_view_and_manual_editability(self):
        # 8.1 CEP Válido
        res_valid = self.client.get('/contacts/cep-lookup/?cep=01310-100')
        self.assertEqual(res_valid.status_code, 200)
        data = res_valid.json()
        self.assertTrue(data['found'])
        self.assertIn('Paulista', data['street'])
        self.assertEqual(data['city'], 'São Paulo')
        self.assertEqual(data['state'], 'SP')

        # 8.2 CEP com Formato Inválido (< 8 dígitos)
        res_invalid = self.client.get('/contacts/cep-lookup/?cep=123')
        self.assertEqual(res_invalid.status_code, 400)
        self.assertFalse(res_invalid.json()['found'])

        # 8.3 CEP Inexistente na Base dos Correios
        res_notfound = self.client.get('/contacts/cep-lookup/?cep=00000-000')
        self.assertEqual(res_notfound.status_code, 200)
        data_nf = res_notfound.json()
        self.assertFalse(data_nf['found'])
        self.assertIn('não localizado', data_nf['message'])

        # 8.4 Caráter Opcional e Edição Manual Plena
        # O usuário pode salvar um endereço totalmente manual, sem CEP ou com dados customizados
        custom_contact = Contact(
            name='Canteiro Remoto Sem CEP',
            contact_type=ContactTypeChoices.COMPANY,
            street='Estrada Vicinal da Mina Velha',
            number='Km 12',
            neighborhood='Zona Rural',
            city='Itabira',
            state='MG',
            postal_code='' # Sem CEP
        )
        custom_contact.full_clean()
        custom_contact.save()

        self.assertEqual(custom_contact.street, 'Estrada Vicinal da Mina Velha')
        self.assertEqual(custom_contact.postal_code, '')
        self.assertIn('Km 12', custom_contact.display_address)
