from django.db import migrations

def populate_inputs(apps, schema_editor):
    TechnicalInputType = apps.get_model('commercial', 'TechnicalInputType')

    inputs = [
        # Insumos Técnicos
        {
            "category": "TECNICO",
            "name": "Furos de Sondagem SPT segundo a NBR 6484",
            "code": "INP-SPT-01",
            "desc": "Laudo completo de sondagem a percussão SPT conforme NBR 6484 com no mínimo 3 furos, indicação de N-SPT metro a metro e cota do lençol freático.",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Planta de Cargas com Esforços Axiais, Horizontais e Momentos",
            "code": "INP-CARG-01",
            "desc": "Planta de locação de cargas com memorial estrutural detalhando esforços axiais característicos (Nk), horizontais (Hx, Hy) e momentos fletores nas bases dos pilares.",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Projetos Arquitetônicos e Implantação em formato DWG",
            "code": "INP-ARQ-01",
            "desc": "Projeto arquitetônico executivo aprovado, incluindo plantas baixas, cortes, fachadas e implantação com coordenadas georreferenciadas em formato DWG editável.",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Levantamento Planialtimétrico Cadastral (DWG)",
            "code": "INP-TOPO-01",
            "desc": "Levantamento topográfico planialtimétrico cadastral em malha de coordenadas UTM com curvas de nível de metro em metro, indicação de confrontantes e árvores protegidas.",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Projeto Estrutural de Concreto ou Estrutura Metálica (DWG)",
            "code": "INP-ESTR-01",
            "desc": "Plantas de formas e armações da superestrutura, detalhes de vigas de transição e especificações de fck do concreto e aço CA-50 em formato DWG.",
            "mandatory": False
        },
        {
            "category": "TECNICO",
            "name": "Laudo de Vistoria Cautelar de Vizinhança Prévia",
            "code": "INP-VIZ-01",
            "desc": "Laudo pericial prévio de constatação de anomalias nos imóveis vizinhos antes do início das escavações e fundações conforme ABNT NBR 12722.",
            "mandatory": False
        },
        # Insumos Administrativos
        {
            "category": "ADMINISTRATIVO",
            "name": "Certidão de Registro de Imóveis / Matrícula Atualizada do Terreno",
            "code": "ADM-MATR-01",
            "desc": "Certidão de inteiro teor da matrícula imobiliária atualizada (validade máxima de 30 dias) expedida pelo Cartório de Registro de Imóveis competente.",
            "mandatory": True
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Contrato Social / Estatuto Vigente e Documentos dos Representantes",
            "code": "ADM-CONTR-01",
            "desc": "Cópia autenticada do Contrato Social consolidado ou Estatuto da empresa e documentos de identificação oficial com foto dos representantes legais.",
            "mandatory": True
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Alvará de Construção / Licença Ambiental de Instalação (LI)",
            "code": "ADM-LIC-01",
            "desc": "Alvará de licença de obra emitido pela Prefeitura Municipal e Licença de Instalação (LI) emitida pelo órgão ambiental competente (IPAAM / SEMMAS).",
            "mandatory": False
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Comprovante de Inscrição Imobiliária / Carnê de IPTU do Imóvel",
            "code": "ADM-IPTU-01",
            "desc": "Cópia da folha de rosto do carnê de IPTU do exercício vigente contendo número da inscrição imobiliária municipal e dados cadastrais do lote.",
            "mandatory": False
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Procuração Pública para Representação Técnica",
            "code": "ADM-PROC-01",
            "desc": "Instrumento público de procuração conferindo poderes expressos ao responsável pela assinatura do contrato e trâmites perante o CREA-AM.",
            "mandatory": False
        }
    ]

    for item in inputs:
        obj, created = TechnicalInputType.objects.get_or_create(
            name=item["name"],
            defaults={
                "category": item["category"],
                "code": item["code"],
                "default_description": item["desc"],
                "is_mandatory_default": item["mandatory"],
                "is_active": True
            }
        )
        if not created and (obj.category != item["category"] or obj.default_description != item["desc"]):
            obj.category = item["category"]
            obj.code = item["code"]
            obj.default_description = item["desc"]
            obj.is_mandatory_default = item["mandatory"]
            obj.save()

def reverse_inputs(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('commercial', '0006_proposalinputrequirement_category_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_inputs, reverse_inputs),
    ]
