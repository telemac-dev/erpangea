from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.contacts.models import Contact, ContactTag, ContactTypeChoices, AddressTypeChoices, DocTypeChoices

User = get_user_model()

class Command(BaseCommand):
    help = "Popula dados de demonstração realistas para o módulo de Contatos da Pangea Engenharia"

    def handle(self, *args, **options):
        self.stdout.write("==> Populando base de Contatos...")

        admin_user = User.objects.filter(is_staff=True).first()

        # 1. Tags / Marcadores
        tag_cliente, _ = ContactTag.objects.get_or_create(name="Cliente Obras", defaults={'color': "#2563eb"})
        tag_fornecedor, _ = ContactTag.objects.get_or_create(name="Fornecedor Sondagem", defaults={'color': "#10b981"})
        tag_parceiro, _ = ContactTag.objects.get_or_create(name="Projetista Parceiro", defaults={'color': "#f59e0b"})
        tag_orgao, _ = ContactTag.objects.get_or_create(name="Órgão Ambiental / Público", defaults={'color': "#8b5cf6"})

        # 2. Empresa 1: Construtora Aliança
        c1, _ = Contact.objects.get_or_create(
            doc_number="11222333000181",
            defaults={
                'name': "Construtora Aliança de Infraestrutura S.A.",
                'trade_name': "Aliança Engenharia",
                'contact_type': ContactTypeChoices.COMPANY,
                'doc_type': DocTypeChoices.CNPJ,
                'state_registration': "110.220.330.440",
                'street': "Avenida Brigadeiro Faria Lima",
                'number': "3477",
                'complement': "14º Andar",
                'neighborhood': "Itaim Bibi",
                'city': "São Paulo",
                'state': "SP",
                'postal_code': "04538-133",
                'phone': "(11) 3040-5500",
                'email': "contato@aliancaeng.com.br",
                'website': "https://www.aliancaeng.com.br",
                'salesperson': admin_user,
                'payment_terms': "30/60 dias",
                'internal_notes': "Cliente corporativo de grande porte. Contratos de contenções em solo grampeado e estacas hélice.",
            }
        )
        c1.tags.add(tag_cliente)

        # Subordinados da Construtora Aliança
        sub1, _ = Contact.objects.get_or_create(
            name="Eng. Eduardo Rezende",
            parent=c1,
            defaults={
                'contact_type': ContactTypeChoices.INDIVIDUAL,
                'address_type': AddressTypeChoices.CONTACT,
                'job_title': "Diretor de Operações e Contratos",
                'email': "eduardo.rezende@aliancaeng.com.br",
                'mobile': "(11) 9 9123-4567",
                'city': "São Paulo",
                'state': "SP",
            }
        )

        sub2, _ = Contact.objects.get_or_create(
            name="Canteiro de Obras Rodovia SP-070",
            parent=c1,
            defaults={
                'contact_type': ContactTypeChoices.INDIVIDUAL,
                'address_type': AddressTypeChoices.DELIVERY,
                'street': "Rodovia Ayrton Senna, km 45",
                'number': "S/N",
                'city': "Guarulhos",
                'state': "SP",
                'postal_code': "07000-000",
                'internal_notes': "Local de entrega de maquinários e perfuratrizes.",
            }
        )

        # 3. Empresa 2: Geotécnica Perfurações
        c2, _ = Contact.objects.get_or_create(
            doc_number="22333444000192",
            defaults={
                'name': "SondaGeo Perfurações e Ensaios EIRELI",
                'trade_name': "SondaGeo",
                'contact_type': ContactTypeChoices.COMPANY,
                'doc_type': DocTypeChoices.CNPJ,
                'street': "Rua dos Topógrafos",
                'number': "120",
                'neighborhood': "Distrito Industrial",
                'city': "Campinas",
                'state': "SP",
                'postal_code': "13080-000",
                'phone': "(19) 3211-8899",
                'email': "operacoes@sondageo.com.br",
                'salesperson': admin_user,
                'payment_terms': "15 dias após medição",
                'internal_notes': "Fornecedor homologado para ensaios SPT e CPTu em campo.",
            }
        )
        c2.tags.add(tag_fornecedor)

        # 4. Pessoa Física Independente: Consultor Geotécnico
        c3, _ = Contact.objects.get_or_create(
            doc_number="12345678909",
            defaults={
                'name': "Prof. Dr. Milton Vargas Sobrinho",
                'contact_type': ContactTypeChoices.INDIVIDUAL,
                'doc_type': DocTypeChoices.CPF,
                'job_title': "Consultor Técnico Sênior em Mecânica dos Solos",
                'city': "São Paulo",
                'state': "SP",
                'mobile': "(11) 9 9876-1122",
                'email': "milton.vargas.consultoria@exemplo.com.br",
                'internal_notes': "Consultor parceiro para revisões de cálculo estrutural de muros de flexão e ancoragens.",
            }
        )
        c3.tags.add(tag_parceiro)

        self.stdout.write(self.style.SUCCESS(
            f" [OK] Contatos e vínculos populados com sucesso!\n"
            f" -> Total contatos ativos: {Contact.objects.filter(is_active=True).count()}"
        ))
