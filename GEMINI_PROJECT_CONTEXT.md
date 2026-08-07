# GEMINIPROJECTCONTEXT.md

Documento de contexto e governança para o agente de codificação Gemini Flash 3.6

Projeto: ERP para escritório de engenharia civil

Tecnologias principais: Python, Django, PostgreSQL e Tailwind CSS

Responsável pelo projeto: Harold

Status: Documento vivo — deve ser atualizado continuamente

Última revisão: 06/08/2026

Versão: 1.0.0

# 1. Finalidade do documento

Este arquivo fornece ao agente de codificação Gemini Flash 3.6 o contexto necessário para contribuir com o desenvolvimento do ERP de forma consistente, segura e alinhada aos objetivos do projeto.

O documento deve ser consultado antes de:

- criar ou alterar funcionalidades;

- modificar modelos de dados;

- alterar regras de negócio;

- criar migrações;

- desenvolver telas;

- implementar integrações;

- sugerir mudanças arquiteturais;

- corrigir erros;

- escrever testes;

- refatorar código.

O agente deve considerar este arquivo como uma fonte principal de contexto, juntamente com:

- código existente;

- documentação técnica;

- decisões arquiteturais registradas;

- requisitos aprovados;

- testes automatizados;

- histórico de tarefas e alterações.

Regra fundamental: o agente não deve presumir que uma funcionalidade existe, que uma regra foi aprovada ou que uma decisão arquitetural pode ser alterada. Em caso de dúvida, deve registrar a incerteza e propor uma solução antes de modificar o comportamento do sistema.

# 2. Visão geral do projeto

O projeto consiste no desenvolvimento de um ERP web interno para um escritório de engenharia civil que atua nas seguintes áreas:

- projetos e consultoria em geotecnia;

- projetos de fundação;

- soluções de contenção;

- muros de arrimo;

- obras de terra;

- estruturas;

- pavimentação;

- consultoria técnica.

O sistema deverá centralizar os processos comerciais, operacionais, documentais e financeiros do escritório.

O fluxo principal do sistema será:

Contato “

Lead “ Proposta “ Contrato “ Projeto “ Entrega “ Medição “ Faturamento “ Pagamento

# 3. Objetivos do sistema

## 3.1. Objetivo principal

Criar uma plataforma web interna para organizar as operações do escritório, reduzir controles dispersos em planilhas e aumentar a visibilidade sobre:

- oportunidades comerciais;

- propostas;

- contratos;

- projetos;

- documentos;

- prazos;

- medições;

- faturamento;

- recebimentos;

- responsabilidades da equipe.

## 3.2. Objetivos específicos

1. Centralizar os dados de clientes, fornecedores e parceiros.

2. Permitir o acompanhamento de leads e propostas.

3. Controlar contratos e suas condições comerciais.

4. Acompanhar projetos, tarefas, prazos e responsáveis.

5. Organizar documentos técnicos e administrativos.

6. Controlar revisões e aprovações documentais.

7. Registrar entregas e medições.

8. Relacionar medições a faturamentos e pagamentos.

9. Disponibilizar indicadores gerenciais.

10. Reduzir retrabalho e perda de informações.

11. Garantir rastreabilidade das alterações importantes.

12. Usar inteligência artificial como apoio, sem substituir a validação humana.

13. Manter uma base preparada para futuras integrações.

# 4. Princípios do projeto

## 4.1. Simplicidade antes da complexidade

A solução deve ser simples o suficiente para ser mantida por uma equipe pequena.

Priorizar:

- monólito modular Django;

- modelos claros;

- serviços de domínio;

- formulários objetivos;

- consultas eficientes;

- componentes reutilizáveis;

- poucas dependências externas.

Não introduzir microsserviços, filas, eventos ou integrações complexas sem justificativa concreta.

## 4.2. Modularidade

Cada domínio deve permanecer separado:

accounts contacts commercial projects documents measurements billing dashboard audit core

Alterações em um módulo não devem quebrar outros módulos sem que isso seja identificado e testado.

## 4.3. Regras de negócio no backend

Regras importantes não devem existir somente nos templates ou em JavaScript.

O backend deve validar:

- permissões;

- transições de status;

- valores;

- relacionamentos;

- obrigatoriedade de campos;

- limites contratuais;

- aprovação de documentos;

- autorização para exclusão ou cancelamento.

## 4.4. Rastreabilidade

Toda ação crítica deve ser auditável.

Devem ser registrados, quando aplicável:

- usuário;

- data e hora;

- objeto alterado;

- ação executada;

- valor anterior;

- valor posterior;

- justificativa;

- origem da ação.

## 4.5. Segurança por padrão

O agente deve tratar dados comerciais, financeiros, pessoais e técnicos como informações potencialmente sensíveis.

Nunca deve:

- expor credenciais;

- inserir chaves de API no código;

- imprimir dados sensíveis em logs;

- desativar proteção CSRF sem justificativa;

- permitir acesso somente porque um botão foi ocultado;

- ignorar validação de uploads;

- conceder permissões amplas para facilitar testes.

## 4.6. Evolução incremental

Cada alteração deve ser pequena, testável e reversível.

Preferir:

Uma tarefa “ Uma implementação “ Testes “ Revisão “ Integração

Evitar alterações que misturem, sem necessidade:

- nova funcionalidade;

- grande refatoração;

- alteração visual;

- mudança no banco;

- nova integração externa.

# 5. Escopo funcional

# 5.1. Módulo de usuários

## Funcionalidades

- login;

- logout;

- recuperação de senha;

- alteração de senha;

- ativação e desativação de usuários;

- controle de permissões;

- registro do último acesso;

- associação a projetos;

- definição de perfil.

## Perfis básicos

### Administrador

Pode:

- gerenciar usuários;

- configurar permissões;

- acessar todos os módulos;

- visualizar dados financeiros;

- consultar auditoria;

- alterar configurações;

- administrar documentos e arquivos.

### Gerente

Pode:

- acompanhar projetos;

- criar e aprovar propostas;

- acompanhar contratos;

- aprovar medições;

- consultar relatórios gerenciais;

- atribuir responsáveis;

- visualizar informações financeiras autorizadas.

### Colaborador

Pode:

- consultar projetos permitidos;

- registrar atividades;

- anexar documentos;

- atualizar tarefas;

- registrar entregas;

- consultar contatos relacionados.

O colaborador não deve acessar dados financeiros sensíveis sem permissão explícita.

# 5.2. Dashboard

O dashboard deverá apresentar indicadores objetivos.

## Indicadores comerciais

- leads abertos;

- propostas em elaboração;

- propostas enviadas;

- propostas vencidas;

- propostas aprovadas;

- taxa de conversão;

- valor potencial do pipeline;

- valor contratado.

## Indicadores operacionais

- projetos em andamento;

- projetos atrasados;

- projetos próximos do vencimento;

- projetos por responsável;

- projetos por tipo de serviço;

- tarefas pendentes;

- entregas aguardando aprovação.

## Indicadores financeiros

- valor faturado;

- valores a receber;

- pagamentos em atraso;

- medições aprovadas não faturadas;

- receita por projeto;

- receita por cliente.

Cada indicador deve possuir uma regra de cálculo documentada.

Exemplos:

- Projeto em andamento: projeto com status EM_ANDAMENTO;

- Proposta enviada: proposta com status ENVIADA ou EM_NEGOCIACAO;

- Contrato fechado: contrato com status ASSINADO ou ATIVO;

- Projeto atrasado: prazo final vencido e status diferente de CONCLUIDO.

# 5.3. Módulo de contatos

O sistema deve permitir cadastrar:

- clientes;

- fornecedores;

- parceiros;

- órgãos públicos;

- profissionais;

- subcontratados.

## Dados essenciais

- nome ou razão social;

- nome fantasia;

- CPF ou CNPJ;

- tipo de pessoa;

- e-mail;

- telefone;

- endereço;

- cidade;

- estado;

- site;

- observações;

- situação ativa ou inativa.

## Histórico de interações

Cada interação pode conter:

- contato;

- usuário responsável;

- data;

- tipo;

- assunto;

- descrição;

- próxima ação;

- prazo da próxima ação;

- anexos.

O modelo deve permitir que um mesmo contato possua mais de uma função.

# 5.4. Módulo comercial

O fluxo comercial principal será:

Lead “ Oportunidade “ Proposta “ Contrato

## Lead

Informações esperadas:

- contato;

- origem;

- serviço de interesse;

- descrição;

- valor estimado;

- probabilidade;

- responsável;

- estágio;

- previsão de fechamento;

- observações.

Estágios sugeridos:

NOVO QUALIFICACAO CONTATO_REALIZADO PROPOSTA_EM_PREPARACAO CONVERTIDO PERDIDO

## Proposta

Informações esperadas:

- número;

- cliente;

- lead de origem;

- escopo;

- serviços incluídos;

- exclusões;

- premissas;

- prazo;

- validade;

- valor;

- condição de pagamento;

- responsável técnico;

- responsável comercial;

- versão;

- status.

Status sugeridos:

RASCUNHO EM_REVISAO ENVIADA EM_NEGOCIACAO APROVADA RECUSADA EXPIRADA CANCELADA

## Contrato

Informações esperadas:

- número;

- cliente;

- proposta de origem;

- projeto relacionado;

- datas;

- valor;

- condições de pagamento;

- índice de reajuste;

- status;

- arquivo;

- responsável;

- observações.

Status sugeridos:

EM_ELABORACAO EM_REVISAO AGUARDANDO_ASSINATURA ASSINADO

ATIVO SUSPENSO ENCERRADO RESCINDIDO

As propostas devem possuir versionamento. Uma alteração relevante não deve apagar a versão anterior.

# 5.5. Módulo de projetos

O projeto é o núcleo operacional do sistema.

## Dados principais

- código;

- nome;

- cliente;

- contrato;

- tipo de serviço;

- descrição;

- responsável técnico;

- gerente;

- equipe;

- endereço da obra;

- município;

- data de início;

- prazo contratado;

- prazo planejado;

- prazo revisado;

- data de conclusão;

- status;

- prioridade;

- percentual concluído;

- orçamento;

- observações.

## Tipos de serviço

- geotecnia;

- fundações;

- contenções;

- muros de arrimo;

- obras de terra;

- estruturas;

- pavimentação;

- consultoria;

- outros.

## Status

PLANEJAMENTO AGUARDANDO_INICIO EM_ANDAMENTO AGUARDANDO_CLIENTE EM_PAUSA EM_REVISAO CONCLUIDO CANCELADO

## Componentes do projeto

- equipe;

- tarefas;

- marcos;

- entregas;

- atividades;

- documentos;

- pendências;

- riscos;

- medições;

- histórico de alterações.

## Regras relevantes

- projeto deve possuir cliente;

- projeto deve possuir responsável;

- projeto concluído deve possuir data de conclusão;

- alteração de prazo deve registrar justificativa;

- projeto cancelado deve possuir motivo;

- projeto em pausa deve possuir justificativa;

- documentos restritos só podem ser acessados por usuários autorizados.

# 5.6. Módulo de documentação

O módulo deve organizar documentos administrativos e técnicos.

## Tipos de documentos

- ART;

- contrato;

- proposta;

- relatório;

- memorial de cálculo;

- memorial descritivo;

- planta;

- sondagem;

- laudo;

- orçamento;

- cronograma;

- medição;

- nota fiscal;

- ata;

- comunicação;

- documento recebido do cliente.

## Requisitos

- upload seguro;

- categorização;

- associação a projeto;

- controle de versão;

- revisão;

- aprovação;

- arquivamento;

- controle de acesso;

- histórico de downloads;

- registro de autor e responsável pela revisão.

Documentos aprovados não devem ser sobrescritos. Uma alteração deve criar nova revisão.

## Informações específicas de ART

Quando aplicável, armazenar:

- número;

- tipo;

- profissional responsável;

- órgão ou conselho;

- data;

- situação;

- arquivo;

- observações.

O sistema não deve declarar que uma ART é juridicamente válida apenas porque foi anexada.

# 5.7. Módulo de medição

A medição deve estar relacionada a:

- contrato;

- projeto;

- entrega;

- período;

- itens executados;

- valor;

- aprovação;

- faturamento.

## Regras

- medição não pode ultrapassar o valor contratado;

- medição rejeitada exige justificativa;

- medição aprovada não deve ser editada sem controle;

- percentual acumulado deve ser calculado;

- medição aprovada pode originar faturamento;

- modificações devem ser auditadas.

## Status

RASCUNHO EM_ELABORACAO ENVIADA EM_ANALISE APROVADA REJEITADA FATURADA CANCELADA

# 5.8. Módulo de faturamento

O módulo deverá controlar:

- valores previstos;

- valores faturados;

- parcelas;

- vencimentos;

- pagamentos;

- atrasos;

- comprovantes;

- relatórios.

## Status financeiros

PREVISTO AGUARDANDO_FATURAMENTO FATURADO EM_ABERTO PAGO PAGO_PARCIALMENTE VENCIDO CANCELADO

A primeira versão deve funcionar como controle financeiro interno. Integrações fiscais e bancárias devem ser planejadas separadamente.

## Relatórios

- contas a receber;

- pagamentos vencidos;

- faturamento por período;

- faturamento por cliente;

- faturamento por projeto;

- previsão de recebimento;

- valores contratados versus recebidos;

- medições aprovadas ainda não faturadas;

- rentabilidade estimada por projeto.

# 6. Arquitetura técnica

# 6.1. Stack

- Python;

- Django;

- PostgreSQL;

- Django Templates;

- Tailwind CSS;

- Redis, quando necessário;

- Celery, quando houver tarefas assíncronas;

- Docker;

- pytest ou Django Test Framework;

- Gemini Flash 3.6 por meio de um serviço desacoplado.

A disponibilidade e o identificador oficial do modelo utilizado na API devem ser confirmados na documentação atual do provedor. O código não deve espalhar o nome do modelo por todo o sistema.

# 6.2. Estrutura sugerida

erp_engenharia/ config/ settings/ base.py development.py production.py testing.py urls.py asgi.py wsgi.py apps/ accounts/ dashboard/ contacts/ commercial/ projects/ documents/ measurements/ billing/ audit/ ai_assistant/ core/ templates/ static/

media/ tests/ requirements/ Dockerfile docker-compose.yml manage.py GEMINI_PROJECT_CONTEXT.md

# 6.3. Organização interna dos aplicativos

Cada aplicativo deve preferencialmente possuir:

app/ admin.py apps.py forms.py models.py urls.py views.py services.py selectors.py permissions.py validators.py templates/ tests/ migrations/

## Responsabilidades dos arquivos

- models.py: persistência e invariantes simples;

- forms.py: validação de entrada;

- services.py: operações de negócio;

- selectors.py: consultas reutilizáveis;

- permissions.py: regras de autorização;

- validators.py: validações específicas;

- views.py: coordenação da requisição;

- tests/: testes unitários e de integração.

# 7. Diretrizes para o agente Gemini

# 7.1. Antes de codificar

O agente deve:

1. Ler este arquivo.

2. Inspecionar a estrutura atual do projeto.

3. Verificar os modelos relacionados.

4. Procurar funcionalidades semelhantes já existentes.

5. Identificar migrações pendentes.

6. Consultar testes existentes.

7. Verificar regras de permissão.

8. Avaliar possíveis impactos em outros módulos.

9. Declarar as premissas utilizadas.

10. Apresentar um plano curto antes de alterações complexas.

# 7.2. Durante a implementação

O agente deve:

- alterar somente o necessário;

- preservar compatibilidade;

- respeitar os padrões existentes;

- usar nomes claros;

- escrever testes;

- incluir validações de backend;

- atualizar a documentação;

- criar migrações quando modelos forem alterados;

- evitar duplicação;

- manter transações atômicas em operações financeiras;

- tratar erros de forma explícita;

- não modificar configurações de produção sem autorização.

# 7.3. Depois da implementação

O agente deve:

- executar testes;

- verificar lint e formatação;

- revisar permissões;

- verificar consultas N+1;

- revisar mensagens de erro;

- testar casos de sucesso e falha;

- conferir migrações;

- informar arquivos alterados;

- informar riscos conhecidos;

- atualizar o status deste documento.

# 7.4. Formato das entregas

Toda tarefa concluída deve ser apresentada com:

Resumo:

- O que foi implementado.

Arquivos alterados:

- Lista dos arquivos.

Banco de dados:

- Migrações criadas ou não necessárias.

Regras de negócio:

- Regras adicionadas ou alteradas.

Testes:

- Testes criados ou executados.

Segurança:

- Impactos em permissões, dados ou uploads.

Riscos:

- Limitações ou pontos pendentes.

Próximos passos:

- Tarefas recomendadas.

# 8. Uso da inteligência artificial

# 8.1. Princípio geral

A inteligência artificial deve apoiar o desenvolvimento e a operação, mas não substituir:

- análise técnica de engenharia;

- aprovação profissional;

- validação jurídica;

- aprovação financeira;

- revisão de segurança;

- decisão de negócio.

# 8.2. Casos de uso permitidos

O agente pode auxiliar em:

- geração de código;

- criação de testes;

- documentação;

- resumo de reuniões;

- classificação de documentos;

- extração de metadados;

- sugestão de tarefas;

- identificação de informações ausentes;

- comparação entre versões;

- criação de rascunhos;

- análise preliminar de riscos.

# 8.3. Casos que exigem revisão humana

Toda saída relacionada a:

- valores;

- contratos;

- documentos técnicos;

- ART;

- normas;

- prazos contratuais;

- medições;

- pagamentos;

- dados pessoais;

- permissões;

- decisões de engenharia;

deve ser revisada por uma pessoa autorizada.

# 8.4. Dados proibidos ou restritos

Não enviar para serviços externos sem autorização:

- senhas;

- tokens;

- chaves privadas;

- dados bancários;

- documentos pessoais desnecessários;

- informações protegidas de clientes;

- dados técnicos confidenciais;

- arquivos integrais quando um resumo anonimizado for suficiente.

# 9. Cronograma de desenvolvimento

# Fase 0 — Preparação

## Objetivos

- validar escopo;

- configurar repositório;

- definir ambiente;

- criar convenções;

- preparar banco;

- configurar integração contínua;

- criar este documento.

## Entregáveis

- repositório inicial;

- ambiente de desenvolvimento;

- configuração Docker;

- projeto Django;

- banco configurado;

- documentação de execução;

- primeira versão do contexto do agente.

# Fase 1 — Fundação técnica

## Objetivos

- criar usuário personalizado;

- implementar autenticação;

- criar perfis;

- criar permissões;

- definir layout base;

- criar auditoria inicial.

## Critérios de conclusão

- login e logout funcionando;

- permissões testadas;

- usuário inativo bloqueado;

- layout base aplicado;

- ações importantes registradas.

# Fase 2 — Contatos

## Objetivos

- cadastrar contatos;

- cadastrar pessoas de contato;

- classificar papéis;

- registrar interações;

- pesquisar e filtrar.

## Critérios de conclusão

- contatos podem ser criados, editados e arquivados;

- contatos podem possuir múltiplas funções;

- histórico de interações está disponível;

- permissões estão aplicadas;

- testes principais foram criados.

# Fase 3 — Comercial

## Objetivos

- implementar leads;

- implementar propostas;

- criar versionamento;

- implementar contratos;

- criar fluxo de status;

- gerar documentos comerciais básicos.

## Critérios de conclusão

- lead pode originar proposta;

- proposta pode originar contrato;

- transições inválidas são bloqueadas;

- versões anteriores são preservadas;

- dados comerciais podem ser consultados no dashboard.

# Fase 4 — Projetos

## Objetivos

- implementar projetos;

- cadastrar equipe;

- criar tarefas;

- criar marcos;

- acompanhar prazos;

- registrar atividades;

- relacionar contrato e projeto.

## Critérios de conclusão

- projeto possui cliente e responsável;

- tarefas podem ser atribuídas;

- prazos atrasados são identificados;

- equipe possui acesso controlado;

- dashboard operacional apresenta informações básicas.

# Fase 5 — Documentação

## Objetivos

- implementar upload;

- categorizar arquivos;

- criar revisões;

- implementar aprovação;

- controlar permissões;

- cadastrar ARTs.

## Critérios de conclusão

- uploads inválidos são rejeitados;

- versões anteriores são preservadas;

- documentos aprovados não são sobrescritos;

- downloads são auditados;

- acesso é limitado ao projeto e ao perfil.

# Fase 6 — Medições

## Objetivos

- criar medições;

- cadastrar itens;

- relacionar entregas;

- implementar fluxo de aprovação;

- calcular valores acumulados.

## Critérios de conclusão

- valor medido não excede contrato;

- medição rejeitada exige justificativa;

- medição aprovada pode ser faturada;

- alterações críticas são auditadas.

# Fase 7 — Faturamento

## Objetivos

- criar contas a receber;

- criar parcelas;

- registrar pagamentos;

- controlar vencimentos;

- gerar relatórios.

## Critérios de conclusão

- pagamentos parciais são suportados;

- vencimentos são identificados;

- faturamento pode ser relacionado à medição;

- relatórios apresentam valores consistentes;

- operações financeiras usam transações seguras.

# Fase 8 — IA e automações

## Objetivos

- criar serviço de integração;

- resumir documentos;

- classificar informações;

- sugerir tarefas;

- auxiliar propostas;

- criar registros de auditoria da IA.

## Critérios de conclusão

- integração isolada em módulo próprio;

- falha da IA não interrompe o ERP;

- respostas são validadas;

- usuário sabe quando o conteúdo foi gerado por IA;

- dados enviados seguem regras de privacidade;

- ações automatizadas exigem revisão quando necessário.

# 10. Responsabilidades

## 10.1. Harold — proprietário do produto

Responsável por:

- definir prioridades;

- validar requisitos;

- aprovar fluxos;

- fornecer regras do negócio;

- validar protótipos;

- aprovar mudanças de escopo;

- indicar responsáveis técnicos;

- aceitar ou rejeitar entregas.

## 10.2. Agente Gemini

Responsável por:

- analisar o contexto;

- propor soluções;

- gerar código;

- criar testes;

- identificar riscos;

- documentar alterações;

- manter consistência arquitetural;

- não tomar decisões irreversíveis sem aprovação;

- sinalizar ambiguidades;

- evitar invenções sobre funcionalidades existentes.

## 10.3. Responsável técnico de engenharia

Responsável por validar:

- dados técnicos;

- documentos de engenharia;

- ART;

- escopos;

- entregáveis;

- marcos;

- terminologia profissional;

- regras específicas dos serviços prestados.

## 10.4. Responsável financeiro

Responsável por validar:

- condições de pagamento;

- parcelas;

- medições;

- faturamentos;

- recebimentos;

- relatórios;

- regras de cancelamento;

- integrações financeiras.

## 10.5. Responsável por segurança e dados

Responsável por validar:

- acessos;

- permissões;

- tratamento de dados pessoais;

- armazenamento de documentos;

- backups;

- logs;

- integrações externas;

- políticas de retenção.

# 11. Plano de comunicação

## 11.1. Registro central de decisões

Toda decisão importante deve ser registrada em arquivos como:

docs/decisions/ ADR-0001-arquitetura-monolito-modular.md ADR-0002-modelo-de-permissoes.md ADR-0003-armazenamento-de-documentos.md ADR-0004-integracao-com-ia.md

Cada decisão deve conter:

- contexto;

- problema;

- alternativas;

- decisão;

- consequências;

- data;

- responsável.

## 11.2. Registro de tarefas

As tarefas devem possuir:

- identificador;

- título;

- módulo;

- prioridade;

- descrição;

- critérios de aceitação;

- dependências;

- status;

- responsável;

- data de criação;

- data de conclusão;

- observações.

## Status permitidos

BACKLOG PLANEJADA EM_DESENVOLVIMENTO EM_REVISAO BLOQUEADA CONCLUIDA CANCELADA

## 11.3. Comunicação de progresso

Cada atualização deve informar:

- progresso desde a última atualização;

- tarefas concluídas;

- tarefas em andamento;

- bloqueios;

- riscos;

- decisões pendentes;

- impacto no cronograma;

- próximos passos.

## 11.4. Comunicação de bloqueios

Um bloqueio deve ser comunicado imediatamente quando:

- faltar uma regra de negócio essencial;

- houver conflito entre requisitos;

- uma alteração puder quebrar dados existentes;

- houver risco de segurança;

- uma integração externa estiver indisponível;

- for necessário alterar o escopo;

- uma migração puder causar perda de dados.

O agente não deve resolver silenciosamente um bloqueio usando uma suposição permanente.

## 11.5. Comunicação de alterações de escopo

Toda solicitação fora do escopo atual deve ser classificada como:

- correção;

- melhoria;

- nova funcionalidade;

- refatoração;

- alteração arquitetural;

- débito técnico;

- mudança de segurança.

A solicitação deve indicar:

- motivo;

- benefício;

- impacto;

- esforço estimado;

- riscos;

- efeito sobre o cronograma.

# 12. Mecanismo para evitar desvios de rota

Antes de implementar qualquer tarefa, o agente deve responder às seguintes perguntas:

1. Qual objetivo do projeto esta tarefa atende?

2. Qual módulo será afetado?

3. A tarefa está no escopo atual?

4. Quais entidades e regras são impactadas?

5. Há impacto em permissões?

6. Há impacto em dados existentes?

7. É necessário criar migração?

8. Há testes suficientes?

9. A tarefa cria dependência externa?

10. O resultado pode ser revertido?

11. Há alguma decisão que depende de Harold?

12. A documentação precisa ser atualizada?

Se a tarefa não estiver alinhada a um objetivo ou módulo definido, deve ser marcada como fora do escopo ou candidata à revisão do roadmap.

# 13. Definition of Ready

Uma tarefa somente deve começar quando possuir:

- descrição clara;

- objetivo;

- módulo identificado;

- critérios de aceitação;

- regra de negócio conhecida;

- prioridade;

- dependências identificadas;

- responsável pela validação;

- riscos conhecidos.

Tarefas incompletas devem permanecer em BACKLOG ou PLANEJADA.

# 14. Definition of Done

Uma tarefa só deve ser considerada concluída quando:

- código implementado;

- validações adicionadas;

- permissões verificadas;

- testes criados ou atualizados;

- migrações executadas, quando aplicável;

- interface revisada;

- mensagens de erro tratadas;

- documentação atualizada;

- lint e formatação executados;

- regressões verificadas;

- auditoria considerada;

- entrega descrita no relatório de progresso;

- critérios de aceitação atendidos.

# 15. Melhores práticas de desenvolvimento

## 15.1. Código

- usar nomes explícitos;

- seguir PEP 8;

- manter funções pequenas;

- evitar lógica complexa nas views;

- usar serviços para operações de negócio;

- evitar duplicação;

- documentar decisões não óbvias;

- não criar abstrações prematuras;

- preferir composição;

- manter dependências atualizadas com controle.

## 15.2. Django

- usar um modelo de usuário customizado;

- declarar related_name claros;

- criar índices para campos frequentemente pesquisados;

- usar select_related e prefetch_related;

- utilizar transaction.atomic() em operações críticas;

- aplicar permissões no backend;

- usar formulários e serializers para validar entradas;

- separar configurações por ambiente;

- não usar DEBUG=True em produção.

## 15.3. Banco de dados

- evitar exclusões físicas quando o histórico for importante;

- usar arquivamento ou desativação;

- criar restrições de integridade;

- usar DecimalField para valores monetários;

- nunca usar float para dinheiro;

- proteger migrações destrutivas;

- testar restauração de backups;

- documentar alterações de esquema.

## 15.4. Frontend

- usar componentes Tailwind consistentes;

- manter hierarquia visual clara;

- fornecer estados de carregamento;

- exibir mensagens de sucesso e erro;

- tornar tabelas filtráveis;

- manter formulários acessíveis;

- evitar JavaScript desnecessário;

- garantir uso adequado em telas menores.

## 15.5. Arquivos

- validar extensão;

- validar tamanho;

- gerar nomes únicos;

- armazenar arquivos fora da área pública;

- verificar permissões;

- evitar confiar no nome enviado pelo usuário;

- registrar uploads e downloads;

- manter backups independentes do banco.

## 15.6. Testes

Devem existir testes para:

- modelos;

- regras de negócio;

- permissões;

- transições de status;

- formulários;

- uploads;

- cálculos;

- medições;

- faturamento;

- views críticas;

- integração com IA usando mocks.

# 16. Estratégias para manter o foco

## 16.1. Trabalhar por fatias verticais

Em vez de construir todo o banco primeiro e toda a interface depois, entregar fluxos completos:

Cadastrar contato “ Criar lead “ Gerar proposta “ Criar contrato

Isso permite validar rapidamente o valor do sistema.

## 16.2. Priorizar o fluxo principal

O fluxo prioritário do MVP é:

Cliente ’ Proposta ’ Contrato ’ Projeto ’ Entrega ’ Medição ’ Faturamento

Funcionalidades que não apoiam esse fluxo devem receber prioridade menor, salvo necessidade operacional.

## 16.3. Controlar o débito técnico

Todo débito técnico deve ser registrado com:

- descrição;

- motivo;

- impacto;

- prioridade;

- risco;

- plano de correção.

## 16.4. Evitar expansão prematura

Não implementar inicialmente:

- aplicativo mobile;

- múltiplas empresas;

- microsserviços;

- integração bancária complexa;

- emissão fiscal completa;

- automações irreversíveis;

- IA para decisões técnicas;

- personalização extrema de relatórios.

## 16.5. Revisão periódica

A cada ciclo de desenvolvimento, revisar:

- objetivos;

- backlog;

- riscos;

- decisões;

- indicadores;

- feedback dos usuários;

- problemas recorrentes;

- alterações necessárias no roadmap.

# 17. Gestão de riscos

Risco Impacto Probabilidade Mitigação

Escopo crescer sem controle Alto Alta Usar backlog e aprovação de mudanças

Permissões inadequadas Alto Média Testes por perfil e auditoria

Perda de documentos Alto Média Backups e versionamento

Dados financeiros inconsistentes Alto Média DecimalField, transações e validações

Dependência excessiva da IA Alto Média Revisão humana e funcionamento sem IA

Consultas lentas Médio Média Índices, paginação e otimização ORM

Migrações destrutivas Alto Baixa Backup e revisão antes da execução

Dados sensíveis enviados à IA Alto Média Anonimização e política de privacidade

Falta de adoção pelos usuários Alto Média Interface simples e treinamento

Regras de negócio ambíguas Médio Alta Critérios de aceitação e decisões registradas

# 18. Segurança, privacidade e LGPD

O sistema deve seguir boas práticas de proteção de dados pessoais.

## Requisitos

- coletar somente os dados necessários;

- documentar a finalidade do tratamento;

- controlar acesso por função;

- registrar operações críticas;

- evitar exposição em logs;

- permitir desativação de registros;

- manter política de retenção;

- proteger arquivos;

- realizar backups;

- restringir integrações externas;

- revisar o uso de dados pela IA.

O agente deve alertar quando uma tarefa envolver:

- CPF;

- CNPJ associado a dados pessoais;

- documentos de identidade;

- dados bancários;

- assinaturas;

- informações de empregados;

- contratos confidenciais;

- dados técnicos de clientes.

# 19. Integração com o Gemini

A integração deve ser encapsulada em uma camada própria:

apps/ai_assistant/ services.py prompts.py schemas.py permissions.py exceptions.py tests/

## Requisitos

- chave de API somente em variável de ambiente;

- nunca registrar prompts com dados sensíveis;

- timeout configurado;

- tratamento de indisponibilidade;

- limite de tamanho;

- validação da resposta;

- registro da operação;

- revisão humana;

- possibilidade de desligar a IA por configuração;

- nenhum fluxo crítico deve depender exclusivamente da resposta do modelo.

## Exemplos de funcionalidades

- resumo de reuniões;

- extração de metadados;

- sugestão de tarefas;

- classificação de documentos;

- comparação de versões;

- identificação de campos ausentes;

- apoio à criação de rascunhos comerciais.

## Proibições

O agente de IA não pode:

- aprovar documentos técnicos;

- validar cálculos de engenharia;

- assinar ART;

- emitir decisão financeira definitiva;

- enviar proposta sem aprovação;

- alterar contrato sem autorização;

- excluir registros;

- conceder permissões;

- executar comandos destrutivos sem confirmação.

# 20. Indicadores de acompanhamento

O andamento do desenvolvimento deve ser acompanhado por métricas simples:

- funcionalidades concluídas;

- funcionalidades em desenvolvimento;

- tarefas bloqueadas;

- bugs abertos;

- bugs críticos;

- cobertura de testes;

- tempo médio de conclusão;

- alterações de escopo;

- migrações pendentes;

- riscos em aberto;

- decisões pendentes;

- módulos entregues.

O foco não deve ser apenas contar linhas de código. O indicador principal é o número de fluxos de negócio confiáveis que o sistema consegue executar.

# 21. Registro de progresso

Esta seção deve ser atualizada a cada ciclo de desenvolvimento.

## Estado atual

Fase atual: Fase 0 — Preparação Status geral: Planejamento Progresso estimado: 0% Riscos críticos: Nenhum registrado Bloqueios: Nenhum registrado Última atualização: 06/08/2026

## Tarefas

- Definir escopo inicial

- Criar repositório

- Configurar ambiente Python

- Configurar projeto Django

- Configurar PostgreSQL

- Configurar Tailwind

- Criar usuário personalizado

- Definir permissões

- Implementar contatos

- Implementar leads

- Implementar propostas

- Implementar contratos

- Implementar projetos

- Implementar documentação

- Implementar medições

- Implementar faturamento

- Integrar Gemini

- Criar dashboard

- Configurar backups

- Criar documentação operacional

## Tarefas em andamento

- Nenhuma.

## Tarefas bloqueadas

- Nenhuma.

## Decisões pendentes

- Definir solução de armazenamento de arquivos em produção.

- Definir política de retenção documental.

- Definir regras finais de aprovação de propostas.

- Definir responsável pela aprovação de medições.

- Confirmar o identificador oficial do modelo Gemini utilizado na integração.

# 22. Registro de alterações deste documento

Versão Data Responsável Alteração

1. 0.0 06/08/2026 Harold Criação do documento

de contexto do projeto

# 23. Instruções finais para o agente Gemini

Antes de qualquer alteração:

1. Leia este documento.

2. Verifique o código existente.

3. Não invente arquivos, funcionalidades ou regras.

4. Não altere o escopo sem registrar a mudança.

5. Não remova dados ou funcionalidades sem autorização.

6. Não faça mudanças destrutivas silenciosamente.

7. Escreva testes para regras importantes.

8. Respeite as permissões de acesso.

9. Proteja dados pessoais, financeiros e técnicos.

10. Informe premissas e riscos.

11. Atualize a documentação após mudanças relevantes.

12. Mantenha o ERP funcional mesmo quando a integração com IA estiver indisponível.

13. Trate a saída da IA como sugestão até que um usuário autorizado a valide.

14. Priorize o fluxo principal do negócio.

15. Prefira uma implementação simples, clara e testável.

## Formato para iniciar uma tarefa

Tarefa: Objetivo: Módulo: Problema que será resolvido: Arquivos provavelmente afetados: Regras de negócio: Critérios de aceitação: Riscos: Plano de implementação: Plano de testes:

## Formato para concluir uma tarefa

Status: Concluída

Implementado:

- ...

Arquivos alterados:

- ...

Testes:

- ...

Migrações:

- ...

Permissões:

- ...

Impactos em outros módulos:

- ...

Riscos ou limitações:

- ...

Documentação atualizada:

- ...

Próxima tarefa recomendada:

- ...

# 24. Regra de manutenção deste arquivo

Este documento deve ser atualizado sempre que ocorrer uma destas situações:

- mudança de escopo;

- nova decisão arquitetural;

- alteração de regras de negócio;

- conclusão de uma fase;

- mudança de responsabilidade;

- inclusão de integração;

- identificação de risco relevante;

- alteração no modelo de permissões;

- adoção de nova tecnologia;

- mudança no fluxo comercial, operacional ou financeiro;

- alteração da política de uso da IA.

A atualização deve acontecer junto com a alteração correspondente, nunca apenas no final do projeto.