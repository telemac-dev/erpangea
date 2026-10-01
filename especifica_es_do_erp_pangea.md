# Documento de Especificações Técnicas e Funcionais (SRS)
## Sistema Integrado de Gestão Empresarial – ERP Pangea

**Organização:** Pangea Engenharia Ltda.  
**Domínio:** Consultoria e Projetos de Engenharia Civil, Geotecnia, Fundações, Contenções e Obras de Terra  
**Referência Institucional:** [www.pangeaengenharia.com.br](https://www.pangeaengenharia.com.br)  
**Padrão Arquitetural:** Monólito Modular Reativo (Modular Monolith)  
**Stack Principal:** Python 3.12+ | Django 5.x | PostgreSQL 16 | HTMX 1.9+ | Bootstrap 5.3  

---

## 1. Visão Geral da Arquitetura e Stack Tecnológica

O sistema adota uma arquitetura de monólito modular de alta coesão e baixo acoplamento entre aplicações Django. A interface dinâmica é viabilizada pelo HTMX por meio da substituição de fragmentos HTML (*HTML partials*), eliminando a sobrecarga de frameworks SPA pesados e simplificando o desenvolvimento corporativo.

```
                    ┌───────────────────────────────────────────┐
                    │      Cliente Web (Desktop / Tablet)       │
                    │      Bootstrap 5.3 + HTMX + Vanilla JS    │
                    └─────────────────────┬─────────────────────┘
                                          │ HTTP (HTML Partials / JSON)
                                          ▼
                    ┌───────────────────────────────────────────┐
                    │             Reverse Proxy (Nginx)         │
                    └─────────────────────┬─────────────────────┘
                                          │ WSGI (Gunicorn)
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                Aplicação Django (ERP Pangea)                           │
│                                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ core_auth    │  │ audit_log    │  │ contacts     │  │ commercial   │  │ projects │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────┬─────┘  │
│         │                 │                 │                 │               │        │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐       │        │
│  │ edms_docs    │  │ measurements │  │ invoices     │  │ financial    │       │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │        │
│         └─────────────────┴─────────────────┼─────────────────┴───────────────┘        │
│                                             ▼                                          │
│                                Django ORM / Signals / Middleware                       │
└─────────────────────────────────────────────┬──────────────────────────────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
          ┌───────────────────────┐                       ┌───────────────────────┐
          │  PostgreSQL (Relacional) │                      │     Storage Local/S3  │
          │  + pg_trgm (Fulltext) │                       │  (DWG, DXF, PDF, ART) │
          └───────────────────────┘                       └───────────────────────┘
```

### Componentes de Infraestrutura
*   **Backend Framework:** Django 5.x com ORM e `django-crispy-forms` integrado ao Bootstrap 5.
*   **Camada de Dinamismo:** HTMX com atributos `hx-get`, `hx-post`, `hx-target` e `hx-swap="innerHTML"`.
*   **Banco de Dados:** PostgreSQL 16 com extensão `pg_trgm` ativada para indexação e busca textual de alta performance sobre nomes de clientes, códigos de prancha e projetos.
*   **Storage de Arquivos:** Sistema com segregação de mídias por diretório de projeto e nomes versionados criptograficamente para evitar sobrescritas acidentais.
*   **Reverse Proxy & Servidor WSGI:** Nginx com terminação TLS/SSL e Gunicorn com múltiplos workers baseados em CPUs disponíveis.

---

## 2. Matriz de Perfis e Permissões (RBAC)

O controle de acesso ao sistema é fundamentado em grupos do Django estruturados nos 5 setores corporativos da Pangea Engenharia:

| Setor / Papel | Visualização de Projetos & Docs | Edição Técnica & Uploads | Gestão Comercial (Propostas) | Medições & Faturamento | Contas a Pagar | Gestão de TI & Acessos |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Comercial** | Leitura básica | ❌ | Criação / Edição | Consulta | ❌ | ❌ |
| **Técnico (Engenharia)** | Total | Criação / Revisão | Consulta | Criação de Medições | ❌ | ❌ |
| **Financeiro** | Acompanhamento | ❌ | Consulta de Contratos | Emissão NF / Aprovação | Total | ❌ |
| **Administrativo** | Consulta geral | Consulta | Consulta | Consulta | Lançamentos | ❌ |
| **TI / Administrador** | Total | Total | Total | Total | Total | Total |

---

## 3. Especificação Funcional dos Módulos

### Módulo 1: Gestão de Usuários e Perfis (`core_auth`)
*   **Objetivo:** Gerenciar autenticação segura, controle de sessões e perfis customizados dos colaboradores.
*   **Modelos de Dados:**
    *   `User`: Baseado no `AbstractUser` padrão com `email` como chave primária de login.
    *   `UserProfile`: Relação 1:1 com `User`.
        *   `setor`: Enum (`ADMINISTRATIVO`, `COMERCIAL`, `TECNICO`, `FINANCEIRO`, `TI`).
        *   `telefone`: CharField formatado com máscara internacional/nacional.
        *   `cargo`: CharField descritivo (ex.: Engenheiro Geotécnico Sênior, Cadista, Coordenador de Projetos).
        *   `numero_crea`: CharField opcional com número de inscrição e UF no conselho de classe.
        *   `avatar`: ImageField para foto de identificação.
*   **Regras de Negócio:**
    *   O usuário possui autorização para atualizar seus próprios dados de contato, foto e senha de acesso.
    *   A modificação de `setor`, `is_active` e permissões de grupo é restrita a usuários com perfil do setor de TI ou Superusuários.
    *   Implementação de bloqueio temporário após 5 tentativas de autenticação com falha consecutiva.

### Módulo 2: Auditoria e Trilha de Eventos (`audit_log`)
*   **Objetivo:** Rastreamento integral de alterações para conformidade, segurança operacional e auditoria interna.
*   **Modelos de Dados:**
    *   `ActivityLog`:
        *   `usuario`: Chave estrangeira para `User` (SET_NULL on delete).
        *   `ip_address`: GenericIPAddressField capturado via cabeçalhos HTTP.
        *   `user_agent`: TextField descritivo da plataforma de acesso.
        *   `timestamp`: DateTimeField indexado com criação automática.
        *   `acao`: Enum (`CREATE`, `UPDATE`, `DELETE`, `LOGIN`, `LOGOUT`, `EXPORT`).
        *   `app_label` e `model_name`: Identificadores do recurso modificado.
        *   `object_id`: Identificador do registro-alvo.
        *   `object_repr`: Representação legível do objeto.
        *   `changes`: JSONField estruturado contendo `{campo: [valor_antigo, valor_novo]}`.
*   **Regras de Negócio:**
    *   Todas as mutações de dados em modelos operacionais disparam signals automáticos que gravam no `ActivityLog`.
    *   A tabela de auditoria é imutável via interface de usuário: permissões de `UPDATE` e `DELETE` são revogadas ao nível de modelo e administração Django.

### Módulo 3: Gerenciamento Unificado de Contatos (`contacts`)
*   **Objetivo:** Centralização de cadastros de clientes, subempreiteiros, consultores, fornecedores de materiais e órgãos públicos reguladores.
*   **Modelos de Dados:**
    *   `Contact`:
        *   `tipo_pessoa`: Enum (`PF`, `PJ`).
        *   `razao_social_nome`: CharField(255).
        *   `nome_fantasia`: CharField(255), opcional para PF.
        *   `cpf_cnpj`: CharField(18), indexado e único, com validação de dígitos verificadores.
        *   `inscricao_estadual` e `inscricao_municipal`: CharFields opcionais.
        *   `classificacoes`: ArrayField ou ManyToManyField para suportar múltiplos vínculos (`LEAD`, `CLIENTE`, `FORNECEDOR`, `PARCEIRO`, `ORGAO_PUBLICO`).
        *   `email_principal` e `telefone_principal`.
    *   `Address`: Vinculado por chave estrangeira (1:N), suportando endereço comercial e endereço de canteiro/obra.
    *   `ContactPerson`: Pessoas de contato vinculadas a PJs (Nome, E-mail, Cargo, Telefone Direto).
*   **Regras de Negócio:**
    *   Verificação assíncrona com HTMX no evento `blur` do campo de CPF/CNPJ para alertar duplicidade antes da submissão do formulário.
    *   Fornecedores e subcontratados devem ter validação cadastral completa para permitir vinculação a lançamentos de Contas a Pagar.

### Módulo 4: Gestão Comercial, Contratos e Ordens de Serviço (`commercial`)
*   **Objetivo:** Gestão do ciclo de vida das oportunidades de engenharia geotécnica e contenções, formalização de contratos e acionamento técnico.
*   **Modelos de Dados:**
    *   `Proposal`:
        *   `codigo_proposta`: Sequencial formatado (ex.: `PROP-2026-0012`).
        *   `cliente`: FK para `Contact`.
        *   `disciplina_principal`: Enum (`FUNDACOES`, `CONTENCOES`, `OBRAS_TERRA`, `ESTRUTURAS`, `PAVIMENTACAO`, `CONSULTORIA`).
        *   `valor_global`: DecimalField(12, 2).
        *   `status`: Enum (`RASCUNHO`, `ENVIADA`, `EM_NEGOCIACAO`, `APROVADA`, `DECLINADA`).
        *   `validade`: DateField.
    *   `Contract`:
        *   `proposta`: OneToOneField para `Proposal`.
        *   `numero_contrato`: CharField(50) único.
        *   `data_assinatura`, `data_vigencia_inicio`, `data_vigencia_fim`.
        *   `valor_total_contratado`: DecimalField(12, 2).
        *   `modalidade_cobranca`: Enum (`MEDICAO_MENSAL`, `PRECO_GLOBAL_MARCOS`, `HORAS_TECNICAS`).
        *   `documento_assinado`: FileField para anexo do PDF assinado digitalmente.
    *   `WorkOrder` (OS):
        *   `contrato`: FK para `Contract`.
        *   `numero_os`: Sequencial anual.
        *   `coordenador_tecnico`: FK para `User` do setor Técnico.
        *   `status`: Enum (`PLANEJAMENTO`, `ATIVA`, `SUSPENSA`, `CONCLUIDA`).
*   **Regras de Negócio:**
    *   A aprovação de uma Proposta Comercial trava a edição de valores e gera automaticamente uma minuta de Contrato.
    *   Uma Ordem de Serviço (OS) só pode ser ativada caso o Contrato correspondente esteja com o arquivo assinado validado pelo setor financeiro/administrativo.

### Módulo 5: Gestão de Projetos, Tarefas e Acompanhamento de Obras (`projects`)
*   **Objetivo:** Coordenação da execução dos projetos executivos de engenharia, cronogramas de sondagens/cálculos e comunicações internas.
*   **Modelos de Dados:**
    *   `Project`:
        *   `ordem_servico`: OneToOneField para `WorkOrder`.
        *   `nome_projeto`: CharField(255).
        *   `localizacao`: CharField descritivo ou coordenadas geográficas para mapeamento da obra.
        *   `status`: Enum (`BRIEFING`, `ESTUDOS_PRELIMINARES`, `CALCULO_DIMENSIONAMENTO`, `DESENHO_DETALHAMENTO`, `REVISAO_INTERNA`, `ENTREGUE`).
        *   `percentual_avanco`: DecimalField calculado dinamicamente com base nas tarefas e fases concluídas.
    *   `ProjectPhase`: Etapas estruturadas (ex.: Sondagens SPT, Análise de Taludes, Detalhamento de Muro de Flexão).
    *   `Task`: Tarefas individuais com atribuição a engenheiros e cadistas (`titulo`, `responsavel`, `prioridade`, `status`, `horas_previstas`, `horas_gastas`).
    *   `ProjectCommunication`: Registro unificado de reuniões, alinhamentos com clientes, notas técnicas e atas de visita de obra.
*   **Regras de Negócio:**
    *   O avanço do projeto para as fases de "Revisão Interna" e "Entregue" exige checklist de validação técnica aprovado pelo Responsável Técnico (RT).
    *   Tarefas com impedimento técnico notificam automaticamente o coordenador do projeto.

### Módulo 6: Gestão Eletrônica de Documentos - EDMS (`edms_docs`)
*   **Objetivo:** Versionamento estrito e arquivamento seguro de arquivos de engenharia, pranchas CAD, relatórios de sondagem e ARTs.
*   **Modelos de Dados:**
    *   `ProjectDocument`:
        *   `projeto`: FK para `Project`.
        *   `tipo`: Enum (`SONDAGEM_SPT_CPTU`, `MEMORIA_CALCULO`, `PRANCHA_CAD_BIM`, `RELATORIO_TECNICO`, `ART_CREA`, `OUTRO`).
        *   `codigo_identificador`: CharField único por projeto (ex.: `PG-PROJ-01-EST-001`).
        *   `titulo`: CharField(255).
    *   `DocumentRevision`:
        *   `documento`: FK para `ProjectDocument`.
        *   `revisao`: CharField (ex.: `R00`, `R01`, `R02`).
        *   `arquivo`: FileField com validação de extensão e antivírus.
        *   `data_upload`: DateTimeField.
        *   `enviado_por`: FK para `User`.
        *   `status`: Enum (`EM_ELABORACAO`, `APROVADO_INTERNO`, `EMITIDO_CLIENTE`, `APROVADO_CLIENTE`).
        *   `notas_alteracao`: TextField documentando alterações da revisão.
*   **Regras de Negócio:**
    *   O upload de um arquivo para um documento existente incrementa automaticamente a numeração da revisão; versões anteriores tornam-se somente-leitura e imutáveis.
    *   Extensões permitidas: `.dwg`, `.dxf`, `.pdf`, `.xlsx`, `.cype`, `.gsz`, `.plx`.
    *   Um projeto não pode transicionar para o status "Entregue" sem pelo menos uma ART (Anotação de Responsabilidade Técnica) homologada no repositório.

### Módulo 7: Gestão de Medições Físico-Financeiras (`measurements`)
*   **Objetivo:** Apuração das entregas parciais ou totais para subsidiar a autorização de faturamento.
*   **Modelos de Dados:**
    *   `MeasurementSheet`:
        *   `contrato`: FK para `Contract`.
        *   `numero_medicao`: IntegerField sequencial por contrato.
        *   `competencia`: DateField (mês/ano de referência).
        *   `valor_total_medido`: DecimalField(12, 2).
        *   `status`: Enum (`RASCUNHO`, `SUBMETIDA_TECNICO`, `APROVADA_CLIENTE`, `REJEITADA`, `FATURADA`).
        *   `documento_comprovatorio`: FileField com o relatório de medição com assinatura ou aceite formal da fiscalização/cliente.
    *   `MeasurementItem`:
        *   `folha_medicao`: FK para `MeasurementSheet`.
        *   `discriminacao`: CharField(255).
        *   `percentual_executado`: DecimalField(5, 2).
        *   `valor_apurado`: DecimalField(12, 2).
*   **Regras de Negócio:**
    *   A soma percentual acumulada das medições para um mesmo item contratual não pode ultrapassar 100% sem aditivo registrado.
    *   Apenas medições com status "Aprovada pelo Cliente" ficam disponíveis para seleção no módulo de emissão de NFS-e.

### Módulo 8: Faturamento e Notas Fiscais de Serviços (`invoices`)
*   **Objetivo:** Emissão, controle fiscal e acompanhamento do recebimento das Notas Fiscais de Serviços Eletrônicas (NFS-e).
*   **Modelos de Dados:**
    *   `ServiceInvoice`:
        *   `medicao`: OneToOneField para `MeasurementSheet`.
        *   `numero_nfse`: CharField(30) único.
        *   `codigo_verificacao`: CharField(50).
        *   `data_emissao`: DateField.
        *   `valor_bruto`: DecimalField(12, 2).
        *   `aliquota_iss`: DecimalField(5, 2).
        *   `retencoes_federais`: JSONField com detalhamento de PIS, COFINS, INSS, CSLL, IRRF.
        *   `valor_liquido`: DecimalField(12, 2).
        *   `status`: Enum (`SOLICITADA`, `EMITIDA`, `PAGA`, `CANCELADA`).
        *   `arquivo_xml`: FileField.
        *   `arquivo_pdf`: FileField.
    *   `AccountReceivable`:
        *   `nota_fiscal`: FK para `ServiceInvoice`.
        *   `numero_parcela`: IntegerField.
        *   `data_vencimento`: DateField.
        *   `data_recebimento`: DateField nulo até a liquidação.
        *   `valor_parcela`: DecimalField(12, 2).
        *   `status`: Enum (`A_VENCER`, `VENCIDA`, `LIQUIDADA`).
*   **Regras de Negócio:**
    *   Ao emitir uma NFS-e, as parcelas financeiras em `AccountReceivable` são geradas automaticamente respeitando os prazos acordados no Contrato (ex.: 15, 30, 45 dias).
    *   O cancelamento da NFS-e cancela as contas a receber associadas e estorna a medição para o status "Aprovada pelo Cliente", permitindo refaturamento.

### Módulo 9: Gestão de Contas a Pagar (`financial`)
*   **Objetivo:** Controle dos compromissos financeiros da Pangea Engenharia com fornecedores de perfuração/sondagem, laboratórios de solos, locação de softwares e custos fixos.
*   **Modelos de Dados:**
    *   `AccountPayable`:
        *   `fornecedor`: FK para `Contact`.
        *   `projeto`: FK opcional para `Project` (para cálculo de margem direta e rentabilidade por obra).
        *   `centro_de_custo`: Enum (`ADMINISTRATIVO`, `OPERACIONAL_GEOTECNIA`, `COMERCIAL`, `TI_SOFTWARES`).
        *   `categoria_despesa`: CharField categorizado (ex.: Laboratório, Combustível Canteiro, Licenças CAD, Honorários).
        *   `descricao`: CharField(255).
        *   `valor_nominal`: DecimalField(12, 2).
        *   `data_vencimento`: DateField indexado.
        *   `data_pagamento`: DateField opcional.
        *   `comprovante_fiscal`: FileField para DANFE/NFS-e do fornecedor ou boleto.
        *   `status`: Enum (`AGUARDANDO_APROVACAO`, `APROVADA`, `LIQUIDADA`, `CANCELADA`).
*   **Regras de Negócio:**
    *   Despesas superiores a R$ 5.000,00 lançadas pelo setor Administrativo entram em fila com status `AGUARDANDO_APROVACAO`, demandando liberação formal de um usuário do grupo Financeiro ou Diretoria.
    *   Toda conta liquidada exige o anexo obrigatório do comprovante bancário de transferência ou liquidação de boleto.

---

## 4. Diagrama Lógico de Dados (Entidade-Relacionamento)

```
 [core_auth.User] 1 ──── 1 [core_auth.UserProfile]
         │
         ├──< (Auditor) >─── [audit_log.ActivityLog]
         │
         ├──< (Responsável) >─── [projects.Project]
         │                              │
         │                              ├── 1 ──< [projects.Task]
         │                              ├── 1 ──< [projects.ProjectPhase]
         │                              └── 1 ──< [edms_docs.ProjectDocument] ── 1 ──< [DocumentRevision]
         │
 [contacts.Contact]
         │
         ├── 1 ──< [commercial.Proposal]
         │                 │
         │                 └── 1 ──── 1 [commercial.Contract]
         │                                      │
         │                                      ├── 1 ──< [commercial.WorkOrder] ──> (Vincula Project)
         │                                      │
         │                                      └── 1 ──< [measurements.MeasurementSheet]
         │                                                        │
         │                                                        └── 1 ──< [invoices.ServiceInvoice]
         │                                                                          │
         │                                                                          └── 1 ──── 1 [AccountReceivable]
         │
         └── 1 ──< [financial.AccountPayable] >── (Opcional: Apropriação de Custo) ── [projects.Project]
```

---

## 5. Padrões de Interface: HTMX + Bootstrap 5

Para garantir alta produtividade sem sacrificar desempenho de rede, a aplicação adota os seguintes padrões de interação:

1.  **Carregamento de Modais Dinâmicos:**
    ```html
    <!-- Botão de disparo na listagem -->
    <button class="btn btn-primary"
            hx-get="/contacts/create/modal/"
            hx-target="#modal-container"
            hx-swap="innerHTML"
            data-bs-toggle="modal"
            data-bs-target="#genericModal">
      Novo Contato
    </button>
    ```
2.  **Validação e Máscaras Assíncronas:**
    ```html
    <!-- Campo com validação ao perder foco -->
    <input type="text"
           name="cpf_cnpj"
           class="form-control"
           hx-post="/contacts/validate-document/"
           hx-trigger="blur"
           hx-target="#doc-feedback"
           hx-swap="innerHTML" />
    <div id="doc-feedback"></div>
    ```
3.  **Filtragem de Tabelas em Tempo Real:**
    ```html
    <!-- Filtro de busca com debounce de 400ms -->
    <input type="search"
           name="q"
           class="form-control"
           placeholder="Filtrar por projeto, código ou cliente..."
           hx-get="/projects/search/"
           hx-trigger="keyup changed delay:400ms"
           hx-target="#projects-table-body"
           hx-swap="innerHTML" />
    ```

---

## 6. Fases de Desenvolvimento e Critérios de Aceitação

```
Fase 1: Fundação & Auth ────► Fase 2: CRM & Comercial ────► Fase 3: Projetos & EDMS
                                                                  │
Fase 6: Homologação & Go-Live ◄─── Fase 5: Financeiro Total ◄─────┘
                                  (Medições, NFS-e e Contas)
```

### Fase 1: Fundação, Autenticação e Cadastros Base
*   **Entregáveis:** Projeto Django configurado em containers Docker; modelos `User`, `UserProfile` e grupos de permissão (RBAC); sistema de auditoria `ActivityLog` via signals; módulo `contacts` completo.
*   **Critérios de Aceitação:**
    *   Usuários efetuam login e editam seus dados no perfil.
    *   Acesso a áreas não autorizadas retorna resposta HTTP 403 padronizada.
    *   Toda criação, alteração ou exclusão de contatos gera log imutável contendo IP, usuário e diff dos campos alterados.

### Fase 2: Gestão Comercial e Contratual
*   **Entregáveis:** Módulo `commercial` com telas de propostas, geração sequencial de códigos, conversão em contratos, geração de ordens de serviço (OS) e exportação de proposta em PDF.
*   **Critérios de Aceitação:**
    *   Ao aprovar uma proposta, a alteração de seu escopo é bloqueada e uma minuta de Contrato é instanciada.
    *   Uma OS só pode ser despachada para o setor técnico se o contrato estiver associado a um anexo digitalizado.

### Fase 3: Engenharia, Projetos e Documentação Técnica (EDMS)
*   **Entregáveis:** Módulo `projects` integrado com `edms_docs`; visualização em quadro de tarefas; versionador de arquivos técnicos com detecção de pranchas CAD e relatórios de sondagem.
*   **Critérios de Aceitação:**
    *   Envio de uma nova versão de prancha gera a revisão incremental (`R00` -> `R01`), preservando a versão anterior intacta para histórico.
    *   O encerramento do projeto é bloqueado se não houver pelo menos uma ART anexada e aprovada.

### Fase 4: Operação de Campo, Medições e Faturamento
*   **Entregáveis:** Módulo `measurements` e módulo `invoices`; folha de medição com itens contratuais e módulo de emissão e controle de NFS-e.
*   **Critérios de Aceitação:**
    *   O somatório das medições parciais não pode ultrapassar o saldo financeiro do contrato.
    *   A emissão de uma NFS-e gera automaticamente os títulos a receber com as datas de vencimento configuradas.

### Fase 5: Gestão Financeira (Contas a Pagar) e Fluxo de Caixa
*   **Entregáveis:** Módulo `financial` com gestão de pagamentos a fornecedores, rateio de custos por projeto e rotina de aprovação de alçadas.
*   **Critérios de Aceitação:**
    *   Lançamentos de contas a pagar superiores a R$ 5.000,00 ficam retidos até autorização de usuário do grupo Financeiro/Diretoria.
    *   Geração de relatório financeiro confrontando receitas medidas vs. despesas alocadas por projeto.

### Fase 6: Homologação, Testes e Go-Live
*   **Entregáveis:** Cobertura de testes unitários e de integração nos serviços críticos; documentação operacional; rotina de backup automatizada com retenção externa.
*   **Critérios de Aceitação:**
    *   Cobertura de testes automatizados superior a 80% nos módulos financeiros e contratuais.
    *   Restauração de backup do banco de dados e arquivos de mídia validada em ambiente espelho em tempo inferior a 30 minutos.