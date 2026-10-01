# ERPangea - Versão 2.0 (Módulo Base Enterprise)

**Organização:** Pangea Engenharia Ltda.  
**Domínio:** Consultoria e Projetos de Engenharia Civil, Geotecnia, Fundações, Contenções e Obras de Terra  
**Arquitetura:** Monólito Modular de Alta Coesão e Baixo Acoplamento com Processamento Assíncrono  
**Stack Principal:** Python 3.12+ | Django 6.x | PostgreSQL 16 (Psycopg 3 Pooling) | Redis 7 | Celery 5.x | HTMX | Bootstrap 5.3  

---

## 🏛️ Funcionalidades Implementadas no Módulo Base (v2.0.0)

### 1. Infraestrutura & Orquestração
- **Gerenciador de Dependências:** Astral `uv` com resolução determinística e compilação antecipada de bytecode.
- **Configuração 12-Factor:** `config/settings.py` parametrizado via `.env` com fallback transparente para SQLite em desenvolvimento ágil (`USE_SQLITE=True`).
- **Banco de Dados:** Conexão com PostgreSQL 16 utilizando pool de conexões persistente (`CONN_MAX_AGE = 600`, `CONN_HEALTH_CHECKS = True`) e extensões (`pg_trgm`, `unaccent`, `uuid-ossp`).
- **Filas e Cache:** Redis 7 como broker do Celery e cache backend.
- **Processamento Assíncrono:** Celery Worker e Celery Beat (DatabaseScheduler via `django-celery-beat`) configurados com retries automáticos e time limits.
- **Containerização Segura:** `Dockerfile` multi-stage executando sob usuário sem privilégios de root (`appuser`, UID 1000) e `docker-compose.yml` orquestrando 5 serviços com healthchecks.
- **Sonda de Integridade:** Endpoint corporativo `/health/` com verificação de conectividade em tempo real com o banco de dados e cache Redis.

### 2. Autenticação Moderna & Identidade
- **Modelo Customizado (`apps.accounts.User`):** Chaves primárias em UUIDv4 contra ataques de enumeração horizontal. Autenticação exclusiva por e-mail corporativo.
- **Proteção Ativa contra Força Bruta:** Contador de tentativas falhas com bloqueio temporal automático (`locked_until`) após 5 erros consecutivos.
- **Perfil do Colaborador (`apps.accounts.UserProfile`):** Vínculo 1:1 automático via Signal, registro no CREA/UF, cargo/especialidade técnica, foto de identificação (avatar) e telefone corporativo normalizado no padrão brasileiro: `(99) 9 9999-9999`.
- **Máscara e Filtros:** Filtro de template `format_phone_br` e máscara interativa client-side em JavaScript nativo.

### 3. Modelo RBAC Multi-Setor com Hierarquia Cumulativa
- **Atribuição Multi-Setor (`apps.accounts.UserSectorAssignment`):** Permite que colaboradores em equipes enxutas acumulem funções em múltiplos setores (`TECNICO`, `COMERCIAL`, `FINANCEIRO`, `ADMINISTRATIVO`, `TI`).
- **Escala Hierárquica Unificada (1 a 4):**
  - **Nível 4 (Diretoria):** Alçada financeira irrestrita (> R$ 25k), RT/CREA, assinatura formal e entrega definitiva de obras.
  - **Nível 3 (Coordenação):** Despacho de OS, aprovação de medições e alçada média (R$ 5k a R$ 25k).
  - **Nível 2 (Operacional):** Elaboração técnica, cálculos, revisões R00&rarr;R01 e emissão de NFS-e.
  - **Nível 1 (Assistente):** Consulta ampla e rascunhos; sem poder de homologação.
- **Princípio da Herança Cumulativa:** Níveis superiores herdam automaticamente as permissões dos níveis inferiores do mesmo setor.
- **Motor de Autorização:** Decorador `@require_role` (suportando regras individuais ou tuplas OR) e mixin `RoleRequiredMixin`.

### 4. Trilha de Auditoria Imutável (`apps.audit_log`)
- **Imutabilidade Estrita (`apps.audit_log.AuditLog`):** Métodos `.save()` e `.delete()` bloqueiam mutações em registros existentes, levantando `PermissionDenied` (HTTP 403).
- **Middleware ContextVars:** Rastreamento thread-safe e async-safe de IP de origem e User-Agent.
- **Eventos Automáticos:** Listeners para login bem-sucedido, logout e falhas de login.
- **Processamento Desacoplado:** Tarefa Celery `record_audit_log_async` para persistência em background.

### 5. Gestão Completa de Senhas
- **Alteração de Senha (Autenticado):** Tela dedicada `/accounts/password/change/` acessível pelo menu do usuário e pela página de perfil.
- **Recuperação de Senha Esquecida (Público):** Ciclo completo em 4 etapas com tokens criptografados e link "Esqueceu a senha?" na tela de login.
- **Alternador de Visibilidade (Olho):** Botões com ícone `bi-eye` / `bi-eye-slash` integrados ao login institucional, alteração de senha e redefinição.

### 6. Interface Corporativa e Governança
- **Barra Superior Unificada:** Miniatura do avatar, nome completo, cargo, crachá do setor/nível hierárquico com contador de setores acumulados (`+X`) e menu dropdown.
- **Manual de Governança (`/accounts/help/`):** Documentação técnica interativa com índice lateral ancorado cobrindo arquitetura, hierarquia, matriz de setores e regras de segregação mínima (Dual Control Mitigado).
- **Django Admin Customizado:** Listagem com crachás coloridos multi-setor e inline tabular para edição rápida de alçadas.

---

## 🧪 Bateria de Testes Automatizados (19 testes)

```bash
USE_SQLITE=True uv run python manage.py test tests
# Ran 19 tests in 6.8s — OK (100% de aprovação)
```

---

## 🚀 Execução Rápida

```bash
# 1. Instalar dependências
uv sync

# 2. Migrar banco de dados
USE_SQLITE=True uv run python manage.py migrate

# 3. Inicializar RBAC
USE_SQLITE=True uv run python manage.py setup_rbac

# 4. Iniciar servidor
USE_SQLITE=True uv run python manage.py runserver 0.0.0.0:8000
```
- **Login:** `admin@pangea.com.br` / `admin123`
