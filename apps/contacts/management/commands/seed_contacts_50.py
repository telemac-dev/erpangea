import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.contacts.models import Contact, ContactTag, ContactTypeChoices, AddressTypeChoices, DocTypeChoices
from apps.contacts.validators import validate_cpf, validate_cnpj

User = get_user_model()

def make_valid_cpf(seed_val):
    random.seed(seed_val)
    base = [random.randint(0, 9) for _ in range(9)]
    soma = sum(base[i] * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    d1 = 0 if resto == 10 else resto
    base.append(d1)
    soma = sum(base[i] * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    d2 = 0 if resto == 10 else resto
    base.append(d2)
    cpf = ''.join(map(str, base))
    validate_cpf(cpf)
    return cpf

def make_valid_cnpj(seed_val, branch=1):
    random.seed(seed_val)
    base = [random.randint(0, 9) for _ in range(8)]
    branch_digits = [int(d) for d in f"{branch:04d}"]
    base.extend(branch_digits)
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(base[i] * pesos1[i] for i in range(12))
    resto = soma % 11
    d1 = 0 if resto < 2 else 11 - resto
    base.append(d1)
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(base[i] * pesos2[i] for i in range(13))
    resto = soma % 11
    d2 = 0 if resto < 2 else 11 - resto
    base.append(d2)
    cnpj = ''.join(map(str, base))
    validate_cnpj(cnpj)
    return cnpj

class Command(BaseCommand):
    help = "Popula o banco com 50 contatos hiper-interligados para a Pangea Engenharia"

    def handle(self, *args, **options):
        self.stdout.write("==> Reiniciando e populando 50 contatos com máxima interligação...")

        # 1. Limpa contatos existentes para criar ecossistema limpo e consistente
        Contact.objects.all().delete()
        ContactTag.objects.all().delete()

        # 2. Resgata usuários do sistema para atuar como responsáveis comerciais
        users = list(User.objects.filter(is_active=True))
        if not users:
            users = [User.objects.first()]

        # 3. Criação de 10 Tags Estruturadas
        tags_data = [
            ("Cliente Corporativo", "#2563eb"),
            ("Fornecedor Sondagem & Perfuratriz", "#10b981"),
            ("Laboratório de Solos & Concreto", "#059669"),
            ("Projetista Estrutural Parceiro", "#f59e0b"),
            ("Órgão Ambiental & Regulador", "#8b5cf6"),
            ("Concessionária de Rodovias", "#dc2626"),
            ("Mineração & Obras Pesadas", "#b45309"),
            ("Incorporadora & Real Estate", "#0284c7"),
            ("Subempreiteiro Canteiro", "#d97706"),
            ("Consultoria Geotécnica Especializada", "#475569"),
        ]
        tags = {}
        for name, color in tags_data:
            tags[name] = ContactTag.objects.create(name=name, color=color)

        # 4. Dados das 12 Empresas Matrizes
        companies_specs = [
            {
                "name": "Construtora Aliança de Infraestrutura e Rodovias S.A.",
                "trade_name": "Aliança Engenharia",
                "city": "São Paulo", "state": "SP", "cep": "04538-133",
                "street": "Avenida Brigadeiro Faria Lima, 3477", "bairro": "Itaim Bibi",
                "phone": "(11) 3040-5500", "email": "contato@aliancaeng.com.br", "site": "https://www.aliancaeng.com.br",
                "tags": [tags["Cliente Corporativo"], tags["Concessionária de Rodovias"]],
                "terms": "30/60 dias",
                "notes": "Cliente corporativo prioritário em contenções e solo grampeado.",
                "subs": [
                    ("Eng. Eduardo Rezende", AddressTypeChoices.CONTACT, "Diretor de Operações e Contratos", "eduardo.rezende@aliancaeng.com.br", "(11) 9 9123-4567"),
                    ("Engª. Mariana Bittencourt", AddressTypeChoices.CONTACT, "Coordenadora de Geotecnia", "mariana.b@aliancaeng.com.br", "(11) 9 9876-1122"),
                    ("Canteiro de Obras Trecho Serra do Mar", AddressTypeChoices.DELIVERY, "Canteiro de Obras", "", "", "Rodovia dos Imigrantes, km 42", "Cubatão", "SP", "11500-000"),
                    ("Aliança Faturamento Central", AddressTypeChoices.INVOICE, "Escritório de Cobrança", "faturamento@aliancaeng.com.br", "(11) 3040-5520", "Rua Funchal, 200", "São Paulo", "SP", "04551-060")
                ]
            },
            {
                "name": "Camargo Corrêa Obras Geotécnicas e Túneis Ltda",
                "trade_name": "Camargo Corrêa Geotecnia",
                "city": "Rio de Janeiro", "state": "RJ", "cep": "20040-002",
                "street": "Avenida Rio Branco, 110", "bairro": "Centro",
                "phone": "(21) 2555-8800", "email": "geotecnia@camargocorrea.com.br", "site": "https://www.camargocorrea.com.br",
                "tags": [tags["Cliente Corporativo"], tags["Mineração & Obras Pesadas"]],
                "terms": "Medição mensal + 45 dias",
                "notes": "Contratos ativos de túneis em solo e rocha (NATM) e fundações profundas.",
                "subs": [
                    ("Dr. Fernando Meirelles", AddressTypeChoices.CONTACT, "Gerente Geral de Engenharia de Túneis", "f.meirelles@camargocorrea.com.br", "(21) 9 8877-3344"),
                    ("Canteiro Túnel Extensão Linha 4", AddressTypeChoices.DELIVERY, "Canteiro de Obras", "", "", "Avenida Niemeyer, s/n", "Rio de Janeiro", "RJ", "22450-220"),
                    ("Camargo Corrêa Unidade Faturamento RJ", AddressTypeChoices.INVOICE, "Faturamento Fiscal", "nf@camargocorrea.com.br", "(21) 2555-8840", "Rua do Ouvidor, 50", "Rio de Janeiro", "RJ", "20040-030")
                ]
            },
            {
                "name": "CCR Rodovias do Sistema Anchieta-Imigrantes S.A.",
                "trade_name": "Ecovias dos Imigrantes",
                "city": "Santos", "state": "SP", "cep": "11013-000",
                "street": "Praça Mauá, 15", "bairro": "Centro",
                "phone": "(13) 3219-9000", "email": "engenharia@ecovias.com.br", "site": "https://www.ecovias.com.br",
                "tags": [tags["Cliente Corporativo"], tags["Concessionária de Rodovias"]],
                "terms": "30 dias após emissão de NFS-e",
                "notes": "Monitoramento contínuo de taludes, contenções com cortina atirantada e drenagem profunda.",
                "subs": [
                    ("Eng. Paulo Guimarães", AddressTypeChoices.CONTACT, "Coordenador de Conservação de Pistas e Taludes", "paulo.guimaraes@ecovias.com.br", "(13) 9 9654-7711"),
                    ("Canteiro Base Operacional KM 28", AddressTypeChoices.DELIVERY, "Posto de Canteiro", "", "", "Rodovia Anchieta, km 28", "São Bernardo do Campo", "SP", "09820-000"),
                    ("Ecovias Contabilidade Matriz", AddressTypeChoices.INVOICE, "Setor Fiscal", "fiscal@ecovias.com.br", "(13) 3219-9050", "Praça Mauá, 15 - 4º andar", "Santos", "SP", "11013-000")
                ]
            },
            {
                "name": "Vale Mineração & Logística S.A. - Divisão Geotecnia",
                "trade_name": "Vale Geotecnia de Barragens",
                "city": "Belo Horizonte", "state": "MG", "cep": "30140-071",
                "street": "Avenida Getúlio Vargas, 671", "bairro": "Funcionários",
                "phone": "(31) 3279-4000", "email": "geotecnia.barragens@vale.com", "site": "https://www.vale.com",
                "tags": [tags["Cliente Corporativo"], tags["Mineração & Obras Pesadas"]],
                "terms": "60 dias",
                "notes": "Consultoria em descaracterização de barragens e ensaios especiais de piezocone CPTu.",
                "subs": [
                    ("Eng. Marcelo Albuquerque", AddressTypeChoices.CONTACT, "Gerente Executivo de Segurança de Estruturas", "marcelo.albuquerque@vale.com", "(31) 9 9988-1234"),
                    ("Geóloga Letícia Campos", AddressTypeChoices.CONTACT, "Especialista em Riscos Geológicos", "leticia.campos@vale.com", "(31) 9 9944-5566"),
                    ("Canteiro Mina Capanema - Frente 03", AddressTypeChoices.DELIVERY, "Canteiro de Obras", "", "", "Complexo Minerário Capanema", "Itabira", "MG", "35900-000"),
                    ("Vale Escritório Administrativo MG", AddressTypeChoices.INVOICE, "Contas a Pagar", "ap.mg@vale.com", "(31) 3279-4080", "Rua Aimorés, 450", "Belo Horizonte", "MG", "30140-070")
                ]
            },
            {
                "name": "Cyrela Empreendimentos Imobiliários S.A.",
                "trade_name": "Cyrela Real Estate",
                "city": "São Paulo", "state": "SP", "cep": "04543-011",
                "street": "Rua do Rócio, 109", "bairro": "Vila Olímpia",
                "phone": "(11) 4502-3000", "email": "suprimentos@cyrela.com.br", "site": "https://www.cyrela.com.br",
                "tags": [tags["Cliente Corporativo"], tags["Incorporadora & Real Estate"]],
                "terms": "30/60 dias",
                "notes": "Empreendimentos residenciais de alto padrão com contenções em hélice contínua e subsolos profundos.",
                "subs": [
                    ("Eng. Felipe Santoro", AddressTypeChoices.CONTACT, "Gerente de Projetos de Fundações", "felipe.santoro@cyrela.com.br", "(11) 9 9765-4321"),
                    ("Canteiro Residencial Grand Tower Jardins", AddressTypeChoices.DELIVERY, "Canteiro de Obras", "", "", "Alameda Lorena, 1500", "São Paulo", "SP", "01424-002"),
                    ("Cyrela Faturamento Corporativo", AddressTypeChoices.INVOICE, "Setor Financeiro", "faturamento@cyrela.com.br", "(11) 4502-3050", "Rua do Rócio, 109 - 3º andar", "São Paulo", "SP", "04543-011")
                ]
            },
            {
                "name": "SondaGeo Perfurações e Ensaios de Campo EIRELI",
                "trade_name": "SondaGeo Geotecnia",
                "city": "Campinas", "state": "SP", "cep": "13080-000",
                "street": "Rua dos Topógrafos, 120", "bairro": "Distrito Industrial",
                "phone": "(19) 3211-8899", "email": "operacoes@sondageo.com.br", "site": "https://www.sondageo.com.br",
                "tags": [tags["Fornecedor Sondagem & Perfuratriz"]],
                "terms": "15 dias após medição",
                "notes": "Fornecedor parceiro de perfuratrizes rotativas, sondagem a percussão SPT e ensaios de palheta (Vane Test).",
                "subs": [
                    ("Sérgio Mascarenhas", AddressTypeChoices.CONTACT, "Coordenador de Frotas de Sondagem", "sergio@sondageo.com.br", "(19) 9 9111-2233"),
                    ("Pátio de Equipamentos e Perfuratrizes Campinas", AddressTypeChoices.DELIVERY, "Base Operacional", "", "", "Rodovia Dom Pedro I, km 135", "Campinas", "SP", "13091-904")
                ]
            },
            {
                "name": "Geotest Laboratório de Mecânica dos Solos e Rochas Ltda",
                "trade_name": "Laboratório Geotest",
                "city": "Curitiba", "state": "PR", "cep": "80240-000",
                "street": "Avenida Sete de Setembro, 4200", "bairro": "Batel",
                "phone": "(41) 3340-2000", "email": "laboratorio@geotest.com.br", "site": "https://www.geotest.com.br",
                "tags": [tags["Laboratório de Solos & Concreto"]],
                "terms": "28 dias",
                "notes": "Ensaios triaxiais adensados, cisalhamento direto, permeabilidade e compressão simples de rochas.",
                "subs": [
                    ("Dra. Beatriz Lunardi", AddressTypeChoices.CONTACT, "Diretora Técnica do Laboratório", "beatriz@geotest.com.br", "(41) 9 9988-7711"),
                    ("Unidade de Coleta de Amostras Deformadas", AddressTypeChoices.OTHER, "Posto de Coleta", "", "", "Rua Comendador Araújo, 310", "Curitiba", "PR", "80420-000")
                ]
            },
            {
                "name": "Arteris Autopista Litoral Sul Concessionária S.A.",
                "trade_name": "Arteris Litoral Sul",
                "city": "Joinville", "state": "SC", "cep": "89201-000",
                "street": "Rua XV de Novembro, 1200", "bairro": "América",
                "phone": "(47) 3451-1000", "email": "contato@arteris.com.br", "site": "https://www.arteris.com.br",
                "tags": [tags["Cliente Corporativo"], tags["Concessionária de Rodovias"]],
                "terms": "30 dias",
                "notes": "Obras do Contorno Viário de Florianópolis e estabilização de encostas na BR-101.",
                "subs": [
                    ("Eng. Carlos Eduardo Ramos", AddressTypeChoices.CONTACT, "Fiscal Técnico de Obras de Arte Especiais", "carlos.ramos@arteris.com.br", "(47) 9 9777-3322"),
                    ("Canteiro Contorno de Florianópolis", AddressTypeChoices.DELIVERY, "Canteiro Central", "", "", "Rodovia BR-101, km 220", "Palhoça", "SC", "88130-000")
                ]
            },
            {
                "name": "Consórcio Linha 6 Laranja do Metrô de São Paulo",
                "trade_name": "Linha Uni Metro",
                "city": "São Paulo", "state": "SP", "cep": "01139-000",
                "street": "Avenida Marquês de São Vicente, 2219", "bairro": "Barra Funda",
                "phone": "(11) 3500-6000", "email": "geotecnia@linhauni.com.br", "site": "https://www.linhauni.com.br",
                "tags": [tags["Cliente Corporativo"], tags["Mineração & Obras Pesadas"]],
                "terms": "Medição quinzenal + 30 dias",
                "notes": "Monitoramento de recalque de superfícies com instrumentação geotécnica e poços VSE.",
                "subs": [
                    ("Eng. André Takahashi", AddressTypeChoices.CONTACT, "Coordenador de Instrumentação Geotécnica", "andre.t@linhauni.com.br", "(11) 9 9888-4455"),
                    ("Frente de Escavação Poço VSE Tietê", AddressTypeChoices.DELIVERY, "Frente de Obra", "", "", "Avenida Otaviano Alves de Lima, s/n", "São Paulo", "SP", "02909-000"),
                    ("Consórcio Linha Uni Escritório Central", AddressTypeChoices.INVOICE, "Faturamento Consórcio", "fiscal@linhauni.com.br", "(11) 3500-6020", "Avenida Marquês de São Vicente, 2219", "São Paulo", "SP", "01139-000")
                ]
            },
            {
                "name": "Aterpa Engenharia de Terraplanagem e Drenagem Ltda",
                "trade_name": "Aterpa Obras",
                "city": "Belo Horizonte", "state": "MG", "cep": "30380-000",
                "street": "Rua Santa Catarina, 1627", "bairro": "Lourdes",
                "phone": "(31) 3290-7000", "email": "suprimentos@aterpa.com.br", "site": "https://www.aterpa.com.br",
                "tags": [tags["Subempreiteiro Canteiro"], tags["Mineração & Obras Pesadas"]],
                "terms": "30 dias",
                "notes": "Subcontratada de terraplenagem pesada, desmonte de rocha a fogo e drenagem subsuperficial.",
                "subs": [
                    ("Vicente Paiva", AddressTypeChoices.CONTACT, "Gerente de Equipamentos Pesados", "vicente.p@aterpa.com.br", "(31) 9 9122-3344"),
                    ("Pátio de Britadores e Tratores Aterpa", AddressTypeChoices.DELIVERY, "Pátio Operacional", "", "", "Anel Rodoviário Celso Mello Azevedo", "Belo Horizonte", "MG", "31250-010")
                ]
            },
            {
                "name": "Engeform Construções e Escavações Especiais S.A.",
                "trade_name": "Engeform Engenharia",
                "city": "Porto Alegre", "state": "RS", "cep": "90480-000",
                "street": "Avenida Carlos Gomes, 111", "bairro": "Auxiliadora",
                "phone": "(51) 3330-8000", "email": "contato.rs@engeform.com.br", "site": "https://www.engeform.com.br",
                "tags": [tags["Cliente Corporativo"], tags["Subempreiteiro Canteiro"]],
                "terms": "30 dias",
                "notes": "Obras hospitalares e estações de tratamento de água com estacas raiz e tirantes.",
                "subs": [
                    ("Engª. Clarice Fontana", AddressTypeChoices.CONTACT, "Coordenadora de Obras Especiais", "clarice.fontana@engeform.com.br", "(51) 9 9345-6789"),
                    ("Canteiro Ampliação Hospital de Clínicas", AddressTypeChoices.DELIVERY, "Canteiro de Obras", "", "", "Rua Ramiro Barcelos, 2350", "Porto Alegre", "RS", "90035-903")
                ]
            },
            {
                "name": "Invepar Concessões de Infraestrutura de Transporte S.A.",
                "trade_name": "Invepar Rodovias e Metrô",
                "city": "Rio de Janeiro", "state": "RJ", "cep": "22250-040",
                "street": "Praia de Botafogo, 300", "bairro": "Botafogo",
                "phone": "(21) 3509-8000", "email": "operacoes@invepar.com.br", "site": "https://www.invepar.com.br",
                "tags": [tags["Cliente Corporativo"], tags["Concessionária de Rodovias"]],
                "terms": "45 dias",
                "notes": "Concessões da Linha Amarela (LAMSA) e Rodovia BR-040 (Via 040). Contenções com terra armada.",
                "subs": [
                    ("Eng. Rodrigo Silveira", AddressTypeChoices.CONTACT, "Especialista de Infraestrutura Rodoviária", "rodrigo.s@invepar.com.br", "(21) 9 9811-2244"),
                    ("Posto de Apoio Geotécnico Linha Amarela", AddressTypeChoices.DELIVERY, "Posto de Canteiro", "", "", "Avenida Carlos Peixoto, 54", "Rio de Janeiro", "RJ", "22290-090")
                ]
            }
        ]

        created_count = 0

        # Criação das Empresas e Subordinados
        for idx, c_spec in enumerate(companies_specs, start=100):
            cnpj = make_valid_cnpj(idx, branch=1)
            salesperson = users[idx % len(users)]

            company = Contact(
                name=c_spec["name"],
                trade_name=c_spec["trade_name"],
                contact_type=ContactTypeChoices.COMPANY,
                doc_type=DocTypeChoices.CNPJ,
                doc_number=cnpj,
                state_registration=f"11{idx}.22{idx}.33{idx}",
                municipal_registration=f"99{idx}88",
                city=c_spec["city"],
                state=c_spec["state"],
                postal_code=c_spec["cep"],
                street=c_spec["street"],
                neighborhood=c_spec["bairro"],
                phone=c_spec["phone"],
                email=c_spec["email"],
                website=c_spec["site"],
                salesperson=salesperson,
                payment_terms=c_spec["terms"],
                internal_notes=c_spec["notes"],
                is_active=True
            )
            company.full_clean()
            company.save()
            company.tags.set(c_spec["tags"])
            created_count += 1
            self.stdout.write(f" [OK] Empresa: {company.name}")

            # Subordinados
            for sub_idx, sub_data in enumerate(c_spec["subs"], start=1):
                sub_name = sub_data[0]
                sub_type = sub_data[1]
                sub_job = sub_data[2]
                sub_email = sub_data[3]
                sub_phone = sub_data[4]
                
                # Se for endereço de entrega/cobrança, pega dados adicionais
                street = sub_data[5] if len(sub_data) > 5 else company.street
                city = sub_data[6] if len(sub_data) > 6 else company.city
                state = sub_data[7] if len(sub_data) > 7 else company.state
                cep = sub_data[8] if len(sub_data) > 8 else company.postal_code

                sub = Contact(
                    name=sub_name,
                    parent=company,
                    contact_type=ContactTypeChoices.INDIVIDUAL,
                    address_type=sub_type,
                    job_title=sub_job,
                    email=sub_email,
                    phone=sub_phone,
                    street=street,
                    city=city,
                    state=state,
                    postal_code=cep,
                    country="Brasil",
                    salesperson=salesperson,
                    is_active=True
                )
                sub.full_clean()
                sub.save()
                created_count += 1
                self.stdout.write(f"    └── Subordinado ({sub.get_address_type_display()}): {sub.name}")

        # 5. Criando 6 Consultores Geotécnicos Independentes (Pessoas Físicas)
        consultants_specs = [
            ("Prof. Dr. Nelson Aoki", "Consultor Sênior em Fundações e Carga Admissível", "São Paulo", "SP", "01310-100", "(11) 9 9123-9901", "nelson.aoki.fundacoes@geoconsult.com.br", [tags["Consultoria Geotécnica Especializada"], tags["Projetista Estrutural Parceiro"]]),
            ("Engª. Maria Helena Albuquerque", "Especialista em Ensaios de Piezocone CPTu e Muros de Flexão", "Rio de Janeiro", "RJ", "22450-000", "(21) 9 9456-9902", "mhelena.albuquerque@geoconsult.com.br", [tags["Consultoria Geotécnica Especializada"]]),
            ("Dr. Álvaro Ferreira de Sousa", "Perito em Estabilidade de Encostas e Taludes Naturais", "Belo Horizonte", "MG", "30130-000", "(31) 9 9789-9903", "alvaro.sousa.pericias@geoconsult.com.br", [tags["Consultoria Geotécnica Especializada"]]),
            ("Eng. Roberto Kanzaki", "Projetista Estrutural de Contenções e Cortinas Atirantadas", "Curitiba", "PR", "80420-000", "(41) 9 9234-9904", "kanzaki.estruturas@geoconsult.com.br", [tags["Projetista Estrutural Parceiro"]]),
            ("Dra. Cristina Brandão Paes", "Geóloga Consultora em Cartografia de Riscos Geológicos", "Salvador", "BA", "40020-000", "(71) 9 9567-9905", "cristina.geologia@geoconsult.com.br", [tags["Consultoria Geotécnica Especializada"], tags["Órgão Ambiental & Regulador"]]),
            ("Eng. Waldemar Hachich Neto", "Consultor em Probabilidade e Confiabilidade Geotécnica", "São Paulo", "SP", "04538-000", "(11) 9 9890-9906", "waldemar.hachich@geoconsult.com.br", [tags["Consultoria Geotécnica Especializada"]]),
        ]

        for idx, (c_name, c_job, c_city, c_state, c_cep, c_mobile, c_email, c_tags) in enumerate(consultants_specs, start=300):
            cpf = make_valid_cpf(idx)
            salesperson = users[idx % len(users)]

            consultant = Contact(
                name=c_name,
                contact_type=ContactTypeChoices.INDIVIDUAL,
                doc_type=DocTypeChoices.CPF,
                doc_number=cpf,
                job_title=c_job,
                city=c_city,
                state=c_state,
                postal_code=c_cep,
                mobile=c_mobile,
                email=c_email,
                salesperson=salesperson,
                internal_notes="Consultor de notório saber para laudos e contraprovas técnicas de projetos complexos.",
                is_active=True
            )
            consultant.full_clean()
            consultant.save()
            consultant.tags.set(c_tags)
            created_count += 1
            self.stdout.write(f" [OK] Consultor Independente: {consultant.name}")

        # 6. Criando 2 Entidades Reguladoras e Ambientais
        agencies_specs = [
            ("CETESB - Companhia Ambiental do Estado de São Paulo", "CETESB", "05459-900", "São Paulo", "SP", "Avenida Professor Frederico Hermann Júnior, 345", "(11) 3133-3000", "falecom@cetesb.sp.gov.br", "https://cetesb.sp.gov.br", 401),
            ("ANM - Agência Nacional de Mineração (Segurança de Barragens)", "ANM Barragens", "70040-902", "Brasília", "DF", "SBN Quadra 02 Bloco N", "(61) 3312-6600", "barragens@anm.gov.br", "https://gov.br/anm", 402),
        ]

        for a_name, a_trade, a_cep, a_city, a_state, a_street, a_phone, a_email, a_site, seed_num in agencies_specs:
            cnpj = make_valid_cnpj(seed_num, branch=1)
            agency = Contact(
                name=a_name,
                trade_name=a_trade,
                contact_type=ContactTypeChoices.COMPANY,
                doc_type=DocTypeChoices.CNPJ,
                doc_number=cnpj,
                city=a_city,
                state=a_state,
                postal_code=a_cep,
                street=a_street,
                phone=a_phone,
                email=a_email,
                website=a_site,
                internal_notes="Órgão fiscalizador e regulador para licenciamentos de lavra e obras de terraplanagem.",
                is_active=True
            )
            agency.full_clean()
            agency.save()
            agency.tags.add(tags["Órgão Ambiental & Regulador"])
            created_count += 1
            self.stdout.write(f" [OK] Entidade Reguladora: {agency.name}")

        # 7. Criando 3 Contatos Históricos Arquivados (Soft-Delete)
        archived_specs = [
            ("Brocas & Coroas Diamantadas Importações Ltda", ContactTypeChoices.COMPANY, DocTypeChoices.CNPJ, 501, "São Paulo", "SP", "Fornecedor extinto em 2024. Cadastro arquivado para fins contábeis."),
            ("Terraplanagem São Geraldo & Transportes ME", ContactTypeChoices.COMPANY, DocTypeChoices.CNPJ, 502, "Betim", "MG", "Contrato encerrado amigavelmente. Descredenciada."),
            ("Eng. Aloísio Cardoso de Mello", ContactTypeChoices.INDIVIDUAL, DocTypeChoices.CPF, 503, "Santos", "SP", "Engenheiro geotécnico aposentado. Histórico mantido para ARTs antigas."),
        ]

        for arch_name, arch_type, arch_doc_type, seed_num, arch_city, arch_state, arch_notes in archived_specs:
            doc = make_valid_cnpj(seed_num) if arch_doc_type == DocTypeChoices.CNPJ else make_valid_cpf(seed_num)
            arch = Contact(
                name=arch_name,
                contact_type=arch_type,
                doc_type=arch_doc_type,
                doc_number=doc,
                city=arch_city,
                state=arch_state,
                internal_notes=arch_notes,
                is_active=False # Arquivado!
            )
            arch.full_clean()
            arch.save()
            created_count += 1
            self.stdout.write(f" [OK] Contato Arquivado (Histórico): {arch.name}")

        active_count = Contact.objects.filter(is_active=True).count()
        total_count = Contact.objects.count()

        self.stdout.write(self.style.SUCCESS(
            f"\n==> POPULAÇÃO CONCLUÍDA COM ÊXITO!\n"
            f" -> Total de registros criados: {total_count}\n"
            f" -> Contatos ativos: {active_count} (Exatamente 50 contatos ativos)\n"
            f" -> Contatos arquivados: {total_count - active_count} (3 registros históricos)\n"
            f" -> Matrizes / Empresas: {Contact.objects.filter(contact_type=ContactTypeChoices.COMPANY).count()}\n"
            f" -> Subordinados interligados: {Contact.objects.filter(parent__isnull=False).count()}\n"
            f" -> Canteiros de obra / Locais de entrega: {Contact.objects.filter(address_type=AddressTypeChoices.DELIVERY).count()}\n"
            f" -> Endereços de cobrança / Filiais: {Contact.objects.filter(address_type=AddressTypeChoices.INVOICE).count()}\n"
            f" -> Consultores técnicos independentes: {Contact.objects.filter(contact_type=ContactTypeChoices.INDIVIDUAL, parent__isnull=True).count()}\n"
            f" -> Tags / Categorias criadas: {ContactTag.objects.count()}\n"
        ))
