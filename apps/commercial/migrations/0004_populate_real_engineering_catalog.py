from django.db import migrations

def populate_real_engineering_catalog(apps, schema_editor):
    TechnicalDiscipline = apps.get_model('commercial', 'TechnicalDiscipline')
    TechnicalServiceType = apps.get_model('commercial', 'TechnicalServiceType')
    ProposalScopeItem = apps.get_model('commercial', 'ProposalScopeItem')

    # 1. Desvincular com segurança itens existentes de escopo para permitir a deleção limpa
    ProposalScopeItem.objects.all().update(service_type_ref=None, discipline=None)

    # 2. Remover todos os registros existentes de Serviços Técnicos e Disciplinas
    TechnicalServiceType.objects.all().delete()
    TechnicalDiscipline.objects.all().delete()

    # 3. Catálogo Real de Engenharia Civil para Escritório de Projetos e Consultoria
    catalog = [
        {
            "discipline": "Geotecnia e Fundações",
            "description": "Projetos geotécnicos e dimensionamento de fundações diretas e profundas, caracterização estratigráfica e ensaios geotécnicos.",
            "services": [
                {
                    "name": "Dimensionamento de Fundações Profundas em Estacas (Hélice, Cravadas e Escavadas)",
                    "code": "GEO-FUND-01",
                    "nbr": "ABNT NBR 6122:2019 e NBR 6118:2023",
                    "desc": "Dimensionamento geotécnico e estrutural completo de fundações profundas em estacas com verificação de capacidade de carga (Aoki-Velloso e Décourt-Quaresma), previsão de recalques e detalhamento de blocos de coroamento em concreto armado."
                },
                {
                    "name": "Dimensionamento de Fundações Superficiais (Sapatas Isoladas, Corridas e Radiers)",
                    "code": "GEO-FUND-02",
                    "nbr": "ABNT NBR 6122:2019 e NBR 6118:2023",
                    "desc": "Projeto executivo de fundações diretas (sapatas e radiers nervurados), com determinação da tensão admissível de solos, verificação à punção, tombamento e armaduras de flexão."
                },
                {
                    "name": "Interpretação e Análise Geotécnica de Ensaios de Campo e Laboratório (SPT, CPTu e Palheta)",
                    "code": "GEO-LAB-01",
                    "nbr": "ABNT NBR 6484:2020 e NBR 12069",
                    "desc": "Elaboração de perfil geotécnico estratigráfico tridimensional com determinação de parâmetros de deformabilidade (E, ν) e resistência ao cisalhamento (c', φ'), N-SPT médio corrigido e cota d'água freática."
                }
            ]
        },
        {
            "discipline": "Contenções de Encostas e Estruturas de Arrimo",
            "description": "Projetos estruturais e geotécnicos de estruturas de contenção de divisa, cortinas atirantadas, solo grampeado e muros de arrimo.",
            "services": [
                {
                    "name": "Projeto Executivo de Contenção em Cortina de Solo Grampeado com Concreto Projetado",
                    "code": "CONT-GRAMP-01",
                    "nbr": "ABNT NBR 11682:2009 e NBR 6118:2023",
                    "desc": "Dimensionamento geotécnico da malha de chumbadores/grampos de aço CA-50, injeção de calda de cimento em bancadas sucessivas, paramento em concreto projetado reforçado com tela soldada e sistema de drenagem profunda (DHP) e barbacas."
                },
                {
                    "name": "Projeto de Cortina Atirantada e Muros de Diafragma com Tirantes Provisórios e Definitivos",
                    "code": "CONT-ATIR-01",
                    "nbr": "ABNT NBR 11682:2009 e NBR 5629:2018",
                    "desc": "Dimensionamento estrutural de cortina de contenção em concreto armado com ancoragens protendidas no maciço, cálculo de comprimento livre e ancorado do bulbo e plano de ensaios de qualificação e protensão."
                },
                {
                    "name": "Dimensionamento de Muros de Arrimo em Concreto Armado (Muros de Flexão e Gravidade)",
                    "code": "CONT-MURO-01",
                    "nbr": "ABNT NBR 11682:2009 e NBR 6118:2023",
                    "desc": "Projeto executivo de muros de contenção com verificação aos estados limites últimos de tombamento, deslizamento pela base, capacidade de carga da fundação e estabilidade global da encosta."
                },
                {
                    "name": "Dimensionamento de Muros em Gabiões e Terramesh com Geogrelhas Poliméricas",
                    "code": "CONT-GABI-01",
                    "nbr": "ABNT NBR 11682:2009 e NBR 10597",
                    "desc": "Projeto de contenção por gravidade e solo reforçado com caixas de gabião tipo caixa e colchão reno em malha hexagonal de arame galvanizado e reforço do aterro com geossintéticos de alta tenacidade."
                }
            ]
        },
        {
            "discipline": "Estabilidade de Taludes e Obras de Terra",
            "description": "Estudos de estabilização de encostas, análise de equilíbrio limite, terraplenagem e aterros sobre solos compressíveis.",
            "services": [
                {
                    "name": "Análise de Estabilidade Global de Encostas Naturais e Taludes de Corte e Aterro",
                    "code": "TALU-ESTAB-01",
                    "nbr": "ABNT NBR 11682:2009",
                    "desc": "Modelagem computacional bidimensional e tridimensional com determinação de fatores de segurança pelos métodos de equilíbrio limite (Bishop Simplificado, Spencer e Morgenstern-Price) para condições drenadas e não-drenadas."
                },
                {
                    "name": "Projeto Geotécnico de Terraplenagem, Bota-Fora e Compensação de Volumes (Corte/Aterro)",
                    "code": "TERRA-COMP-01",
                    "nbr": "ABNT NBR 11682:2009 e NBR 7182",
                    "desc": "Plano de terraplenagem com cálculo de seções transversais, notas de serviço, curvas de compensação volumétrica (Brückner), bermas de equilíbrio e especificações de compactação de aterros (Proctor Normal/Modificado)."
                },
                {
                    "name": "Projeto de Aterros sobre Solos Moles com Geodrenos e Bermas de Equilíbrio",
                    "code": "TERRA-MOLE-01",
                    "nbr": "ABNT NBR 11682:2009 e NBR 6122:2019",
                    "desc": "Modelagem de adensamento unidimensional de camadas argilosas moles com drenos verticais pré-fabricados (DVP), aterro de sobrecarga temporária e cálculo da taxa de recalques no tempo por Teoria de Terzaghi."
                }
            ]
        },
        {
            "discipline": "Estruturas de Concreto Armado e Protendido",
            "description": "Cálculo estrutural de superestruturas prediais residenciais e comerciais, lajes protendidas e estruturas especiais de concreto.",
            "services": [
                {
                    "name": "Projeto Estrutural de Edifícios Residenciais e Comerciais em Concreto Armado",
                    "code": "ESTR-CONC-01",
                    "nbr": "ABNT NBR 6118:2023 e NBR 8681:2003",
                    "desc": "Concepção e cálculo de superestrutura completa (pilares, vigas, lajes maciças e nervuradas), pórticos espaciais contravento, cálculo de efeitos de 2ª ordem global (parâmetro α e γz) e plantas executivas de armação e formas."
                },
                {
                    "name": "Projeto de Lajes Protendidas com Cordoalhas Engraxadas Não-Aderentes",
                    "code": "ESTR-PROT-01",
                    "nbr": "ABNT NBR 6118:2023",
                    "desc": "Dimensionamento e detalhamento de lajes planas e nervuradas protendidas, traçado dos cabos parabólicos, cálculo das perdas imediatas e diferidas de protensão e armaduras passivas de punção e cisalhamento."
                },
                {
                    "name": "Projeto Estrutural de Muros, Reservatórios e Piscinas Enterradas em Concreto Armado",
                    "code": "ESTR-RESERV-01",
                    "nbr": "ABNT NBR 6118:2023 e NBR 9575",
                    "desc": "Dimensionamento de reservatórios enterrados e elevados sujeitos a empuxos hidrostáticos e de terra combinados, com controle de fissuração reduzida (wmax ≤ 0,10 mm) para estanqueidade hídrica total."
                }
            ]
        },
        {
            "discipline": "Estruturas Metálicas e Mistas",
            "description": "Projetos de galpões industriais, coberturas espaciais, pontes rolantes, mezaninos e passarelas metálicas.",
            "services": [
                {
                    "name": "Projeto Estrutural de Galpões Industriais e Centros Logísticos em Aço",
                    "code": "ESTR-MET-01",
                    "nbr": "ABNT NBR 8800:2024 e NBR 6123:2023",
                    "desc": "Concepção de pórticos planos e espaciais com perfis soldados e laminados, cálculo de cargas dinâmicas de pontes rolantes, análise das forças de vento conforme NBR 6123 e detalhamento executivo de ligações parafusadas e soldadas."
                },
                {
                    "name": "Projeto de Mezaninos Metálicos e Estruturas de Cobertura Espacial",
                    "code": "ESTR-MET-02",
                    "nbr": "ABNT NBR 8800:2024 e NBR 14762",
                    "desc": "Dimensionamento de vigas e pilares metálicos com lajes tipo Steel Deck em perfis formados a frio, detalhamento de contraventamentos horizontais e verticais em cruzeta e chapas de base com chumbadores."
                }
            ]
        },
        {
            "discipline": "Drenagem Urbana e Hidrologia Aplicada",
            "description": "Estudos hidrológicos de bacias hidrográficas, microdrenagem, macrodrenagem, bacias de amortecimento e drenos profundos.",
            "services": [
                {
                    "name": "Estudo Hidrológico e Projeto Executivo de Microdrenagem Pluvial Urbana",
                    "code": "HIDRO-MICRO-01",
                    "nbr": "ABNT NBR 10844 e Manuais de Drenagem Urbana",
                    "desc": "Determinação de vazões de pico pelo Método Racional para tempos de recorrência (TR) de projeto, dimensionamento hidráulico de sarjetas, bocas de lobo, caixas de ligação, tubulações em PEAD/concreto e dissipadores de energia."
                },
                {
                    "name": "Projeto de Macrodrenagem, Canais Abertos e Bacias de Amortecimento de Cheias (Piscinões)",
                    "code": "HIDRO-MACRO-01",
                    "nbr": "Manuais Técnicos de Hidráulica e Drenagem Fluvial",
                    "desc": "Modelagem hidrodinâmica de canais de grande porte com verificação de linha de remanso e velocidade crítica, e dimensionamento de reservatórios de detenção/retenção de amortecimento de picos pluviométricos com descarregadores de fundo."
                },
                {
                    "name": "Projeto Executivo de Drenagem Superficial e Subsuperficial de Encostas e Rodovias",
                    "code": "HIDRO-SUB-01",
                    "nbr": "ABNT NBR 11682:2009 e Manuais DNIT",
                    "desc": "Projeto de canaletas de crista e pé de talude, descidas d'água em degraus de concreto, bacias de dissipação e drenos sub-horizontais profundos para despressurização do lençol freático em maciços terrosos."
                }
            ]
        },
        {
            "discipline": "Infraestrutura Viária e Pavimentação",
            "description": "Projetos geométricos de vias urbanas e loteamentos, dimensionamento estrutural de pavimentos flexíveis e rígidos.",
            "services": [
                {
                    "name": "Projeto Geométrico e de Sinalização Viária de Loteamentos e Vias Urbanas",
                    "code": "VIA-GEOM-01",
                    "nbr": "Normas e Manuais do CONTRAN e DNIT",
                    "desc": "Traçado geométrico em planta e perfil longitudinal com curvas circulares e de transição em espiral, cálculo de superelevações, distâncias de visibilidade de parada, seções transversais tipo e projeto de sinalização horizontal e vertical."
                },
                {
                    "name": "Dimensionamento Estrutural de Pavimentos Flexíveis (Asfálticos) e Rígidos (Concreto)",
                    "code": "VIA-PAV-01",
                    "nbr": "Manuais DNIT e ABNT NBR 7584",
                    "desc": "Determinação do Número N de solicitações por eixos padrão de tráfego (8,2 t), dimensionamento de camadas de subleito, sub-base de brita graduada tratada com cimento (BGTC) e capa de concreto asfáltico usinado a quente (CBUQ)."
                }
            ]
        },
        {
            "discipline": "Consultoria Técnica, Pareceres e Laudos Periciais",
            "description": "Consultoria geotécnica de campo, perícias judiciais e extrajudiciais, vistorias cautelares de vizinhança e monitoramento de instrumentação.",
            "services": [
                {
                    "name": "Consultoria Geotécnica Especializada e Parecer Técnico de Fundação e Obra de Terra",
                    "code": "CONS-PAREC-01",
                    "nbr": "ABNT NBR 6122:2019 e NBR 11682:2009",
                    "desc": "Acompanhamento técnico presencial com avaliação de riscos, análise de comportamento de fundações em fase de escavação, recomendação de ajustes executivos in loco e emissão de ART de assessoria técnica."
                },
                {
                    "name": "Laudo Pericial de Engenharia Civil e Diagnóstico de Patologias Estruturais e Geotécnicas",
                    "code": "CONS-LAUDO-01",
                    "nbr": "ABNT NBR 13752 (Perícias de Engenharia) e IBAPE",
                    "desc": "Vistoria pericial com levantamento fotográfico minucioso de recalques diferenciais, fissuras, trincas, flechas excessivas e recalques de encosta, ensaios não-destrutivos (esclerometria e ultrassom) e parecer conclusivo sobre causas e estabilidade."
                },
                {
                    "name": "Projeto e Acompanhamento de Instrumentação Geotécnica de Recalques e Nível D'água",
                    "code": "CONS-INST-01",
                    "nbr": "ABNT NBR 11682:2009 e NBR 6122:2019",
                    "desc": "Plano de instrumentação com piezômetros tipo Casagrande/corda vibrante, marcos superficiais de recalque, inclinômetros bi-axiais para monitoramento de deslocamentos horizontais e relatórios periódicos de comportamento com curvas de tendência."
                },
                {
                    "name": "Laudo de Vistoria Cautelar de Vizinhança para Obras Urbanas",
                    "code": "CONS-VIZ-01",
                    "nbr": "ABNT NBR 12722 e Diretrizes do IBAPE",
                    "desc": "Vistoria preventiva detalhada de todos os imóveis circunvizinhos ao empreendimento antes do início das escavações e fundações, catalogação de anomalias pré-existentes com registro fotográfico e termo assinado pelos proprietários."
                }
            ]
        },
        {
            "discipline": "Instalações Prediais e Especiais",
            "description": "Projetos de instalações hidrossanitárias prediais, reúso de água, instalações elétricas, subestações e proteção contra descargas atmosféricas.",
            "services": [
                {
                    "name": "Projeto de Instalações Hidráulicas, Sanitárias e Reúso de Águas Pluviais",
                    "code": "INST-HIDRO-01",
                    "nbr": "ABNT NBR 5626:2020 e NBR 8160:1999",
                    "desc": "Dimensionamento de rede de água fria e quente com cálculo de perdas de carga contínuas e localizadas, sistema separador absoluto de esgoto sanitário com ventilação primária/secundária e aproveitamento de águas de chuva para bacias e rega."
                },
                {
                    "name": "Projeto Elétrico de Baixa Tensão, Subestação Abrigada e SPDA (Pára-Raios)",
                    "code": "INST-ELET-01",
                    "nbr": "ABNT NBR 5410:2004 e NBR 5419:2015",
                    "desc": "Cálculo de demanda e balanceamento de circuitos de força e iluminação, dimensionamento de quadros gerais, condutores e disjuntores por capacidade de corrente e queda de tensão, e sistema de captação e malha de aterramento SPDA."
                }
            ]
        }
    ]

    for item_disc in catalog:
        disc_obj = TechnicalDiscipline.objects.create(
            name=item_disc["discipline"],
            description=item_disc["description"],
            is_active=True
        )
        for s_data in item_disc["services"]:
            TechnicalServiceType.objects.create(
                discipline=disc_obj,
                name=s_data["name"],
                code=s_data["code"],
                default_nbr_references=s_data["nbr"],
                default_description=s_data["desc"],
                is_active=True
            )

    # 4. Vincular itens de escopo existentes aos novos serviços criados
    for scope_item in ProposalScopeItem.objects.all():
        text_lower = (scope_item.service_type or "").lower()
        matched_service = None
        if "fundaç" in text_lower:
            matched_service = TechnicalServiceType.objects.filter(name__icontains="Fundações Profundas").first()
        elif "talude" in text_lower or "encosta" in text_lower:
            matched_service = TechnicalServiceType.objects.filter(name__icontains="Encostas Naturais").first()
        elif "contenç" in text_lower or "arrimo" in text_lower:
            matched_service = TechnicalServiceType.objects.filter(name__icontains="Solo Grampeado").first()
        elif "consultoria" in text_lower or "perícia" in text_lower:
            matched_service = TechnicalServiceType.objects.filter(name__icontains="Consultoria Geotécnica").first()
        elif "drenagem" in text_lower:
            matched_service = TechnicalServiceType.objects.filter(name__icontains="Drenagem Superficial").first()

        if not matched_service:
            matched_service = TechnicalServiceType.objects.first()

        if matched_service:
            scope_item.service_type_ref = matched_service
            scope_item.discipline = matched_service.discipline
            scope_item.service_type = matched_service.name
            scope_item.save(update_fields=['service_type_ref', 'discipline', 'service_type'])


def reverse_populate(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('commercial', '0003_seed_technical_catalog'),
    ]

    operations = [
        migrations.RunPython(populate_real_engineering_catalog, reverse_populate),
    ]
