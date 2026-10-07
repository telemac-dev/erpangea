import uuid
from django.db import migrations

def seed_technical_catalog(apps, schema_editor):
    TechnicalDiscipline = apps.get_model('commercial', 'TechnicalDiscipline')
    TechnicalServiceType = apps.get_model('commercial', 'TechnicalServiceType')
    TechnicalInputType = apps.get_model('commercial', 'TechnicalInputType')
    ProposalScopeItem = apps.get_model('commercial', 'ProposalScopeItem')
    ProposalInputRequirement = apps.get_model('commercial', 'ProposalInputRequirement')

    # 1. Disciplinas
    disc_fundacoes, _ = TechnicalDiscipline.objects.get_or_create(
        name="Fundações e Geotecnia",
        defaults={"description": "Projetos de fundações superficiais e profundas, sapatas, estacas e blocos."}
    )
    disc_contencoes, _ = TechnicalDiscipline.objects.get_or_create(
        name="Contenções e Estruturas de Arrimo",
        defaults={"description": "Cortinas atirantadas, solo grampeado, muros de flexão e contenções de divisa."}
    )
    disc_taludes, _ = TechnicalDiscipline.objects.get_or_create(
        name="Estabilidade de Taludes e Encostas",
        defaults={"description": "Análises de equilíbrio limite, instrumentação e estabilização de encostas."}
    )
    disc_pericia, _ = TechnicalDiscipline.objects.get_or_create(
        name="Consultoria e Perícia Geotécnica",
        defaults={"description": "Laudos técnicos, perícias judiciais e assessoria em sinistros de engenharia."}
    )
    disc_obras_terra, _ = TechnicalDiscipline.objects.get_or_create(
        name="Obras de Terra e Drenagem",
        defaults={"description": "Aterros, escavações, rebaixamento de lençol e drenagem profunda."}
    )

    # 2. Tipos de Servico
    services_data = [
        {
            "name": "Dimensionamento de Fundações Superficiais e Profundas (NBR 6122 / NBR 6118)",
            "code": "FUND-01",
            "discipline": disc_fundacoes,
            "default_nbr_references": "ABNT NBR 6122:2019 e NBR 6118:2023",
            "default_description": "Projeto executivo completo de fundações em estacas tipo hélice contínua monitorada e blocos de coroamento em concreto armado."
        },
        {
            "name": "Análise de Estabilidade de Encostas e Taludes (NBR 11682)",
            "code": "TALU-01",
            "discipline": disc_taludes,
            "default_nbr_references": "ABNT NBR 11682:2009",
            "default_description": "Análise de estabilidade global de talude com cálculo de fatores de segurança pelos métodos de Bishop simplificado e Morgenstern-Price."
        },
        {
            "name": "Projetos Geotécnicos e Estruturais de Contenções de Divisa",
            "code": "CONT-01",
            "discipline": disc_contencoes,
            "default_nbr_references": "ABNT NBR 11682:2009 e NBR 6118:2023",
            "default_description": "Projeto executivo de contenção em cortina de solo grampeado com concreto projetado e drenagem profunda subsuperficial."
        },
        {
            "name": "Consultoria Geotécnica e Laudos Periciais em Obra",
            "code": "CONS-01",
            "discipline": disc_pericia,
            "default_nbr_references": "ABNT NBR 11682 e Manual de Segurança de Barragens",
            "default_description": "Vistoria técnica pericial in loco com análise de instrumentação piezométrica e emissão de laudo técnico conclusivo com ART."
        },
        {
            "name": "Projeto de Cortinas de Solo Grampeado e Concreto Projetado",
            "code": "CONT-02",
            "discipline": disc_contencoes,
            "default_nbr_references": "ABNT NBR 11682:2009",
            "default_description": "Dimensionamento geotécnico e estrutural de malha de grampos autoperfurantes e paramento em concreto projetado reforçado com tela soldada."
        },
        {
            "name": "Projeto Executivo de Drenagem Profunda e Subsuperficial",
            "code": "DREN-01",
            "discipline": disc_obras_terra,
            "default_nbr_references": "ABNT NBR 11682:2009",
            "default_description": "Dimensionamento de drenos sub-horizontais profundos (DHP), canaletas de crista e trincheiras drenantes."
        }
    ]

    for s_data in services_data:
        TechnicalServiceType.objects.get_or_create(
            name=s_data["name"],
            defaults={
                "code": s_data["code"],
                "discipline": s_data["discipline"],
                "default_nbr_references": s_data["default_nbr_references"],
                "default_description": s_data["default_description"],
                "is_active": True
            }
        )

    # 3. Tipos de Insumo
    inputs_data = [
        {
            "name": "Furos de Sondagem SPT segundo a NBR 6484",
            "code": "SPT-01",
            "default_description": "Laudo de Sondagem a Percussão SPT conforme ABNT NBR 6484 com no mínimo 3 furos e indicação de N-SPT.",
            "is_mandatory_default": True
        },
        {
            "name": "Planta de Cargas com Esforços Axiais, Horizontais e Momentos",
            "code": "CARGAS-01",
            "default_description": "Planta de Cargas com memorial estrutural detalhando esforços axiais (Nk), horizontais (Hx, Hy) e momentos fletores.",
            "is_mandatory_default": True
        },
        {
            "name": "Projetos Arquitetônicos e Implantação em formato DWG",
            "code": "ARQ-01",
            "default_description": "Projeto Arquitetônico completo e Implantação Verticalizada em formato editável DWG.",
            "is_mandatory_default": True
        },
        {
            "name": "Levantamento Planialtimétrico Cadastral (DWG)",
            "code": "TOPO-01",
            "default_description": "Levantamento topográfico planialtimétrico cadastral com curvas de nível de metro em metro e amarração georreferenciada.",
            "is_mandatory_default": True
        },
        {
            "name": "Projeto Estrutural de Concreto ou Estrutura Metálica (DWG)",
            "code": "ESTRUT-01",
            "default_description": "Projeto estrutural com locação e dimensões de pilares, paredes e vigas de transição.",
            "is_mandatory_default": False
        },
        {
            "name": "Outro Documento / Insumo Técnico",
            "code": "OUTRO-01",
            "default_description": "Fornecimento obrigatório pela contratante conforme normas técnicas.",
            "is_mandatory_default": False
        }
    ]

    for inp_data in inputs_data:
        TechnicalInputType.objects.get_or_create(
            name=inp_data["name"],
            defaults={
                "code": inp_data["code"],
                "default_description": inp_data["default_description"],
                "is_mandatory_default": inp_data["is_mandatory_default"],
                "is_active": True
            }
        )

    # 4. Vincular registros existentes de ProposalScopeItem e ProposalInputRequirement
    choice_service_map = {
        'FUNDACOES': 'Dimensionamento de Fundações Superficiais e Profundas (NBR 6122 / NBR 6118)',
        'ESTABILIDADE_TALUDES': 'Análise de Estabilidade de Encostas e Taludes (NBR 11682)',
        'CONTENCOES': 'Projetos Geotécnicos e Estruturais de Contenções de Divisa',
        'CONSULTORIA_PERICIA': 'Consultoria Geotécnica e Laudos Periciais em Obra'
    }

    for item in ProposalScopeItem.objects.all():
        full_name = choice_service_map.get(item.service_type, item.service_type)
        service_obj = TechnicalServiceType.objects.filter(name=full_name).first()
        if service_obj:
            item.service_type_ref = service_obj
            item.discipline = service_obj.discipline
            item.service_type = service_obj.name
            item.save()

    choice_input_map = {
        'SONDAGEM_SPT': 'Furos de Sondagem SPT segundo a NBR 6484',
        'PLANTA_CARGAS': 'Planta de Cargas com Esforços Axiais, Horizontais e Momentos',
        'ARQUITETURA_DWG': 'Projetos Arquitetônicos e Implantação em formato DWG',
        'LEVANTAMENTO_TOPOGRAFICO': 'Levantamento Planialtimétrico Cadastral (DWG)',
        'PROJETO_ESTRUTURAL_DWG': 'Projeto Estrutural de Concreto ou Estrutura Metálica (DWG)',
        'OUTRO': 'Outro Documento / Insumo Técnico'
    }

    for inp in ProposalInputRequirement.objects.all():
        full_name = choice_input_map.get(inp.required_item_type, inp.required_item_type)
        inp_obj = TechnicalInputType.objects.filter(name=full_name).first()
        if inp_obj:
            inp.input_type_ref = inp_obj
            inp.required_item_type = inp_obj.name
            inp.save()


def reverse_seed(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('commercial', '0002_technicaldiscipline_technicalinputtype_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_technical_catalog, reverse_seed),
    ]
