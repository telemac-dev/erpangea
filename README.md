# ERPangea - Sistema Integrado de Gestão Empresarial (Versão 2.0.2)

**Organização:** Pangea Engenharia Ltda.  
**Sede:** Manaus / Amazonas &bull; Registro CREA-AM  
**Domínio:** Consultoria e Projetos de Engenharia Civil, Geotecnia, Fundações Superficiais e Profundas, Contenções de Grande Porte, Estabilidade de Taludes e Laudos Periciais  
**Padrão Arquitetural:** Monólito Modular de Alta Coesão e Baixo Acoplamento com Processamento Assíncrono  
**Stack Principal:** Python 3.12+ | Django 6.x | PostgreSQL 16 (Psycopg 3 Pooling) | Redis 7 | Celery 5.x | HTMX 1.9+ | Bootstrap 5.3  

---

## 🏛️ 1. Visão Geral da Arquitetura do Sistema

O **ERPangea v2.0.2** centraliza e digitaliza integralmente a esteira técnica, comercial, cadastral e de governança da Pangea Engenharia, integrando regras estritas de normas ABNT (NBR 6122, 6118, 11682, 6484), compliance jurídico de contratos e controle de alçadas executivas.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Camada de Apresentação (Interface Web)                          │
│                   Bootstrap 5.3 + HTMX 1.9 + Vanilla JS (Sem SPAs Pesadas)             │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTP (HTML Partials / JSON)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              Gunicorn WSGI Application Server                          │
├───────────────────┬───────────────────┬───────────────────┬────────────────────────────┤
│   apps.accounts   │  apps.audit_log   │   apps.contacts   │      apps.commercial       │
│  (Auth, Perfil,   │  (Auditoria 100%  │ (Empresas, SPEs,  │   (Propostas ABNT, Portal  │
│   RBAC Multi-Set) │     Imutável)     │  ViaCEP, Kanban)  │   Aceite, CTR, D0 Mise Svc)│
└─────────┬─────────┴─────────┬─────────┴─────────┬─────────┴──────────────┬─────────────┘
          │                   │                   │                        │
          ▼                   ▼                   ▼                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                         PostgreSQL 16 (Relacional + pg_trgm)                           │
│                 Pool de Conexões Persistente (CONN_MAX_AGE = 600s)                     │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             Redis 7 & Celery 5.x                                       │
│          Cache de Sessão + Broker de Mensageria + Worker & Beat Scheduler              │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 2. Módulos Entregues e Funcionalidades

### 2.1 Identidade, Autenticação Moderna & Governança (`apps.accounts`)
- **Identificadores UUIDv4:** Chaves primárias em UUIDv4 em todos os modelos de usuários e entidades, mitigando ataques de enumeração horizontal (OWASP).
- **Autenticação por E-mail:** Login corporativo estrito por e-mail, sem dependência de usernames legados.
- **Proteção Ativa contra Força Bruta:** Contador incremental de falhas de autenticação (`failed_login_attempts`) com bloqueio temporário automático (`locked_until`) após 5 tentativas consecutivas.
- **Perfil Profissional & CREA (`UserProfile`):** Vínculo automático 1:1, número de registro no conselho de classe (CREA/UF) para habilitação de ARTs, cargo, foto/avatar e telefone corporativo.
- **Padronização Telefônica Brasileira:** Máscara interativa em JavaScript nativo e validação backend para telefones celulares no padrão `(99) 9 9999-9999` e fixos `(99) 9999-9999`.
- **Ciclo Completo de Senhas:**
  - Alteração de senha autenticada (`/accounts/password/change/`) acessível pelo menu do usuário e página de perfil.
  - Recuperação de senha esquecida em 4 etapas com tokens criptografados e link na tela de login.
  - Botão alternador de visibilidade (ícone de olho `bi-eye` / `bi-eye-slash`) integrado em todos os campos de senha do sistema.
- **Barra Superior de Usuário Unificada:** Miniatura do avatar com fallback para inicial, nome completo, cargo, crachá do setor/nível hierárquico com contador de setores acumulados (`+X`) e menu dropdown com ações rápidas e logout seguro via `POST` (CSRF).

### 2.2 Modelo RBAC Multi-Setor com Hierarquia Cumulativa
- **Atribuição Multi-Setor (`UserSectorAssignment`):** Projetado para equipes enxutas onde colaboradores acumulam responsabilidades de setores distintos (`ADMINISTRATIVO`, `COMERCIAL`, `TECNICO`, `FINANCEIRO`, `TI`).
- **Escala Hierárquica Unificada (Níveis 1 a 4):**
  - **Nível 4 (Diretoria):** Alçada financeira irrestrita (> R$ 25k), RT/CREA, assinatura formal de contratos e entrega definitiva de obras.
  - **Nível 3 (Coordenação):** Despacho de Ordens de Serviço (OS), aprovação de medições e alçada média (R$ 5k a R$ 25k).
  - **Nível 2 (Operacional):** Elaboração técnica, cálculos, desenhos, revisões R00&rarr;R01 e emissão de NFS-e.
  - **Nível 1 (Assistente):** Consulta ampla e rascunhos; sem poder de homologação.
- **Princípio da Herança Cumulativa:** Níveis superiores herdam automaticamente as prerrogativas dos níveis inferiores do mesmo setor.
- **Motor de Autorização:** Decorador `@require_role` (suportando regras individuais ou tuplas `OR`) e mixin `RoleRequiredMixin`.
- **Manual de Governança Interativo (`/accounts/help/`):** Documentação técnica ancorada com matriz de permissões por setor, regras de segregação mínima (*Dual Control Mitigado*) e princípios de autoridade máxima.

### 2.3 Trilha de Auditoria Imutável (`apps.audit_log`)
- **Imutabilidade Estrita (`AuditLog`):** Métodos `.save()` e `.delete()` bloqueiam mutações em registros existentes no banco de dados, levantando `PermissionDenied` (HTTP 403).
- **Middleware ContextVars:** Rastreamento thread-safe e async-safe de endereço IP de origem e User-Agent do navegador.
- **Rastreamento Automático:** Listeners para login, logout, falhas de autenticação e mutações em entidades de domínio (`Contact`, `CommercialProposal`, `LegalContract`, etc.).
- **Processamento Assíncrono:** Tarefa Celery `record_audit_log_async` para persistência em background sob alta carga.

### 2.4 Gerenciamento Unificado de Contatos (`apps.contacts`)
- **Modelo Polimórfico de Entidades (`Contact`):** Suporte nativo a Pessoa Jurídica (`COMPANY`) e Pessoa Física (`INDIVIDUAL`) com relacionamento hierárquico pai-filho (`parent_id`).
- **Suporte a Empreendimentos e SPEs:**
  - Classificação `company_subtype`: *Matriz / Holding Controladora*, *Sociedade de Propósito Específico (SPE)*, *Filial / Unidade Regional* e *Consórcio de Empresas*.
  - Uma SPE ou filial pode ter seu **CNPJ próprio (14 dígitos)** e estar simultaneamente vinculada à construtora/holding controladora.
  - Validação anti-ciclo hierárquico no método `clean()` (impede dependências circulares).
- **Subordinação & Multi-Endereços:** Cadastro de pessoas de contato subordinadas (`CONTACT`), endereços de faturamento (`INVOICE`), canteiros de obra / frentes de entrega (`DELIVERY`) e filiais (`OTHER`).
- **Validação Fiscal Brasileira:**
  - Algoritmos matemáticos oficiais de validação de dígitos verificadores de CPF e CNPJ (rejeita sequências repetidas e cálculos inválidos).
  - Endpoint assíncrono HTMX (`/contacts/validate-document/`) com validação no evento `blur` e detecção em tempo real de duplicidade de documentos ativos.
  - Campos para Inscrição Estadual (IE), Inscrição Municipal (IM) e Código SUFRAMA.
- **Autopreenchimento de Endereço via ViaCEP:**
  - Endpoint proxy interno com cache de 24h em Redis/Memória e timeout resiliente de 4s (`/contacts/cep-lookup/?cep=...`).
  - Preenchimento automático de Logradouro, Bairro, Cidade e UF ao digitar 8 dígitos de CEP, com foco automático no campo Número.
  - Caráter 100% opcional com liberdade total de edição manual e feedback visual por badges (*Buscando*, *Sucesso*, *Não Localizado*, *Manual*).
- **Visualizações Duplas:**
  - **Kanban (`/contacts/?view=kanban`):** Grade simétrica com cartões de dimensões uniformes (195px de altura fixa), tipografia dos nomes padronizada em 2 linhas (`text-truncate-2`), avatar com sub-logotipo da empresa-mãe sobreposto, badges de tags e indicação de holding controladora.
  - **Tabela / Lista (`/contacts/?view=list`):** Grade completa com caixas de seleção para operações em massa, dados fiscais, contatos diretos e links rápidos de ação.
- **Operações Avançadas:**
  - **Modal de Confirmação de Arquivamento:** Explicita os efeitos do *Soft Delete* (preservação integral de histórico de contratos e medições) e audita o nível de permissões exigido via RBAC antes de confirmar.
  - **Assistente de Mesclagem (Merge Wizard):** Deduplicação de cadastros elegendo um contato de destino e reatribuindo automaticamente entidades vinculadas.
  - **Exportação & Importação:** Download direto da base em Excel (.xlsx) e CSV; assistente de importação com modelo para download e relatório linha a linha de inconsistências.

### 2.5 Módulo Comercial & Gestão Contratual (`apps.commercial`)
- **Numeração Formal Pangea:** Propostas comerciais no formato sequencial `PROP-XXXXA/AAAA` (ex.: `PROP-1685A/2026`) e contratos `CTR-XXXXA/AAAA`.
- **Combobox Preditivo de Seleção de Clientes:**
  - Campo inteligente com busca em tempo real por Razão Social, Nome Fantasia, CNPJ, CPF, SPE ou Cidade.
  - Sugestões com badges visuais (`PJ • SPE`, `PJ • Matriz`, `PF`), documento formatado e indicador de holding controladora.
  - Card de resumo com botão "Trocar" e sugestão automática de localização da obra baseada na cidade do cliente.
- **Escopos Técnicos com Normas ABNT (`ProposalScopeItem`):**
  - Associação mandatória de disciplinas e normas técnicas:
    - *NBR 6122 (Projeto e Execução de Fundações)*
    - *NBR 6118 (Estruturas de Concreto Armado)*
    - *NBR 11682 (Estabilidade de Encostas e Taludes)*
    - *NBR 6484 (Sondagens de Simples Reconhecimento SPT)*
  - Precificação por item com cálculo automático do valor global fixo e irreajustável.
  - **Trava de Imutabilidade:** Após o aceite da proposta, escopo e valores são blindados contra alterações.
- **Checklist Técnico de Insumos da Contratante (`ProposalInputRequirement`):**
  - Rastreamento e homologação técnica de laudos de sondagem SPT, plantas de carga com momentos e arquivos DWG fornecidos pelo cliente.
  - Modal do engenheiro geotécnico para emissão de parecer e aprovação de conformidade normativa.
- **Portal Público e Aceite Eletrônico Legal (`/commercial/public/proposal/<token>/`):**
  - Landing page pública responsiva acessível via token seguro HTTPS sem necessidade de login.
  - **Aceite Online Qualificado (MP 2.200-2/2001 e Lei 14.063/2020):** Coleta de Nome Completo, CPF/CNPJ, Cargo/Poderes de representação, IP de origem, User-Agent e carimbo de tempo, gerando **Hash SHA-256 de Conformidade Jurídica**.
  - Opções para o cliente de *Solicitar Revisão de Escopo* (reabre com status `EM_REVISAO`) e *Recusa Formal* (`DECLINADA` com motivo).
  - Bloqueio automático de aceite para propostas com prazo de validade expirado.
- **Conversão Automática em Minuta Contratual (`LegalContract`):**
  - O aceite da proposta instancia automaticamente a minuta contratual com cláusulas padrão da Pangea Engenharia:
    - Cláusula de Objeto vinculada às normas ABNT.
    - Cláusula de Preço Fixo e Condições Comerciais.
    - **Cláusula Suspensiva de Prazo:** O prazo de execução (10 a 30 dias) conta estritamente a partir da validação de todos os insumos técnicos ($D_0$).
    - Foro da Comarca de Manaus/AM e obrigação de recolhimento de ART junto ao CREA-AM.
  - Suporte a *Minuta Padrão ERP* e *Contrato Externo (Minuta do Cliente)* com upload do PDF assinado.
- **Painel de Entrada em Serviço (*Mise en Service* & $D_0$):**
  - Governança que bloqueia a contagem do cronograma até que as 3 pré-condições sejam atendidas:
    1. Contrato formal assinado (com PDF anexado).
    2. Todos os insumos obrigatórios aprovados pelo engenheiro geotécnico.
    3. Número de ART no CREA-AM registrado.
  - Ao disparar o *Mise en Service*, o sistema formaliza o **Marco Zero ($D_0$)** e calcula a data limite final exata de entrega ($D_0 + \text{Prazo}$).
- **Visualização para Impressão / PDF (`/commercial/proposals/<id>/print/`):**
  - Layout institucional da Pangea Engenharia com cabeçalho de Manaus/AM, tabelas de normas, memoriais descritivos e linhas formais de assinatura.

---

## 🧪 3. Bateria de Testes Automatizados (35 Testes)

O sistema possui uma suite formal de testes unitários e de integração cobrindo 100% dos fluxos críticos:

```bash
USE_SQLITE=True uv run python manage.py test tests
```

### Cobertura da Suite:
1. `tests/test_auth_and_audit.py`: Modelo User com UUIDv4, criação de superuser, perfil automático, proteção contra força bruta (lockout), imutabilidade de logs de auditoria e tasks assíncronas no Celery.
2. `tests/test_hierarchical_rbac.py`: Atribuições multi-setor, herança cumulativa de níveis hierárquicos (1 a 4), estanqueidade entre setores acumulados, decorador `@require_role`, regras `OR` e exclusividade do setor primário.
3. `tests/test_password_management.py`: Alteração autenticada de senha, ciclo de recuperação em 4 etapas com tokens criptografados e re-autenticação.
4. `tests/test_contacts.py`: Validação matemática de CPF e CNPJ, detecção assíncrona de duplicidade, contatos subordinados, soft-delete com modal e alçadas RBAC, assistente de mesclagem, exportação CSV/XLSX, importação e suporte a SPEs/Holdings com prevenção de ciclos hierárquicos.
5. `tests/test_commercial.py`: Codificação `PROP-XXXXA/AAAA`, cálculo de itens de escopo, imutabilidade pós-aceite, portal público com token, aceite eletrônico com hash SHA-256, solicitação de revisão, recusa, bloqueio de proposta expirada, geração contratual automática, trava tripla de *Mise en Service* ($D_0$) e cálculo de prazo final.

---

## 🚢 4. Guia Completo de Deploy e Operação no Portainer

A aplicação está configurada para deploy automatizado em contêineres Docker orquestrados via **Portainer CE**.

### 4.1 Dados de Conexão e Topologia de Produção

| Parâmetro | Valor de Produção / Homologação |
| :--- | :--- |
| **Servidor Host** | `192.168.10.250` |
| **Painel Portainer CE** | `http://192.168.10.250:9000/` |
| **Endpoint Portainer** | `ID: 3 (local)` |
| **Stack Name** | `erpangea-v2` |
| **Git Repository** | `https://github.com/telemac-dev/erpangea.git` |
| **Branch Ativa** | `refs/heads/v2.0.2` |
| **Compose File** | `docker-compose.yml` |
| **URL da Aplicação Web**| **`http://192.168.10.250:8000/`** |
| **Sonda de Healthcheck** | `http://192.168.10.250:8000/health/` |

---

### 4.2 Topologia de Contêineres da Stack

A stack `erpangea-v2` é composta por 5 microsserviços interligados na rede bridge isolada `erpangea_net`:

```
┌──────────────────┬───────────────────────┬───────────────────┬──────────────────────────────────────────┐
│ Serviço          │ Nome do Contêiner     │ Porta no Host     │ Função Operacional                       │
├──────────────────┼───────────────────────┼───────────────────┼──────────────────────────────────────────┤
│ `web`            │ `erpangea_web`        │ `8000:8000`       │ Gunicorn WSGI Server (Django Web Core)   │
│ `celery_worker`  │ `erpangea_worker`     │ Interna           │ Processamento assíncrono de tarefas      │
│ `celery_beat`    │ `erpangea_beat`       │ Interna           │ Agendador de tarefas periódicas          │
│ `db`             │ `erpangea_db`         │ `5433:5432`*      │ PostgreSQL 16 Alpine com pg_trgm/unaccent│
│ `redis`          │ `erpangea_redis`      │ `6380:6379`*      │ Redis 7 Alpine com persistência AOF      │
└──────────────────┴───────────────────────┴───────────────────┴──────────────────────────────────────────┘
```
*\*As portas do PostgreSQL (5433) e Redis (6380) foram mapeadas no host para evitar conflito com outras instâncias legadas rodando no mesmo servidor (ex.: banco na 5432).*

---

### 4.3 Inicialização Automática e Zero-Downtime (`start-web.sh`)

O contêiner `erpangea_web` utiliza o script de entrada inteligente `/app/docker/scripts/start-web.sh`, que executa na seguinte ordem antes de subir o Gunicorn:

1. **Aguardar Serviços:** Aguarda o PostgreSQL e o Redis estarem completamente operacionais e com healthchecks saudáveis (`pg_isready` e `redis-cli ping`).
2. **Migrações Automáticas:** Executa `python manage.py migrate --noinput`.
3. **Provisionamento RBAC:** Executa `python manage.py setup_rbac` para garantir a criação dos 5 grupos corporativos.
4. **Garantia de Superusuário:** Verifica e provisiona o administrador padrão se inexistente:
   - **E-mail:** `admin@pangea.eng.br`
   - **Senha:** `Pangea#2026`
5. **Carga Inicial Idempotente:** Caso o banco esteja vazio, dispara automaticamente os comandos de seed:
   - `seed_contacts_50`: Popula 55 contatos com dados de holdings e prepostos.
   - `seed_manaus_constructors`: Popula as 10 maiores construtoras de Manaus/AM com SPEs, canteiros e telefones DDD 92.
   - `seed_commercial_demo`: Popula propostas modelo, contratos e marco zero $D_0$.
6. **Execução do Gunicorn:** Dispara o servidor WSGI com 4 workers em modo multithread (`gthread`):
   ```bash
   exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2
   ```

---

### 4.4 Procedimento de Deploy Passo a Passo no Portainer

#### Opção A: Criação de Nova Stack via Interface Web do Portainer
1. Acesse: `http://192.168.10.250:9000/` e efetue login com usuário e senha do Portainer.
2. Selecione o ambiente **local** (Endpoint 3).
3. No menu lateral esquerdo, clique em **Stacks** &rarr; **Add stack**.
4. Configure os parâmetros da Stack:
   - **Name:** `erpangea-v2`
   - **Build method:** Selecione **Repository**.
   - **Repository URL:** `https://github.com/telemac-dev/erpangea.git`
   - **Repository reference:** `refs/heads/v2.0.2`
   - **Compose path:** `docker-compose.yml`
   - **Automatic updates:** Habilite se desejar *polling* contínuo de novos commits.
5. Clique no botão azul **Deploy the stack**. O Portainer clonará a branch, construirá a imagem Docker via `Dockerfile` e subirá os 5 contêineres automaticamente.

#### Opção B: Deploy e Atualização Automatizada via API REST
Você pode disparar a criação ou atualização da stack programaticamente através da API do Portainer:

```bash
# 1. Autenticar e obter token JWT
JWT_TOKEN=$(curl -s -X POST http://192.168.10.250:9000/api/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<SENHA_PORTAINER>"}' | grep -o '"jwt":"[^"]*' | cut -d'"' -f4)

# 2. Disparar o Git Redeploy da Stack (ID 33) com pull da imagem e rebuild
curl -s -X PUT "http://192.168.10.250:9000/api/stacks/33/git/redeploy?endpointId=3" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repositoryReferenceName":"refs/heads/v2.0.2","prune":false,"pullImage":true}'
```

---

### 4.5 Variáveis de Ambiente Suportadas

O arquivo `.env.example` serve de base para o ambiente:

```ini
# Seguranca e Core
SECRET_KEY=erpangea-insecure-dev-key-change-in-production-2026-v2
DEBUG=False
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=http://192.168.10.250:8000,http://localhost:8000,http://127.0.0.1:8000

# Banco de Dados (PostgreSQL 16)
USE_SQLITE=False
POSTGRES_DB=erpangea_v2
POSTGRES_USER=pangea_user
POSTGRES_PASSWORD=pangea_secure_pass
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_CONN_MAX_AGE=600

# Cache e Filas Assíncronas (Redis 7 & Celery)
REDIS_HOST=redis
REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_WORKER_CONCURRENCY=4
CELERY_LOG_LEVEL=INFO

# Credenciais Iniciais de Administrador
ADMIN_EMAIL=admin@pangea.eng.br
ADMIN_PASSWORD=Pangea#2026

# Servidor Gunicorn
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
```

---

## 🛠️ 5. Comandos de Manutenção e Operação

### Executar Comandos no Contêiner em Produção via Docker CLI:
```bash
# Acessar shell do container web
docker exec -it erpangea_web bash

# Executar migrações manualmente
docker exec -it erpangea_web python manage.py migrate

# Criar um novo colaborador via comando CLI
docker exec -it erpangea_web python manage.py create_collaborator \
  --email="diretor.obras@pangea.eng.br" \
  --password="SenhaForte#2026" \
  --first-name="Eduardo" \
  --last-name="Rezende" \
  --sector="TECNICO" \
  --level=4 \
  --extra-sectors="COMERCIAL:3,FINANCEIRO:4" \
  --job-title="Diretor Técnico de Engenharia" \
  --crea="CREA-AM 506123/D"

# Repopular construtoras de Manaus
docker exec -it erpangea_web python manage.py seed_manaus_constructors
```

### Visualizar Logs em Tempo Real:
```bash
docker logs -f erpangea_web
docker logs -f erpangea_worker
docker logs -f erpangea_beat
docker logs -f erpangea_db
```

---

## 💻 6. Execução Local para Desenvolvimento

Caso deseje executar o projeto em modo local/desenvolvimento rápido sem Docker:

```bash
# 1. Instalar dependências via uv
uv sync

# 2. Executar migrações locais no SQLite
USE_SQLITE=True uv run python manage.py migrate

# 3. Inicializar grupos de permissão RBAC
USE_SQLITE=True uv run python manage.py setup_rbac

# 4. Criar dados de teste (Opcional)
USE_SQLITE=True uv run python manage.py seed_contacts_50
USE_SQLITE=True uv run python manage.py seed_manaus_constructors
USE_SQLITE=True uv run python manage.py seed_commercial_demo

# 5. Iniciar servidor de desenvolvimento
USE_SQLITE=True uv run python manage.py runserver 0.0.0.0:8000
```
- Acesso Web Local: [http://localhost:8000](http://localhost:8000)
- Credenciais: `admin@pangea.eng.br` / `Pangea#2026`
