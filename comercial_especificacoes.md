# Especificação Técnica e Funcional do Módulo Comercial e Contratual (ERPangea)

**Código do Módulo:** `MOD-COM-CTR-01`  
**Data de Emissão:** 05 de outubro de 2026  
**Empresa:** Pangea Engenharia Ltda.  
**Versão da Especificação:** 1.0.0  
**Status:** Pronto para Implementação  

---

## 1. Contexto e Visão Geral

A **Pangea Engenharia Ltda.** é uma empresa de consultoria e projetos geotécnicos e estruturais sediada em Manaus/AM, especializada em fundações superficiais e profundas, estabilidade de encostas e taludes, contenções de grande porte e laudos técnicos periciais.

O ciclo comercial histórico opera sob propostas comerciais formais emitidas em PDF (padrão de numeração `PROP-XXXXA/AAAA`), contendo escopos detalhados, divisão estrita de responsabilidades entre contratada e contratante, valores fixos e irreajustáveis e cláusulas expressas de validade (15 a 30 dias). O início do prazo de execução (geralmente entre 10 e 30 dias) é estritamente condicionado ao recebimento e validação de insumos técnicos externos fornecidos pelo cliente (furos de sondagem SPT segundo a NBR 6484, plantas de carga com esforços axiais, horizontais e momentos, implantação vertical e projetos em formato `*.dwg`).

### 1.1 Objetivo do Novo Módulo
Implementar uma esteira comercial digital ponta a ponta dentro do ERPangea que permita:
1. Parametrizar e emitir propostas comerciais técnicas com envio de e-mails transacionais e link de aceite eletrônico com valor legal.
2. Converter automaticamente propostas aceitas em minutas contratuais customizáveis, preservando integridade de valores, escopo e cláusulas de responsabilidade.
3. Controlar o fluxo de pré-requisitos e dependências para disparar a *mise en service* (entrada em serviço/abertura de Ordem de Serviço de Engenharia) somente após a homologação de insumos técnicos obrigatórios e geração da ART junto ao CREA-AM.

---

## 2. Análise dos Módulos Atuais e Arquitetura de Integração

O ERPangea já possui três módulos operacionais ativos. O novo módulo (`Módulo Comercial e Contratos`) atuará como o ponto de entrada da esteira de negócios da empresa.

```
       ┌────────────────────────────────────────────────────────┐
       │     NOVO: Módulo Comercial & Contratos (MOD-COM-CTR)   │
       │  [Propostas] ──► [Aceite Online] ──► [Minuta/Contrato] │
       └───────────────────────────┬────────────────────────────┘
                                   │
         ┌─────────────────────────┼────────────────────────┐
         ▼                         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Módulo Finanças │     │ Módulo Projetos  │     │  Módulo Clientes │
│  (Faturamento e  │     │  & Engenharia    │     │  & Stakeholders  │
│    Medições)     │     │ (Ordem Serviço)  │     │     (CRM/Base)   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

### 2.1 Módulos Atualmente em Funcionamento
* **Módulo de Clientes e Contatos (Base Cadastral):** Armazena dados cadastrais de clientes corporativos (ex.: construtoras, incorporadoras, condomínios) com CNPJ, contatos técnicos e financeiros.
* **Módulo de Finanças e Medições:** Controla o contas a receber, faturamento por medição e emissão de notas fiscais vinculadas a centros de custos específicos por obra.
* **Módulo de Projetos e Engenharia:** Gerencia tarefas de desenho técnico em CAD, relatórios de cálculo estrutural, memoriais geotécnicos e acompanhamento de cronogramas.

### 2.2 Pontos de Integração com o Novo Módulo
* **Com o Módulo de Clientes:** O novo módulo consulta o cadastro existente e registra novos contatos (coordenadores de projetos e diretores técnicos) durante a criação da proposta.
* **Com o Módulo de Finanças:** Ao ocorrer o aceite da proposta e assinatura do contrato, o plano financeiro (ex.: *50% no aceite / 50% na entrega final* ou *medições mensais*) é automaticamente injetado como títulos provisionados no contas a receber, amarrados ao centro de custo da obra.
* **Com o Módulo de Projetos (Mise en Service):** A Ordem de Serviço (OS) do projeto só transita de `Pendente de Insumos` para `Em Execução` após a aprovação do checklist de documentos da contratante (arquivos `*.dwg`, sondagens SPT, plantas de carga). A data dessa aprovação define o marco zero ($D_0$) do cronograma.

---

## 3. Requisitos Funcionais (RF)

### RF-01: Cadastro e Parametrização da Proposta
* **RF-01.1:** O sistema deve gerar automaticamente o número sequencial da proposta no padrão `PROP-[Sequencial][Sufixo]/[Ano]` (ex.: `PROP-1685A/2026`).
* **RF-01.2:** Deve permitir selecionar o tipo de serviço através de templates técnicos pré-configurados:
  * Escolha e dimensionamento de fundações superficiais/profundas e radier (conforme NBR 6122 e NBR 6118);
  * Parecer técnico e análise de estabilidade de encostas e taludes (conforme NBR 11682);
  * Projetos geotécnicos e estruturais de contenções de divisa;
  * Consultoria técnica e visitas periciais em obra.
* **RF-01.3:** O operador deve selecionar os itens de responsabilidade da contratante obrigatórios para o escopo (ex.: sondagens SPT segundo NBR 6484, plantas de carga com momentos e cargas axiais/horizontais, arquivos `*.dwg` de arquitetura e terraplenagem).
* **RF-01.4:** O sistema deve suportar a definição de preços por valor global ou por itens (ex.: valor segregado para fundações e contenções), registrando a cláusula de preço fixo e irreajustável.
* **RF-01.5:** Configuração da vigência da proposta (padrão de 15 ou 30 dias corridos).

### RF-02: Mecanismo de Disparo por E-mail e Aceite Eletrônico
* **RF-02.1:** Geração dinâmica do PDF formal da proposta (layout institucional Pangea) assinado digitalmente pelo consultor técnico responsável.
* **RF-02.2:** Envio automático via e-mail transacional (SMTP/API) com texto de apresentação formal e botão de acesso via token seguro criptografado (HTTPS).
* **RF-02.3:** Página de visualização responsiva com três opções para o cliente:
  * **Aceitar Proposta:** Exige preenchimento de nome completo, CPF/CNPJ, cargo e validação por token OTP (enviado por e-mail ou SMS) ou aceite eletrônico qualificado (registrando IP, navegador, timestamp e hash do documento);
  * **Solicitar Revisão:** Campo aberto para feedback e contraproposta que reabre a proposta para edição interna no ERP;
  * **Recusar Proposta:** Encerra o ciclo e exige seleção do motivo da recusa.
* **RF-02.4:** Bloqueio automático de aceite caso a data atual ultrapasse o prazo de validade estipulado.

### RF-03: Geração e Edição da Minuta Contratual
* **RF-03.1:** No momento exato do aceite, o ERP deve instanciar uma minuta contratual baseada nos parâmetros da proposta sem necessidade de redigitação.
* **RF-03.2:** Cláusulas contratuais automáticas:
  * Objeto e escopo técnico detalhado com normas ABNT aplicáveis;
  * Condição suspensiva de prazo: cláusula expressa determinando que os prazos de entrega (10 a 30 dias) contam a partir da entrega integral dos insumos da contratante;
  * Forma de faturamento e penalidades por inadimplência;
  * Responsabilidade da Pangea pelo registro da ART no CREA-AM;
  * Foro da Comarca de Manaus/AM.
* **RF-03.3:** Editor de minuta no ERP com controle de versão e marcação de alterações (*redlining*) para revisões jurídicas e inserção de cláusulas específicas do cliente antes do envio final.
* **RF-03.4:** Integração com motor de assinatura digital (e-mail/DFe) para coleta de assinaturas dos representantes legais de ambas as partes.

### RF-04: Checklist de Insumos e Gatilho de *Mise en Service*
* **RF-04.1:** Repositório seguro para recebimento e versionamento dos arquivos enviados pelo cliente (`*.dwg`, `*.pdf`, `*.xlsx`).
* **RF-04.2:** Painel de aprovação técnica: o engenheiro geotécnico deve validar a conformidade dos furos de sondagem (SPT) e plantas de carga.
* **RF-04.3:** O botão e gatilho de *Mise en Service* (abertura formal de execução do projeto) só é liberado quando:
  1. Contrato estiver assinado;
  2. Todos os insumos obrigatórios estiverem com status `Aprovado pelo Responsável Técnico`;
  3. Comprovante de abertura de ART no CREA-AM estiver anexado ou agendado.
* **RF-04.4:** Disparo automático do cálculo do cronograma: Data Final = $D_0$ + Prazo Contratual em dias corridos.

---

## 4. Requisitos Não Funcionais (RNF)

* **RNF-01 (Segurança e Validade Jurídica):** O mecanismo de aceite eletrônico e assinatura deve cumprir os requisitos da Medida Provisória nº 2.200-2/2001 e da Lei nº 14.063/2020, gerando um Manifesto de Conformidade com hash SHA-256 e trilha de auditoria completa.
* **RNF-02 (Desempenho):** O tempo de renderização do PDF da proposta e da minuta contratual não deve exceder 3 segundos.
* **RNF-03 (Disponibilidade e Acesso):** O portal de aceite deve operar com índice de disponibilidade de 99,8% e funcionar em dispositivos móveis e desktops.
* **RNF-04 (Auditoria e Logs):** Todos os eventos (emissão, envio de e-mail, abertura do link, aceite, reprovação e alterações na minuta) devem ser registrados em tabela de logs imutável.
* **RNF-05 (Conformidade com a LGPD):** Anonimização e proteção de dados cadastrais sensíveis dos signatários conforme a Lei nº 13.709/2018.

---

## 5. Modelo de Dados Relacional (Esquema Conceitual)

```
┌─────────────────────────┐       ┌─────────────────────────┐
│     commercial_proposal │       │    proposal_scope_item  │
├─────────────────────────┤       ├─────────────────────────┤
│ id (PK)                 │1     N│ id (PK)                 │
│ proposal_code (UNIQUE)  ├───────┤ proposal_id (FK)        │
│ client_id (FK)          │       │ service_type            │
│ project_name            │       │ nbr_references          │
│ total_value             │       │ subtotal_value          │
│ payment_terms_type      │       └─────────────────────────┘
│ validity_days           │
│ status                  │       ┌─────────────────────────┐
│ expires_at              │       │    proposal_input_req   │
│ accepted_at             │1     N├─────────────────────────┤
│ acceptance_ip           ├───────┤ id (PK)                 │
│ acceptance_hash         │       │ proposal_id (FK)        │
└────────────┬────────────┘       │ required_item_type      │
             │1                   │ description             │
             │                    │ status (PENDING/OK)     │
             │1                   └─────────────────────────┘
┌────────────┴────────────┐
│      legal_contract     │       ┌─────────────────────────┐
├─────────────────────────┤1     N│    contract_milestone   │
│ id (PK)                 ├───────┤ (Mise en Service)       │
│ proposal_id (FK)        │       ├─────────────────────────┤
│ contract_code (UNIQUE)  │       │ id (PK)                 │
│ contract_html_body      │       │ contract_id (FK)        │
│ status                  │       │ trigger_date (D0)       │
│ crea_art_number         │       │ lead_time_days          │
│ crea_art_status         │       │ deadline_date           │
│ signed_pdf_url          │       │ technical_manager_id    │
└─────────────────────────┘       └─────────────────────────┘
```

---

## 6. Roadmap de Implementação

O desenvolvimento e implantação são estruturados em 4 sprints quinzenais:

```
[ Sprint 1: Modelagem e Proposta Digital ] ──► (Semanas 1-2)
                     │
[ Sprint 2: Motor de Aceite e E-mail ]     ──► (Semanas 3-4)
                     │
[ Sprint 3: Automação Contratual ]         ──► (Semanas 5-6)
                     │
[ Sprint 4: Insumos, ART e Mise en Service]──► (Semanas 7-8)
```

### Sprint 1: Parametrização Comercial e Motor de Propostas (Dias 1 a 15)
* Implementação das tabelas `commercial_proposal`, `proposal_scope_item` e `proposal_input_req`.
* Criação da interface de elaboração de propostas no ERPangea com cadastro de normas ABNT e matriz de responsabilidades.
* Geração do layout de proposta em PDF/A de alta fidelidade visual.

### Sprint 2: Notificações Transacionais e Portal de Aceite (Dias 16 a 30)
* Configuração do serviço de envio de e-mails transacionais com links de segurança tokenizados.
* Desenvolvimento da landing page pública responsiva para visualização e aceite eletrônico.
* Implementação dos registros de auditoria (IP, user agent, geolocalização e carimbo de tempo).

### Sprint 3: Conversão e Gestor de Contratos (Dias 31 a 45)
* Criação do gerador automático de minutas contratuais vinculadas à proposta aceita.
* Implementação do editor web de cláusulas com salvamento de versões e histórico de revisões.
* Integração com serviço de assinatura digital e emissão do contrato final assinado.

### Sprint 4: Entrada em Serviço (*Mise en Service*) e Testes Integrados (Dias 46 a 60)
* Desenvolvimento da aba de upload e homologação de insumos técnicos (sondagens SPT, projetos em CAD `*.dwg` e plantas de carga).
* Implementação da trava lógica de disparo do cronograma ($D_0$) e vínculo do número da ART no CREA-AM.
* Testes de ponta a ponta (Homologação) com propostas piloto e treinamento das equipes técnica, financeira e comercial.

---

## 7. Desafios Previstos e Estratégias de Mitigação

| Desafio Identificado | Causa Raiz | Solução Técnica / Operacional Implementada |
| :--- | :--- | :--- |
| **Insumos técnicos entregues fora do padrão normativo** | Cliente fornece sondagens incompletas ou plantas sem cargas completas. | O ERP implementa checklist técnico obrigatório: o projeto não muda para *Em Execução* sem o parecer "Aprovado" do consultor geotécnico. Notificação automática de inconformidade disparada ao cliente. |
| **Divergência entre data de assinatura e início real dos trabalhos** | Clientes assumem que o prazo corre a partir do contrato assinado, mesmo sem entregar os projetos em DWG. | Cláusula contratual padrão parametrizada: "O prazo de $X$ dias inicia a partir da data de upload e validação do último documento listado no Anexo de Insumos". O ERP envia e-mail formalizando a data $D_0$. |
| **Tentativa de aceite em propostas com validade expirada** | Demora interna na diretoria do cliente ultrapassando 15 ou 30 dias. | A landing page bloqueia o botão de aceite após a expiração e exibe botão "Solicitar Revalidação Comercial", notificando o gestor da Pangea no ERP. |
| **Resistência do cliente à assinatura da minuta gerada** | Grandes incorporadoras com departamento jurídico próprio exigem minuta própria. | O módulo permite alternar entre "Minuta Padrão ERP" e "Contrato Externo (Minuta do Cliente)", permitindo upload do PDF externo sem romper o vínculo com o escopo e orçamento aprovados. |

---

## 8. Critérios de Homologação e Aceite da Entrega

1. **Geração de Proposta:** Criação com sucesso de uma proposta modelo completa para fundações e contenções em menos de 5 minutos, gerando o PDF padronizado com normas ABNT.
2. **Disparo e Aceite:** Envio de e-mail ao cliente de teste, abertura em smartphone/desktop e validação do aceite eletrônico com geração imediata do relatório de auditoria e hash criptográfico.
3. **Migração de Dados:** 100% dos dados da proposta (razão social, CNPJ, valor, forma de parcelamento, escopo e responsabilidades) migrados para a minuta contratual sem distorções.
4. **Governança da Entrada em Serviço:** O sistema deve impedir categoricamente o avanço do cronograma de engenharia até que os arquivos `*.dwg`, laudos de sondagem SPT e a indicação da ART estejam validados e registrados.