# Documento de Especificação Funcional e Técnica: Módulo de Contatos

## Informações Gerais
- **Objetivo do Documento:** Fornecer o levantamento funcional e a especificação técnica detalhada do módulo de Contatos a partir da inspeção da instância de referência, estabelecendo diretrizes precisas para que a equipe de engenharia implemente um módulo equivalente no ERPangea sem necessidade de reanálise.
- **Sistema de Referência:** Odoo (Community/Enterprise Edition rodando com localização brasileira/LatAm).
- **Data da Análise:** 02 de Outubro de 2026.
- **Escopo da Análise:** Interface web do aplicativo Contatos (`/odoo/contacts`), abrangendo navegação, formulários de empresas e indivíduos, contatos subordinados, visualizações (Kanban, Lista, Atividade), filtros, agrupamentos, operações em lote (exportação, arquivamento, mesclagem) e importação.
- **Limitações:** A análise foi realizada estritamente em modo de observação/somente-leitura com o perfil de usuário disponibilizado, sem execução de mutações permanentes na base de dados. Parâmetros avançados de configuração global (ex.: edição direta de tabelas de alíquotas ou parametrização de servidores EDI) não estavam expostos para este perfil.

---

## Convenções de Rastreabilidade
Para total conformidade com as diretrizes de governança:
- **[Observado]:** Funcionalidade, campo, elemento visual ou regra confirmada diretamente na interface durante a inspeção.
- **[Inferido]:** Conclusão técnica ou arquitetural provável decorrente dos comportamentos e metadados inspecionados, sujeita a refinamento na arquitetura alvo.
- **[Não verificado]:** Recurso identificado na interface cuja execução completa alteraria registros de produção ou cujo acesso exigia privilégios de superadministrador.

---

## 1. Navegação e Telas

### 1.1 Barra de Navegação Superior (Navbar)
- **[Observado]** Seletor de aplicativos corporativos à esquerda (`apps menu`), disponibilizando atalhos para os módulos instalados no ecossistema (Contatos, Vendas, Faturamento, Mensagens, Painéis, Aplicativos).
- **[Observado]** Identificador de contexto da marca: rótulo clicável "Contatos" com retorno para a visualização padrão.
- **[Observado]** Menu de seção único intitulado "Contatos" apontando para a listagem geral (`res.partner`).
- **[Observado]** Painel direito com atalhos de produtividade:
  - Contador de atividades pendentes.
  - Contador de mensagens não lidas / comunicação interna.
  - Seletor de Empresa Ativa (*Multi-company switcher*).
  - Menu do usuário autenticado (preferências, perfil e encerramento de sessão).

### 1.2 Painel de Controle (Control Panel) e Barra de Ações
- **[Observado]** **Breadcrumbs (Migalhas de Pão):** Indicação hierárquica do caminho percorrido (ex.: `Contatos / Acme Corporation`). Ao clicar no segmento pai, retorna à listagem preservando filtros aplicados.
- **[Observado]** **Botão de Ação Primária ("Novo"):** Posicionado em destaque no canto superior esquerdo, dispara a criação de um novo registro em branco.
- **[Observado]** **Menu de Ações Globais ("Ações" - Ícone de Engrenagem):**
  - Quando nenhum registro está selecionado na lista: exibe a opção **"Importar registros"**.
  - Quando um ou mais registros estão marcados: transforma-se em menu de operações em lote (ver seção 3.2).
  - Quando visualizando um formulário individual: exibe operações de registro único (ver seção 3.3).
- **[Observado]** **Controle de Paginação (Pager):** Exibição no formato `1-39 / 39`, com botões direcionais "Anterior" e "Próximo" e suporte a saltos de página.
- **[Observado]** **Seletor de Visualizações (View Switcher):**
  1. **Kanban (`o_kanban`):** Visualização padrão em grade responsiva de cartões (cards).
  2. **Lista / Tabela (`o_list`):** Visualização tabular em grade com ordenação por colunas e caixas de seleção.
  3. **Atividade (`o_activity`):** Matriz de compromissos categorizada por tipo de atividade.

### 1.3 Modos de Visualização

#### Visualização Kanban
- **[Observado]** Disposição em cartões verticais dinâmicos em grade fluida.
- **[Observado]** Anatomia do Cartão (Card):
  - **Lado Esquerdo:** Foto ou logotipo principal (`avatar_128`).
  - **Sub-avatar:** Quando o contato é uma pessoa física subordinada a uma empresa, o logotipo da empresa-mãe é renderizado sobreposto no canto inferior direito do avatar do contato.
  - **Corpo do Cartão:**
    - Nome completo em destaque tipográfico (`fw-bold fs-5`).
    - Marcadores / Categorias (`category_id`) exibidos como pílulas coloridas compactas.
    - Cargo e empresa vinculada (ex.: *"Sales Representative em Acme Corporation"*).
    - Localização geográfica simplificada (Cidade, País).
    - E-mail de contato direto.
    - Indicador numérico de atividades pendentes associadas.
- **[Observado]** Ao aplicar agrupamento (ex.: por País ou Empresa), a grade Kanban converte-se automaticamente em colunas de estágios agrupados, com contadores de itens por coluna e controles de dobra/desdobra (*collapse/expand*).

#### Visualização em Lista (Tabela / Tree View)
- **[Observado]** Colunas exibidas por padrão:
  1. Caixa de seleção para operações em lote (*checkbox*).
  2. Nome (`complete_name`): exibe "Empresa, Pessoa" para contatos subordinados.
  3. Telefone (`phone`).
  4. E-mail (`email`).
  5. Vendedor Responsável (`user_id`).
  6. Atividades (`activity_ids`): ícone de relógio indicando prazos de tarefas.
  7. Cidade (`city`).
  8. País (`country_id`).
  9. Empresa Vinculada (`company_id`).
- **[Observado]** **Seletor de Colunas Opcionais:** Ícone de engrenagem no cabeçalho da tabela permitindo ativar/desativar visibilidade em tempo real das colunas:
  - Celular (`mobile`)
  - Endereço (`street`)
  - Estado / UF (`state_id`)
  - Número de identificação fiscal (`vat`)
  - Método de envio de faturas (`invoice_sending_method`)
  - Formato para EDI (`invoice_edi_format`)
  - Marcadores (`category_id`)
- **[Observado]** Ordenação: clique sobre qualquer título de coluna alterna ordenação ascendente e descendente com indicador de seta.
- **[Observado]** Agrupamento na lista: transforma a tabela em linhas de cabeçalho tipo acordeão (ex.: `Brasil (4)`), permitindo expansão individual.

#### Visualização em Atividade
- **[Observado]** Tabela bidimensional cruzando os contatos (linhas) com os tipos de atividades corporativas (colunas):
  - E-mail
  - Ligação (*Call*)
  - Reunião (*Meeting*)
  - Lista de Tarefas (*To-Do*)
  - Carregar documento (*Upload Document*)

---

## 2. Cadastro de Contatos (Modelo de Dados e Formulário)

O módulo utiliza um modelo polimórfico unificado (`res.partner`) com discriminação de comportamento através do campo `company_type`.

### 2.1 Cabeçalho do Formulário (Campos Principais)

| Campo | Rótulo / Descrição | Tipo | Obrigatoriedade | Regra de Exibição / Dependência |
| :--- | :--- | :--- | :---: | :--- |
| `image_1920` | Foto / Logotipo | Imagem (Binary) | Opcional | Exibe avatar padrão com opção de upload ou limpeza. |
| `company_type` | Tipo de Contato | Radio (`is_company`) | **Obrigatório** | Opções: **Individual** (Pessoa física) ou **Empresa** (Pessoa jurídica). Padrão no cadastro: *Empresa*. |
| `name` | Nome / Razão Social | Texto (CharField 255) | **Obrigatório** | Título principal em tipografia ampliada (`h1`). Autocomplete ativo. |
| `parent_id` | Nome da empresa vinculada | Many2one (`res.partner`) | Opcional | **Exibido apenas quando `company_type == 'Individual'`**. Permite associar o indivíduo a uma empresa existente. |
| `type` | Tipo de Endereço | Seleção | **Obrigatório** (em Individual) | Opções: *Contato*, *Endereço de cobrança*, *Endereço de entrega*, *Outro endereço*. |
| `function` | Cargo / Especialidade | Texto (CharField 100) | Opcional | **Exibido apenas quando `company_type == 'Individual'`**. |
| `title` | Título de Cortesia | Many2one (`res.partner.title`)| Opcional | Ex: Sr., Sra., Dr. **Exibido apenas quando `company_type == 'Individual'`**. |

### 2.2 Bloco de Endereço Geográfico Estruturado
- **[Observado]** O formulário divide o endereço em campos estruturados com renderização compacta:
  - `street_name`: Nome do logradouro / rua (ex.: *Santa Barbara Rd*).
  - `street_number`: Número predial (ex.: *77*).
  - `street_number2`: Complemento (ex.: *Apto 102, Bloco B*).
  - `street2`: Bairro ou segunda linha de endereço.
  - `city`: Cidade.
  - `state_id`: Estado / UF (Many2one com filtro dependente do país selecionado).
  - `zip`: CEP / Código Postal.
  - `country_id`: País (Many2one).
- **[Observado]** Quando um contato individual é vinculado a uma empresa (`parent_id`), os campos de endereço são herdados da empresa-mãe caso o tipo seja "Contato".

### 2.3 Bloco de Identificação Fiscal (Localização Brasil)
- **[Observado]**
  - `l10n_latam_identification_type_id`: Tipo de Identificação (Many2one, **Obrigatório**). Opções observadas: *CNPJ*, *CPF*. Padrão na criação de empresa: *CNPJ*.
  - `vat`: Número do documento (CharField 20). Sujeito à validação matemática de dígitos verificadores e máscara.
  - `l10n_br_ie_code`: Inscrição Estadual (CharField, opcional).
  - `l10n_br_im_code`: Inscrição Municipal (CharField, opcional).
  - `l10n_br_isuf_code`: Código SUFRAMA (CharField, opcional, aplicável a operações na Zona Franca de Manaus).

### 2.4 Canais de Comunicação e Categorização
- **[Observado]**
  - `phone`: Telefone corporativo principal (validação de formato).
  - `mobile`: Celular corporativo.
  - `email`: E-mail corporativo (com link rápido para cliente de e-mail).
  - `website`: URL do site da empresa (validação de protocolo web).
  - `category_id`: Marcadores / Etiquetas corporativas (relação Many2many com paleta de cores para categorização: ex.: *Cliente*, *Fornecedor*, *VIP*, *Fabricante*).

### 2.5 Abas Temáticas do Formulário

#### Aba 1: "Contatos e Endereços" (`contact_addresses`)
- **[Observado]** Grid de contatos subordinados associados à empresa (`child_ids`).
- **[Observado]** Botão **"Adicionar"** dispara um modal dinâmico para cadastramento de vínculos.
- **[Observado]** Modal de Vínculo Subordinado possui 4 opções de tipo (`type`):
  1. **Contato:** Campos de Nome, Cargo, Título de cortesia, E-mail, Telefone, Celular e Notas.
  2. **Endereço de Cobrança:** Substitui cargo/título pelo bloco completo de endereço (Rua, Número, Complemento, Bairro, Cidade, Estado, CEP, País) e dados de faturamento.
  3. **Endereço de Entrega:** Bloco completo de endereço para despacho logístico ou localização de canteiro.
  4. **Outro Endereço:** Endereço auxiliar para correspondências ou filiais.

#### Aba 2: "Vendas e Compras" (`sales_purchases`)
- **[Observado]**
  - **Grupo VENDAS:**
    - `user_id`: Vendedor responsável pelo atendimento (Many2one `res.users`).
    - `property_payment_term_id`: Condições de pagamento padrão em vendas (Many2one `account.payment.term`, ex.: *30 dias*, *À vista*).
    - `property_inbound_payment_method_line_id`: Forma de pagamento de entrada.
  - **Grupo COMPRAS:**
    - `property_supplier_payment_term_id`: Condições de pagamento para compras/fornecedores.
    - `property_outbound_payment_method_line_id`: Forma de pagamento de saída.
  - **Grupo INFORMAÇÃO FISCAL:**
    - `property_account_position_id`: Posição fiscal / Mapeamento tributário (Many2one).
  - **Grupo DIVERSOS:**
    - `company_registry`: Número de registro comercial / Junta comercial.
    - `ref`: Código de referência interna do contato.
    - `company_id`: Vínculo com a empresa operadora (suporte a ambiente *Multi-empresa*).
    - `industry_id`: Ramo de atividade / Indústria (Many2one).

#### Aba 3: "Faturamento" (`accounting`)
- **[Observado]**
  - **Grupo CONTAS BANCÁRIAS (`bank_ids`):** Tabela editável inline contendo:
    - Número da conta / Chave Pix.
    - Banco (Many2one `res.bank`).
    - Flag "Enviar dinheiro" (habilitação para pagamentos automáticos).
  - **Grupo FATURAS DE CLIENTES:**
    - `invoice_sending_method`: Método de envio de faturas (*Baixar*, *Por e-mail*, *Pelo correio*).
    - `invoice_edi_format`: Formato de transmissão eletrônica EDI (ex.: Factur-X, Peppol BIS 3.0, XML padrão).
    - `peppol_eas` e `peppol_endpoint`: Endereçamento e identificação na rede europeia/internacional Peppol.
  - **Grupo AUTOMAÇÃO:**
    - `autopost_bills`: Regra de validação de faturas de compras (*Sempre*, *Perguntar após 3 validações*, *Nunca*).

#### Aba 4: "Anotações Internas" (`internal_notes`)
- **[Observado]**
  - `comment`: Editor de texto para anotações operacionais, observações técnicas e histórico confidencial da equipe sobre o contato.

### 2.6 Botões Estatísticos (*Smart Buttons*)
- **[Observado]** No topo direito do formulário, contadores com acesso rápido:
  - **Vendas (`action_view_sale_order`):** Quantidade de pedidos/propostas comerciais vinculadas (ex.: "2 Vendas").
  - **Faturado (`action_view_partner_invoices`):** Montante total já faturado contra o contato (ex.: "R$ 0,00 Faturado").
- **[Inferido]** Novos módulos (como Projetos e Medições) podem registrar dinamicamente seus próprios *smart buttons* nessa área.

### 2.7 Painel Lateral de Comunicação (*Chatter*)
- **[Observado]**
  - **Enviar mensagem:** Envio de e-mail ao contato diretamente de dentro do sistema, com anexo de arquivos e cópia oculta.
  - **Notas internas:** Registro de apontamento visível exclusivamente para colaboradores internos.
  - **Atividades:** Agendamento de follow-ups com tipo (E-mail, Ligação, Reunião, Tarefa), prazo de conclusão (*Due date*) e responsável designado.
  - **Seguidores:** Gestão de usuários internos e contatos externos inscritos nas notificações do registro.
  - **Histórico de Auditoria Integrado:** Rastreamento cronológico de criação e alteração de campos chave com indicação de autor e horário.

---

## 3. Operações Observadas

### 3.1 Operações Básicas de Ciclo de Vida (CRUD)
- **[Observado] Criação:** Disparada pelo botão "Novo". Formulário carrega valores padrão e destaca campos obrigatórios com sublinhado/estilo específico.
- **[Observado] Consulta:** Abertura imediata a partir de cartões no Kanban ou linhas na tabela.
- **[Observado] Edição:** Permite alteração in-place. O salvamento é automático ao desviar o foco de campos alterados ou explícito via atalhos do teclado.
- **[Observado] Descarte:** Desfaz alterações não salvas restaurando o estado original do banco.

### 3.2 Operações em Lote (Bulk Actions)
Quando um ou mais registros são marcados na visualização em lista:
1. **Exportar:**
   - Abre modal "Exportar dados".
   - Opção de exportação compatível com importação (inclui campos de chave técnica).
   - Formatos suportados: **XLSX** e **CSV**.
   - Seletor de campos disponíveis em árvore hierárquica e painel de campos a exportar.
2. **Arquivar / Desarquivar:**
   - Realiza *Soft Delete* alterando o campo `active` do contato para `False`.
   - Remove o contato das buscas cotidianas sem quebrar a integridade referencial com contratos, faturas e projetos históricos.
3. **Duplicar:**
   - Clona os dados do contato gerando um novo registro com o sufixo "(cópia)".
4. **Excluir:**
   - Realiza exclusão física (`Hard Delete`) se e somente se o contato não possuir registros dependentes com restrição de chave estrangeira (`models.PROTECT`). Caso possua, a exclusão é rejeitada pelo sistema.
5. **Mesclar (Merge Wizard):**
   - Disponível quando 2 ou mais contatos são selecionados.
   - Apresenta assistente de deduplicação exibindo tabela comparativa dos registros.
   - Permite eleger o **"Contato de Destino"**.
   - Redireciona automaticamente todos os documentos, faturas, propostas e tarefas associadas aos contatos secundários para o contato eleito, unificando a base.
6. **Ações de Comunicação:** Envio de E-mail e SMS em massa.
7. **Download (vCard):** Exportação individual ou agrupada no formato padrão de agenda eletrônica `.vcf`.
8. **Conceder acesso ao portal:** Vincula o e-mail do contato a um usuário externo de autoatendimento.

### 3.3 Operação de Importação de Registros
- **[Observado]** Acessada em *Ações > Importar registros* (quando nenhum item estiver marcado).
- **[Observado]** Suporte a arquivos `.xlsx` e `.csv`.
- **[Observado]** Fornece links para download de modelo de planilha pré-formatado (*template*) com as colunas reconhecidas pelo sistema.
- **[Observado]** Mapeamento assistido de colunas da planilha para campos da entidade de contatos com validação prévia de erros de conversão antes da gravação definitiva.

---

## 4. Pesquisa, Filtros e Organização

### 4.1 Mecanismo de Busca Inteligente
- **[Observado]** Campo de entrada único com autocomplete preditivo que sugere dinamicamente critérios específicos conforme o texto digitado:
  - *Buscar Nome para: [termo]*
  - *Buscar Empresa relacionada para: [termo]*
  - *Buscar E-mail para: [termo]*
  - *Buscar Telefone/Celular para: [termo]*
  - *Buscar Marcador para: [termo]*
  - *Buscar Vendedor para: [termo]*
- **[Observado]** Os critérios selecionados transformam-se em cápsulas visuais (*facets*) na barra de pesquisa, combinando filtros com lógica conjuntiva (`AND`).

### 4.2 Filtros Pré-Configurados
- **[Observado]**
  - **Pessoa física:** Filtra registros onde `is_company = False` (29 contatos identificados na base de referência).
  - **Empresas:** Filtra registros onde `is_company = True` (10 contatos identificados).
  - **Faturas de clientes:** Filtra contatos com movimentação de faturamento de saída.
  - **Contas do fornecedor:** Filtra contatos cadastrados como prestadores/vendedores.
  - **Arquivado:** Filtra contatos inativos (`active = False`, 4 contatos identificados).
  - **Filtro Personalizado:** Construtor dinâmico com operadores lógicos (*contém*, *não contém*, *é igual a*, *está definido*, etc.) aplicáveis a qualquer campo do modelo.

### 4.3 Agrupamento Dinâmico (*Group By*)
- **[Observado]** Opções rápidas:
  - **Por Vendedor (`user_id`):** Agrupa os contatos por colaborador responsável.
  - **Por Empresa (`parent_id`):** Agrupa pessoas físicas sob suas respectivas empresas-mãe.
  - **Por País (`country_id`):** Agrupa por território geográfico.
- **[Observado]** Adicionar grupo personalizado: permite agrupar por qualquer campo categórico (ex.: Estado, Cidade, Cargo, Marcadores).
- **[Observado]** Comportamento visual do agrupamento:
  - No Kanban: cria colunas verticais com contadores numéricos de itens por grupo.
  - Na Lista: cria linhas de cabeçalho expansíveis (acordeão) totalizando registros.

### 4.4 Favoritos
- **[Observado]** Permite salvar o conjunto de filtros, buscas e agrupamentos atuais com um nome customizado.
- **[Observado]** Opções:
  - *Usar por padrão:* Abre a tela aplicando automaticamente este filtro.
  - *Compartilhar com todos os usuários:* Torna o filtro visível para a equipe.

---

## 5. Permissões e Regras de Governança Observadas

### 5.1 Restrições de Acesso
- **[Observado]** O usuário operacional padrão (`demo`) tem acesso pleno de leitura e edição à carteira de contatos, mas **não visualiza** os menus de parametrização global (tabelas de países, títulos, ramos de atividade).
- **[Inferido]** A criação e manutenção de tabelas auxiliares (ex.: cadastro de Bancos, Estados e Países) requer perfil de administração de sistemas / TI.
- **[Observado]** A visibilidade de informações financeiras (como faturas e pedidos de vendas) está conectada às permissões dos módulos de Faturamento e Vendas.

### 5.2 Regras de Negócio e Integridade Cadastral
- **[Observado] Unicidade Cadastral:** O sistema alerta e desencoraja a duplicidade de números fiscais (CNPJ/CPF) e e-mails.
- **[Observado] Dependência de Tipo:** A alteração do radio `company_type` oculta instantaneamente campos exclusivos de indivíduo (como `parent_id`, `function` e `title`), limpando seus vínculos lógicos para evitar inconsistências.
- **[Observado] Integridade de Exclusão:** Registros com histórico transacional não podem ser excluídos fisicamente, devendo ser arquivados para auditoria.

---

## 6. Requisitos para Implementação no ERPangea (v2.0.1)

Com base nas observações da aplicação de referência e no contexto corporativo de engenharia civil/geotécnica da Pangea Engenharia, detalham-se os requisitos para desenvolvimento:

### 6.1 Requisitos Funcionais (RF)

- **RF01 - Modelo Polimórfico de Contatos:** O sistema deve suportar contatos corporativos classificados como Pessoa Jurídica (Empresa) e Pessoa Física (Individual) em uma mesma entidade base, controlada pelo discriminador de tipo.
- **RF02 - Relação Hierárquica Empresa-Subordinados:** Permitir que contatos individuais sejam vinculados a uma empresa-mãe (`parent_id`), herdando dados de endereço e exibindo identificação composta (*"Empresa, Nome"*).
- **RF03 - Tipificação de Endereços Secundários:** O sistema deve permitir o cadastro de múltiplos endereços e pessoas de contato associadas a uma empresa, categorizados como:
  - *Contato Técnico / Comercial*
  - *Endereço de Cobrança / Faturamento*
  - *Endereço de Canteiro / Entrega de Obras*
  - *Outro Endereço*
- **RF04 - Validação Fiscal Brasileira:**
  - Campo de tipo de documento (*CNPJ* ou *CPF*).
  - Validação matemática obrigatória de dígitos verificadores para CPF (11 dígitos) e CNPJ (14 dígitos).
  - Campos opcionais para Inscrição Estadual (IE), Inscrição Municipal (IM) e Código SUFRAMA.
  - Detecção assíncrona de duplicidade de documento via HTMX ao perder o foco (*blur*).
- **RF05 - Categorização por Marcadores (Tags):** Suporte a etiquetas coloridas dinâmicas para segmentação comercial e operacional (ex.: *Cliente*, *Fornecedor Sondagem*, *Projetista Parceiro*, *Órgão Ambiental/Público*).
- **RF06 - Visualizações Múltiplas:**
  - **Visualização Kanban:** Cartões com avatar, sub-avatar da empresa vinculada, cargo, cidade/UF, e-mail e tags.
  - **Visualização em Tabela:** Grid com ordenação em tempo real, seleção de colunas opcionais e paginação assíncrona.
- **RF07 - Barra de Busca com Facets e Autocomplete:** Campo de busca textual unificado com sugestões preditivas para filtrar por Nome, Razão Social, CNPJ/CPF, E-mail, Telefone ou Marcador.
- **RF08 - Filtros Rápidos e Agrupamento:**
  - Filtros rápidos: *Empresas*, *Pessoas Físicas*, *Clientes*, *Fornecedores*, *Arquivados*.
  - Agrupamento dinâmico: por Cidade, Estado, Vendedor e Empresa-Mãe.
- **RF09 - Operação de Arquivamento (Soft Delete):** Capacidade de arquivar contatos inativos sem exclusão física do banco, ocultando-os das seleções normais e mantendo o histórico de auditoria.
- **RF10 - Assistente de Mesclagem (Deduplicação):** Funcionalidade para fundir dois ou mais contatos duplicados em um contato principal, transferindo automaticamente contratos, propostas, medições e documentos para o contato consolidado.
- **RF11 - Exportação e Importação de Dados:**
  - Exportação em formato XLSX e CSV dos contatos filtrados.
  - Importação assistida a partir de planilhas Excel/CSV com modelo padrão para download.
- **RF12 - Trilha de Auditoria Imutável:** Todas as criações, atualizações de campos e arquivamentos devem disparar gravação automática no `apps.audit_log.AuditLog`.

### 6.2 Requisitos Não Funcionais (RNF)

- **RNF01 - Performance de Busca:** Consultas textuais por nome, razão social ou documento devem responder em tempo inferior a 250ms para bases de até 50.000 contatos, utilizando índices B-Tree e `pg_trgm` (PostgreSQL).
- **RNF02 - Interface Reativa sem SPA Pesada:** O dinamismo de filtros, paginação, modais e validação de documentos deve ser viabilizado exclusivamente com HTMX e partials HTML do Django, mantendo o consumo de memória client-side mínimo.
- **RNF03 - Segurança e RBAC:** Apenas colaboradores com nível hierárquico mínimo de *Operacional (Nível 2)* nos setores autorizados podem criar ou editar dados fiscais de contatos.
- **RNF04 - Responsividade e Ergonomia Visual:** A interface deve seguir rigorosamente a identidade visual corporativa do ERPangea em Bootstrap 5.3, com suporte a resoluções desktop e tablet.

---

## 7. Modelagem de Dados Proposta para o ERPangea

### 7.1 Entidade Principal: `apps.contacts.models.Contact`
```python
# [Inferido com base nos modelos observados res.partner]
class ContactTypeChoices(models.TextChoices):
    COMPANY = 'COMPANY', 'Pessoa Jurídica (Empresa)'
    INDIVIDUAL = 'INDIVIDUAL', 'Pessoa Física (Individual)'

class AddressTypeChoices(models.TextChoices):
    CONTACT = 'CONTACT', 'Contato'
    INVOICE = 'INVOICE', 'Endereço de Cobrança'
    DELIVERY = 'DELIVERY', 'Endereço de Entrega / Canteiro'
    OTHER = 'OTHER', 'Outro Endereço'

class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact_type = models.CharField(max_length=15, choices=ContactTypeChoices.choices, default=ContactTypeChoices.COMPANY)
    address_type = models.CharField(max_length=15, choices=AddressTypeChoices.choices, default=AddressTypeChoices.CONTACT)
    
    # Identificação
    name = models.CharField("Nome / Razão Social", max_length=255, db_index=True)
    trade_name = models.CharField("Nome Fantasia", max_length=255, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subordinates')
    
    # Documentos Fiscais
    doc_type = models.CharField("Tipo de Documento", max_length=10, choices=[('CNPJ', 'CNPJ'), ('CPF', 'CPF')], default='CNPJ')
    doc_number = models.CharField("Número do Documento", max_length=20, unique=True, db_index=True)
    state_registration = models.CharField("Inscrição Estadual", max_length=30, blank=True)
    municipal_registration = models.CharField("Inscrição Municipal", max_length=30, blank=True)
    suframa_code = models.CharField("Código SUFRAMA", max_length=30, blank=True)
    
    # Endereço Estruturado
    street = models.CharField("Logradouro", max_length=200, blank=True)
    number = models.CharField("Número", max_length=20, blank=True)
    complement = models.CharField("Complemento", max_length=100, blank=True)
    neighborhood = models.CharField("Bairro", max_length=100, blank=True)
    city = models.CharField("Cidade", max_length=100, db_index=True, blank=True)
    state = models.CharField("Estado / UF", max_length=2, db_index=True, blank=True)
    postal_code = models.CharField("CEP", max_length=10, blank=True)
    country = models.CharField("País", max_length=50, default='Brasil')
    
    # Contato e Profissional
    phone = models.CharField("Telefone", max_length=25, blank=True)
    mobile = models.CharField("Celular", max_length=25, blank=True)
    email = models.EmailField("E-mail", blank=True, db_index=True)
    website = models.URLField("Website", blank=True)
    job_title = models.CharField("Cargo / Função", max_length=100, blank=True)
    
    # Comercial e Financeiro
    salesperson = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    payment_terms = models.CharField("Condições de Pagamento", max_length=50, blank=True)
    tags = models.ManyToManyField('ContactTag', blank=True, related_name='contacts')
    
    # Controle
    avatar = models.ImageField(upload_to='contacts/avatars/', null=True, blank=True)
    internal_notes = models.TextField("Anotações Internas", blank=True)
    is_active = models.BooleanField("Ativo", default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 7.2 Entidade de Categorização: `apps.contacts.models.ContactTag`
```python
class ContactTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome do Marcador", max_length=50, unique=True)
    color = models.CharField("Cor (Hex ou Bootstrap)", max_length=20, default="#2563eb")
```

---

## 8. Critérios de Aceite para Validação e Testes

### Cenário 1: Cadastro de Empresa com Validação de CNPJ
- **Dado** que um usuário com perfil Comercial ou Administrativo clica em "Novo Contato"
- **Quando** o tipo for "Pessoa Jurídica" e ele preencher um CNPJ matematicamente inválido (ex.: `11.111.111/1111-11`)
- **Então** o sistema deve emitir um feedback visual imediato de erro via HTMX sem recarregar a tela
- **E** o salvamento deve ser bloqueado até a correção para um CNPJ válido com 14 dígitos.

### Cenário 2: Adição de Contato Subordinado com Logotipo da Empresa
- **Dado** uma empresa previamente cadastrada (ex.: *"Pangea Obras Ltda."*)
- **Quando** o usuário adicionar um subordinado do tipo "Contato" com nome *"João Engenheiro"*
- **Então** o subordinado deve ser registrado vinculado à empresa-mãe
- **E** na visualização Kanban, o cartão de João deve renderizar o sub-avatar com o logotipo da Pangea Obras no canto inferior direito.

### Cenário 3: Bloqueio de Duplicidade de Documento
- **Dado** que já existe um contato cadastrado com o CPF `123.456.789-00`
- **Quando** outro operador tentar cadastrar um novo contato com o mesmo CPF
- **Então** o sistema deve exibir alerta informando que o documento já pertence a um contato cadastrado e impedir o registro duplicado.

### Cenário 4: Arquivamento e Desarquivamento (*Soft Delete*)
- **Dado** um contato com histórico de propostas ou contratos associados
- **Quando** o usuário acionar a opção "Arquivar"
- **Então** o contato deve ser marcado como `is_active = False`
- **E** o contato deve desaparecer da listagem padrão de contatos ativos
- **E** os contratos e propostas históricas devem permanecer íntegros sem quebra de integridade referencial
- **E** o contato deve ser reencontrado e recuperável ao aplicar o filtro "Arquivado".

### Cenário 5: Assistente de Mesclagem de Contatos Duplicados
- **Dado** que dois registros distintos representam a mesma empresa com grafias ligeiramente diferentes
- **Quando** o administrador selecionar ambos na lista e acionar "Ações > Mesclar"
- **E** selecionar o contato de destino definitivo
- **Então** o sistema deve reassociar todas as entidades filhas (endereços, subordinados, faturas) ao contato eleito
- **E** remover ou arquivar o registro redundante, gravando a operação no `AuditLog`.

---

## 9. Pontos Não Verificados e Decisões de Projeto

1. **[Não verificado] Protocolo Peppol Internacional:**
   - *Observação:* A interface do Odoo exibe campos de transmissão eletrônica Peppol (EAS / Endpoint).
   - *Decisão para ERPangea:* Dispensável para a operação local no Brasil. O módulo nacional deve focar na emissão direta de NFS-e (já implementada nas especificações anteriores) e campos de NF-e/SEFAZ (IE/IM).
2. **[Não verificado] Sincronização Automática com Receita Federal:**
   - *Observação:* O campo de busca de parceiros no Odoo possui classe `o_field_field_partner_autocomplete` para preenchimento automático.
   - *Decisão para ERPangea:* Implementar endpoint opcional consumindo API pública (ex.: BrasilAPI / ReceitaWS) para autocompletar Razão Social e Endereço a partir da digitação do CNPJ.
3. **[Observado vs Inferido] Módulo de Atividades:**
   - *Observação:* O módulo de contatos do Odoo integra-se fortemente à agenda de atividades (ligações, reuniões, tarefas).
   - *Decisão para ERPangea:* A interface do Kanban deve exibir o indicador de atividades, conectando-se ao módulo de Projetos e Tarefas do ERPangea.
