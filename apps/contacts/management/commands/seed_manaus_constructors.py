import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.contacts.models import (
    Contact,
    ContactTag,
    ContactTypeChoices,
    CompanySubtypeChoices,
    AddressTypeChoices,
    DocTypeChoices
)
from apps.contacts.management.commands.seed_contacts_50 import make_valid_cnpj, make_valid_cpf

User = get_user_model()

class Command(BaseCommand):
    help = "Popula o banco com 10 grandes construtoras e incorporadoras de Manaus/AM com SPEs, canteiros e prepostos"

    def handle(self, *args, **options):
        self.stdout.write("==> Populando 10 grandes Construtoras de Manaus/AM...")

        # 1. Recupera usuários comerciais
        users = list(User.objects.filter(is_active=True))
        if not users:
            users = [User.objects.first()]

        # 2. Garante Tags relevantes
        tag_cliente, _ = ContactTag.objects.get_or_create(name="Cliente Corporativo", defaults={'color': "#2563eb"})
        tag_incorporadora, _ = ContactTag.objects.get_or_create(name="Incorporadora & Real Estate", defaults={'color': "#0284c7"})
        tag_obras_pesadas, _ = ContactTag.objects.get_or_create(name="Mineração & Obras Pesadas", defaults={'color': "#b45309"})

        # 3. Definição das 10 Grandes Construtoras de Manaus
        manaus_companies = [
            {
                "seed": 801,
                "name": "Direcional Engenharia S.A. - Regional Amazonas",
                "trade_name": "Direcional Engenharia Manaus",
                "street": "Avenida Djalma Batista, 1661",
                "number": "Sala 701",
                "bairro": "Chapada",
                "cep": "69050-010",
                "phone": "(92) 3642-1000",
                "email": "manaus@direcional.com.br",
                "website": "https://www.direcional.com.br",
                "notes": "Líder em empreendimentos residenciais de grande porte em Manaus. Projetos contínuos de radier e fundações em estacas escavadas.",
                "director": ("Eng. Sérgio Murilo Guimarães", "Diretor Regional de Engenharia", "sergio.murilo@direcional.com.br", "(92) 9 9122-3344"),
                "job_site": ("Canteiro Residencial Reserva da Cidade", "Avenida Nathan Xavier de Albuquerque, s/n", "Novo Aleixo", "69098-000"),
                "spe": ("Reserva da Cidade Incorporadora SPE Ltda.", "Reserva da Cidade SPE", 8012)
            },
            {
                "name": "Construtora Capital S.A.",
                "trade_name": "Capital Engenharia",
                "seed": 802,
                "street": "Avenida André Araújo, 2153",
                "number": "Edifício Capital Center",
                "bairro": "Aleixo",
                "cep": "69060-000",
                "phone": "(92) 3659-2000",
                "email": "contato@capitalengenharia.com.br",
                "website": "https://www.capitalengenharia.com.br",
                "notes": "Uma das mais tradicionais construtoras do Amazonas. Obras de grande porte com contenções atirantadas e drenagem profunda.",
                "director": ("Eng. Fábio de Albuquerque", "Superintendente de Obras", "fabio.albuquerque@capitalengenharia.com.br", "(92) 9 9234-5566"),
                "job_site": ("Canteiro Edifício Maison Vivaldi", "Rua Terezina, 275", "Adrianópolis", "69057-070"),
                "spe": ("Capital Vivaldi Empreendimentos Imobiliários SPE S.A.", "Capital Vivaldi SPE", 8022)
            },
            {
                "name": "Engeco Engenharia e Construções Ltda.",
                "trade_name": "Engeco Construtora",
                "seed": 803,
                "street": "Rua Salvador, 440",
                "number": "Torre Engeco",
                "bairro": "Adrianópolis",
                "cep": "69057-040",
                "phone": "(92) 3303-4000",
                "email": "engenharia@engeco.com.br",
                "website": "https://www.engeco.com.br",
                "notes": "Pioneira em edifícios de altíssimo padrão arquitetônico em Manaus. Solos colapsíveis e fundações especiais.",
                "director": ("Dr. Márcio Tavares Pimenta", "Diretor Técnico de Projetos", "marcio.pimenta@engeco.com.br", "(92) 9 9345-7788"),
                "job_site": ("Canteiro Edifício Solar Tapajós", "Avenida Coronel Teixeira, 1850", "Ponta Negra", "69037-000"),
                "spe": ("Engeco Tapajós Empreendimento Imobiliário SPE Ltda.", "Engeco Tapajós SPE", 8032)
            },
            {
                "name": "RD Engenharia e Comércio Ltda.",
                "trade_name": "RD Engenharia",
                "seed": 804,
                "street": "Rua Belém, 892",
                "number": "Sede RD",
                "bairro": "Nossa Senhora das Graças",
                "cep": "69053-130",
                "phone": "(92) 3647-5000",
                "email": "comercial@rdengenharia.com.br",
                "website": "https://www.rdengenharia.com.br",
                "notes": "Forte atuação em habitação verticalizada e obras de infraestrutura urbana em Manaus.",
                "director": ("Eng. Carlos Alberto R. Dantas", "Diretor Presidente", "carlos.dantas@rdengenharia.com.br", "(92) 9 9155-8899"),
                "job_site": ("Canteiro Residencial Vista do Sol", "Avenida José Augusto Loureiro, 120", "Ponta Negra", "69037-025"),
                "spe": ("RD Vista do Sol Incorporação SPE Ltda.", "RD Vista do Sol SPE", 8042)
            },
            {
                "name": "Colmeia Incorporadora e Construtora S.A. - Manaus",
                "trade_name": "Construtora Colmeia",
                "seed": 805,
                "street": "Avenida Mário Ypiranga, 315",
                "number": "Sala 1204",
                "bairro": "Adrianópolis",
                "cep": "69057-000",
                "phone": "(92) 3642-6000",
                "email": "manaus@colmeia.com.br",
                "website": "https://www.colmeia.com.br",
                "notes": "Edifícios comerciais e corporativos icônicos. Obras em solos argilosos com necessidade de estacas hélice contínua.",
                "director": ("Engª. Patrícia Magalhães", "Coordenadora de Fundações e Estruturas", "patricia.m@colmeia.com.br", "(92) 9 9411-2233"),
                "job_site": ("Canteiro Comercial The Office Manaus", "Rua Rio Purus, 500", "Vieiralves", "69053-050"),
                "spe": ("Colmeia The Office Empreendimentos SPE S.A.", "Colmeia The Office SPE", 8052)
            },
            {
                "name": "Morar Mais Construções e Empreendimentos Ltda.",
                "trade_name": "Morar Mais Manaus",
                "seed": 806,
                "street": "Avenida Torquato Tapajós, 5200",
                "number": "Galpão 04",
                "bairro": "Flores",
                "cep": "69058-830",
                "phone": "(92) 3651-7000",
                "email": "contato@morarmaismanaus.com.br",
                "website": "https://www.morarmaismanaus.com.br",
                "notes": "Loteamentos fechados e condomínios horizontais. Projetos de estabilização de encostas e terraplanagem em Manaus.",
                "director": ("Eng. Luciano Barreto", "Gerente de Engenharia de Terra", "luciano@morarmaismanaus.com.br", "(92) 9 9522-3344"),
                "job_site": ("Canteiro Condomínio Quinta das Marinas", "Estrada da Marina, s/n", "Tarumã", "69041-000"),
                "spe": ("Morar Mais Quinta das Marinas SPE Ltda.", "Quinta das Marinas SPE", 8062)
            },
            {
                "name": "SKN Incorporadora e Engenharia Ltda.",
                "trade_name": "SKN Engenharia",
                "seed": 807,
                "street": "Avenida Coronel Teixeira, 500",
                "number": "Loja 12",
                "bairro": "Ponta Negra",
                "cep": "69037-000",
                "phone": "(92) 3302-8000",
                "email": "atendimento@sknincorporadora.com.br",
                "website": "https://www.sknincorporadora.com.br",
                "notes": "Empreendimentos de luxo na orla do Rio Negro. Contenções complexas de margem fluvial.",
                "director": ("Dr. Rodrigo Becker", "Diretor Técnico e Financeiro", "rodrigo.becker@sknincorporadora.com.br", "(92) 9 9633-4455"),
                "job_site": ("Canteiro Edifício Soberane Ponta Negra", "Rua Salvador, 80", "Adrianópolis", "69057-040"),
                "spe": ("SKN Soberane Ponta Negra SPE Ltda.", "SKN Soberane SPE", 8072)
            },
            {
                "name": "Cristal Engenharia e Construções Ltda.",
                "trade_name": "Cristal Engenharia",
                "seed": 808,
                "street": "Avenida Umberto Calderaro Filho, 455",
                "number": "Cristal Tower",
                "bairro": "Adrianópolis",
                "cep": "69057-015",
                "phone": "(92) 3648-9000",
                "email": "cristal@cristalengenharia.com.br",
                "website": "https://www.cristalengenharia.com.br",
                "notes": "Complexos multiuso integrados a shoppings centers em Manaus. Escavações profundas com rebaixamento de lençol freático.",
                "director": ("Eng. Gustavo H. Medeiros", "Gerente Geral de Obras Civis", "gustavo@cristalengenharia.com.br", "(92) 9 9744-5566"),
                "job_site": ("Canteiro Manauara Tower II", "Avenida Mário Ypiranga, 1300", "Adrianópolis", "69057-000"),
                "spe": ("Cristal Manauara Tower Empreendimento SPE S.A.", "Cristal Manauara SPE", 8082)
            },
            {
                "name": "Mosaico Engenharia e Projetos EIRELI",
                "trade_name": "Mosaico Engenharia Manaus",
                "seed": 809,
                "street": "Rua Rio Içá, 310",
                "number": "Sala 302",
                "bairro": "Vieiralves",
                "cep": "69053-100",
                "phone": "(92) 3236-1200",
                "email": "projetos@mosaicoam.com.br",
                "website": "https://www.mosaicoam.com.br",
                "notes": "Projetos industriais no Polo Industrial de Manaus (PIM). Fundações pesadas para prensas e pontes rolantes.",
                "director": ("Engª. Renata Mendonça", "Coordenadora de Projetos Industriais", "renata@mosaicoam.com.br", "(92) 9 9855-6677"),
                "job_site": ("Canteiro Galpão Fabril Foxconn PIM", "Avenida dos Oitis, 1500", "Distrito Industrial II", "69075-842"),
                "spe": ("Mosaico Industrial PIM 01 SPE Ltda.", "Mosaico PIM SPE", 8092)
            },
            {
                "name": "Tecnisa Amazonas Empreendimentos Imobiliários S.A.",
                "trade_name": "Tecnisa Manaus",
                "seed": 810,
                "street": "Avenida Darcy Vargas, 654",
                "number": "Sala 405",
                "bairro": "Parque Dez de Novembro",
                "cep": "69055-035",
                "phone": "(92) 3646-3300",
                "email": "manaus@tecnisa.com.br",
                "website": "https://www.tecnisa.com.br",
                "notes": "Empreendimentos residenciais de alta densidade. Laudos de estabilidade de encostas e ensaios de prova de carga.",
                "director": ("Eng. Bruno Camargo Lins", "Gerente Técnico de Contratos", "bruno.lins@tecnisa.com.br", "(92) 9 9966-7788"),
                "job_site": ("Canteiro Reserva Morada do Sol", "Alameda Cosme Ferreira, 2200", "Aleixo", "69083-000"),
                "spe": ("Tecnisa Morada do Sol SPE S.A.", "Tecnisa Morada do Sol SPE", 8102)
            }
        ]

        total_created = 0

        for idx, comp in enumerate(manaus_companies):
            salesperson = users[idx % len(users)]
            cnpj_matriz = make_valid_cnpj(comp["seed"], branch=1)

            # 1. Cria a Construtora Matriz
            matriz = Contact.objects.create(
                name=comp["name"],
                trade_name=comp["trade_name"],
                contact_type=ContactTypeChoices.COMPANY,
                company_subtype=CompanySubtypeChoices.MATRIZ,
                doc_type=DocTypeChoices.CNPJ,
                doc_number=cnpj_matriz,
                state_registration=f"04.{comp['seed']}.123-0",
                municipal_registration=f"IM-{comp['seed']}88",
                city="Manaus",
                state="AM",
                postal_code=comp["cep"],
                street=comp["street"],
                number=comp["number"],
                neighborhood=comp["bairro"],
                country="Brasil",
                phone=comp["phone"],
                email=comp["email"],
                website=comp["website"],
                salesperson=salesperson,
                payment_terms="30/60 dias após medição aprovada",
                internal_notes=comp["notes"],
                is_active=True
            )
            matriz.tags.add(tag_cliente, tag_incorporadora)
            total_created += 1
            self.stdout.write(self.style.SUCCESS(f" [OK] Construtora Matriz {idx+1}/10: {matriz.name} (CNPJ: {matriz.formatted_doc_number})"))

            # 2. Cria o Diretor / Engenheiro de Contato Subordinado
            dir_name, dir_job, dir_email, dir_phone = comp["director"]
            sub_person = Contact.objects.create(
                name=dir_name,
                parent=matriz,
                contact_type=ContactTypeChoices.INDIVIDUAL,
                address_type=AddressTypeChoices.CONTACT,
                job_title=dir_job,
                email=dir_email,
                mobile=dir_phone,
                city="Manaus",
                state="AM",
                salesperson=salesperson,
                is_active=True
            )
            total_created += 1
            self.stdout.write(f"       └── Preposto: {sub_person.name} ({sub_person.job_title})")

            # 3. Cria o Canteiro de Obras em Manaus (Local de Entrega)
            site_name, site_street, site_bairro, site_cep = comp["job_site"]
            sub_site = Contact.objects.create(
                name=site_name,
                parent=matriz,
                contact_type=ContactTypeChoices.INDIVIDUAL,
                address_type=AddressTypeChoices.DELIVERY,
                street=site_street,
                neighborhood=site_bairro,
                city="Manaus",
                state="AM",
                postal_code=site_cep,
                country="Brasil",
                salesperson=salesperson,
                internal_notes="Local autorizado para entrega de sondagens, projetos executivos e vistorias de campo.",
                is_active=True
            )
            total_created += 1
            self.stdout.write(f"       └── Canteiro de Obra: {sub_site.name} ({site_bairro})")

            # 4. Cria a Sociedade de Propósito Específico (SPE com CNPJ Próprio vinculada à Matriz)
            spe_name, spe_trade, spe_seed = comp["spe"]
            cnpj_spe = make_valid_cnpj(spe_seed, branch=1)
            spe_company = Contact.objects.create(
                name=spe_name,
                trade_name=spe_trade,
                parent=matriz, # Vinculada à Holding Matriz!
                contact_type=ContactTypeChoices.COMPANY,
                company_subtype=CompanySubtypeChoices.SPE,
                doc_type=DocTypeChoices.CNPJ,
                doc_number=cnpj_spe,
                city="Manaus",
                state="AM",
                postal_code=site_cep,
                street=site_street,
                neighborhood=site_bairro,
                country="Brasil",
                salesperson=salesperson,
                internal_notes=f"SPE constituída especificamente para o empreendimento {site_name}, controlada por {matriz.name}.",
                is_active=True
            )
            spe_company.tags.add(tag_cliente, tag_incorporadora)
            total_created += 1
            self.stdout.write(f"       └── SPE (CNPJ Próprio): {spe_company.name} (CNPJ: {spe_company.formatted_doc_number})")

        self.stdout.write(self.style.SUCCESS(
            f"\n==> SUCESSO: 10 GRANDES CONSTRUTORAS DE MANAUS CADASTRADAS!\n"
            f" -> Total de novos registros inseridos: {total_created} (10 Matrizes + 10 SPEs + 10 Prepostos + 10 Canteiros)\n"
            f" -> Total geral de contatos no ERPangea: {Contact.objects.count()}\n"
            f" -> Total de contatos de Manaus/AM: {Contact.objects.filter(city__iexact='Manaus').count()}"
        ))
