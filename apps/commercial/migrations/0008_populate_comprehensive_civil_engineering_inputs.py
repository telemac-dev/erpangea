from django.db import migrations

def populate_comprehensive_inputs(apps, schema_editor):
    TechnicalInputType = apps.get_model('commercial', 'TechnicalInputType')
    ProposalInputRequirement = apps.get_model('commercial', 'ProposalInputRequirement')

    # Remove registros de testes sem nome válido
    TechnicalInputType.objects.filter(name__in=["Insumo Técnico", ""]).delete()

    inputs_catalog = [
        # =========================================================================
        # 1. INSUMOS TÉCNICOS DE ENGENHARIA CIVIL E GEOTÉCNICA (16 INSUMOS)
        # =========================================================================
        {
            "category": "TECNICO",
            "name": "Laudo de Sondagem a Percussão SPT (ABNT NBR 6484)",
            "code": "TEC-GEO-01",
            "desc": "Laudo completo de sondagem a percussão SPT conforme ABNT NBR 6484 com no mínimo 3 furos, indicação de N-SPT metro a metro, cotas de amostragem georreferenciadas e posição do lençol freático (NA).",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Laudo de Sondagem Rotativa / Mista em Maciço Rochoso (ABNT NBR 6484)",
            "code": "TEC-GEO-02",
            "desc": "Relatório de sondagem rotativa com recuperação de testemunhos, determinação de índices RQD (Rock Quality Designation), grau de alteração, coerência e atitude das descontinuidades/fraturas.",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Ensaio de Piezocone / CPTu em Solos Moles (ABNT NBR 12069)",
            "code": "TEC-GEO-03",
            "desc": "Ensaio de cone elétrico com medição contínua de resistência de ponta (qc), atrito lateral (fs), poropressão dinâmica (u2) e ensaios de dissipação para determinação de coeficientes de adensamento.",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Ensaios Geotécnicos de Laboratório (Cisalhamento Direto e Triaxial)",
            "code": "TEC-GEO-04",
            "desc": "Laudos de ensaios de caracterização completa (granulometria, limites de Atterberg), ensaio de cisalhamento direto ou triaxial (CD/CU/UU) com determinação de coesão efetiva (c') e ângulo de atrito (φ').",
            "mandatory": False
        },
        {
            "category": "TECNICO",
            "name": "Ensaio de Permeabilidade in situ de Solo e Rocha (Lefranc e Lugeon)",
            "code": "TEC-GEO-05",
            "desc": "Determinação dos coeficientes de permeabilidade horizontal e vertical (k) para subsidiar projetos de rebaixamento de lençol freático, drenagem profunda (DHP) e vazões de infiltração.",
            "mandatory": False
        },
        {
            "category": "TECNICO",
            "name": "Ensaio de Prova de Carga Estática sobre Placa ou Estaca (NBR 6489 / NBR 12131)",
            "code": "TEC-GEO-06",
            "desc": "Relatório executivo de prova de carga estática com curva carga x recalque, determinação de carga de ruptura geotécnica e módulos de reação do subleito/maciço terroso.",
            "mandatory": False
        },
        {
            "category": "TECNICO",
            "name": "Planta de Cargas Estruturais com Esforços Axiais e Momentos Fletores",
            "code": "TEC-ESTR-01",
            "desc": "Planta de locação de cargas com memorial estrutural detalhando esforços axiais característicos (Nk), forças horizontais (Hx, Hy) e momentos fletores (Mx, My) em cada pilar ou parede de concreto.",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Projeto Arquitetônico Executivo Aprovado Completo (DWG/BIM)",
            "code": "TEC-ARQ-01",
            "desc": "Jogo completo de plantas baixas, cortes longitudinais e transversais, elevações/fachadas e implantação verticalizada em formato digital DWG editável e modelo IFC (BIM).",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Projeto Estrutural de Concreto Armado / Metálica da Superestrutura (DWG/BIM)",
            "code": "TEC-ESTR-02",
            "desc": "Plantas de formas de transição, locação de pilares, dimensões de vigas e lajes, especificações de fck do concreto e tensões de escoamento do aço estrutural em formato editável DWG.",
            "mandatory": False
        },
        {
            "category": "TECNICO",
            "name": "Levantamento Planialtimétrico Cadastral Georreferenciado (DWG)",
            "code": "TEC-TOPO-01",
            "desc": "Levantamento topográfico em coordenadas UTM (SIRGAS 2000) com curvas de nível de metro em metro, cotas de soleiras, postes, bueiros, árvores protegidas e amarração de confrontantes.",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Projeto de Terraplenagem e Geometria de Cortes e Aterros (DWG)",
            "code": "TEC-TERRA-01",
            "desc": "Plantas de terraplenagem com seções transversais tipo, curvas de compensação volumétrica (corte/aterro), cotas finais de greide, bermas de equilíbrio e taludes projetados.",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Estudo Hidrológico e Mancha de Inundação da Bacia Hidrográfica",
            "code": "TEC-HIDRO-01",
            "desc": "Estudo hidrológico de macrodrenagem com determinação de vazões de pico para tempos de recorrência (TR) de 25, 50 e 100 anos, delimitação de áreas de preservação permanente (APP) e cotas de cheia histórica.",
            "mandatory": False
        },
        {
            "category": "TECNICO",
            "name": "Cadastro de Redes de Utilidades Públicas Enterradas (Água, Esgoto, Gás, Energia)",
            "code": "TEC-UTIL-01",
            "desc": "Plantas cadastrais emitidas pelas concessionárias de serviços públicos indicando interferências de adutoras, redes de esgoto, gasodutos, cabos ópticos subterrâneos e faixas de servidão.",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Levantamento Batimétrico de Margens e Cursos D'água",
            "code": "TEC-BATI-01",
            "desc": "Levantamento batimétrico multifeixe com malha tridimensional de profundidades de leito de rio ou igarapé para subsidiar projetos de atracadouros, pontes, cais e contenções marginais.",
            "mandatory": False
        },
        {
            "category": "TECNICO",
            "name": "Laudo de Vistoria Cautelar de Vizinhança Prévia (ABNT NBR 12722)",
            "code": "TEC-VIZ-01",
            "desc": "Laudo pericial prévio de constatação de anomalias nos imóveis vizinhos antes do início das escavações e fundações conforme ABNT NBR 12722 e diretrizes do IBAPE com registro fotográfico.",
            "mandatory": True
        },
        {
            "category": "TECNICO",
            "name": "Relatório de Monitoramento e Instrumentação Geotécnica Existente",
            "code": "TEC-INST-01",
            "desc": "Histórico de leituras e calibrações de piezômetros, inclinômetros, marcos superficiais de recalque ou medidores de nível d'água instalados na área do empreendimento.",
            "mandatory": False
        },

        # =========================================================================
        # 2. INSUMOS ADMINISTRATIVOS, CARTORÁRIOS E DE LICENCIAMENTO (13 INSUMOS)
        # =========================================================================
        {
            "category": "ADMINISTRATIVO",
            "name": "Certidão de Registro de Imóveis / Matrícula Atualizada do Terreno",
            "code": "ADM-MATR-01",
            "desc": "Certidão de inteiro teor da matrícula imobiliária com certidão de ônus reais e ações reais/reipersecutórias, expedida pelo Cartório de Registro de Imóveis competente há no máximo 30 dias.",
            "mandatory": True
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Escritura Pública de Compra e Venda ou Contrato de Cessão de Direitos",
            "code": "ADM-ESCR-01",
            "desc": "Título translativo de propriedade devidamente averbado ou instrumento público/particular de compromisso de compra e venda conferindo legitimidade de posse para intervenção física na área.",
            "mandatory": False
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Certidão Negativa de Débitos Municipais e Carnê de IPTU do Terreno",
            "code": "ADM-IPTU-01",
            "desc": "Cópia da folha de rosto do carnê de IPTU do exercício vigente contendo número da inscrição imobiliária municipal, cadastro fiscal e certidão negativa de tributos municipais.",
            "mandatory": False
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Contrato Social Consolidado / Estatuto Social Vigente e Última Alteração",
            "code": "ADM-CONTR-01",
            "desc": "Cópia autenticada do Contrato Social consolidado ou Estatuto Social vigente acompanhado da ata de eleição da diretoria, devidamente registrados na Junta Comercial competente (JUCEA).",
            "mandatory": True
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Documentos de Identificação Oficial dos Representantes Legais (RG / CNH e CPF)",
            "code": "ADM-DOCS-01",
            "desc": "Cópia digitalizada em alta resolução do documento de identidade oficial com foto (RG ou CNH) e comprovante de inscrição no CPF dos sócios administradores ou diretores signatários.",
            "mandatory": True
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Procuração Pública para Representação Técnica e Contratual",
            "code": "ADM-PROC-01",
            "desc": "Instrumento público de mandato com poderes específicos conferidos para firmar contratos de prestação de serviços de engenharia, responder perante o CREA-AM e prefeituras.",
            "mandatory": False
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Comprovante de Inscrição e Situação Cadastral no CNPJ (Receita Federal)",
            "code": "ADM-CNPJ-01",
            "desc": "Comprovante de inscrição cadastral na Receita Federal do Brasil (RFB) da contratante ou da Sociedade de Propósito Específico (SPE) emitido nos últimos 30 dias com situação ATIVA.",
            "mandatory": True
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Alvará de Construção / Licença Municipal de Obras e Instalação",
            "code": "ADM-ALVAR-01",
            "desc": "Alvará de licença de obra emitido pela Prefeitura Municipal / Instituto Municipal de Planejamento Urbano (ex: IMPLUR) autorizando a execução das obras e intervenções.",
            "mandatory": False
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Licença Ambiental Prévia (LP) ou de Instalação (LI)",
            "code": "ADM-LIC-01",
            "desc": "Licença expedida pelo órgão ambiental competente (IPAAM / SEMMAS) com o termo de condicionantes ambientais aplicáveis ao desmatamento, movimentação de terra e drenagem.",
            "mandatory": False
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Outorga de Direito de Uso de Recursos Hídricos / Barramento / Canalização",
            "code": "ADM-OUTOR-01",
            "desc": "Portaria de outorga preventiva ou definitiva emitida pela Agência Nacional de Águas (ANA) ou órgão estadual de recursos hídricos para intervenções em calhas fluviais e nascentes.",
            "mandatory": False
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Certidão de Diretrizes Urbanísticas e Viárias / Termo de Compromisso",
            "code": "ADM-DIR-01",
            "desc": "Diretrizes urbanísticas emitidas pelo órgão viário municipal (ex: IMMU) para dimensionamento de acessos de veículos pesados, faixas de aceleração/desaceleração e recuos obrigatórios.",
            "mandatory": False
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Comprovante de Endereço Comercial Atualizado da Sede da Contratante",
            "code": "ADM-END-01",
            "desc": "Comprovante de endereço emitido nos últimos 60 dias (energia elétrica, água ou telecomunicações) da sede da contratante para fins de emissão de notas fiscais e faturamento.",
            "mandatory": False
        },
        {
            "category": "ADMINISTRATIVO",
            "name": "Ficha Cadastral e Dados para Faturamento / Envio de Notas Fiscais Eletrônicas",
            "code": "ADM-FAT-01",
            "desc": "Formulário cadastral preenchido com dados do departamento financeiro/fiscal, e-mail para envio de XML e DANFE, regime de tributação (Lucro Real/Presumido/Simples) e inscrições municipais.",
            "mandatory": True
        }
    ]

    for item in inputs_catalog:
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
        if not created:
            obj.category = item["category"]
            obj.code = item["code"]
            obj.default_description = item["desc"]
            obj.is_mandatory_default = item["mandatory"]
            obj.is_active = True
            obj.save()

def reverse_inputs(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('commercial', '0007_populate_administrative_and_technical_inputs'),
    ]

    operations = [
        migrations.RunPython(populate_comprehensive_inputs, reverse_inputs),
    ]
