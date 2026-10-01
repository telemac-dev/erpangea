# ERPangea - Sistema Integrado de Gestão Empresarial

**Organização:** Pangea Engenharia Ltda.  
**Domínio:** Engenharia Civil, Geotecnia, Fundações, Contenções e Obras de Terra  
**Padrão Arquitetural:** Monólito Modular Reativo (Modular Monolith)  
**Stack Principal:** Python 3.12+ | Django 5.x / 6.x | HTMX | Bootstrap 5.3 | PostgreSQL 16  

---

## 🏛️ Visão Geral e Módulos Entregues

O ERPangea centraliza todos os processos corporativos, técnicos e financeiros da empresa:

1. **Autenticação & RBAC (`core_auth`)**:
   - Modelo de usuário customizado com e-mail como chave de login.
   - Perfis segregados por setor corporativo: *Administrativo*, *Comercial*, *Técnico*, *Financeiro*, *TI*.
   - Perfis com CREA, telefone, avatar e cargo descritivo.

2. **Auditoria Imutável (`audit_log`)**:
   - Trilha de auditoria automática em todas as operações através de Signals e Middleware.
   - Rastreamento de usuário, IP e diff das alterações no `ActivityLog`.

3. **Gerenciamento de Contatos (`contacts`)**:
   - Cadastro unificado de clientes, fornecedores, subempreiteiros e órgãos públicos.
   - Validação assíncrona em tempo real de CPF/CNPJ com HTMX.

4. **Gestão Comercial & Contratos (`commercial`)**:
   - Propostas comerciais sequenciais (`PROP-YYYY-XXXX`).
   - Imutabilidade do escopo após aprovação.
   - Conversão automática em minuta de Contrato (`CTR-YYYY-XXXX`).
   - Ordens de Serviço (`OS-YYYY-XXXX`) com bloqueio de ativação até anexação do contrato assinado.

5. **Projetos & Tarefas (`projects`)**:
   - Quadro Kanban reativo (A Fazer, Em Andamento, Impedimento, Concluída) com atualização instantânea via HTMX.
   - Bloqueio de entrega: o projeto só pode transicionar para o status **"Entregue"** se houver pelo menos uma ART aprovada no EDMS.

6. **Cofre de Documentos EDMS (`edms_docs`)**:
   - Repositório técnico com versionamento estrito e incremental (`R00` -> `R01` -> `R02`).
   - Preservação do histórico e validação de extensões técnicas (DWG, DXF, PDF, CYPE, etc.).

7. **Medições Físico-Financeiras (`measurements`)**:
   - Folhas de medição sequenciais com validação do teto financeiro contratado.
   - Fluxo de aprovação formal para habilitação de faturamento.

8. **Faturamento & NFS-e (`invoices`)**:
   - Emissão de notas fiscais vinculadas exclusivamente a medições aprovadas.
   - Geração automática de títulos no **Contas a Receber** com vencimento programado.
   - Rotina de cancelamento com estorno automático de medição e títulos.

9. **Gestão Financeira & Contas a Pagar (`financial`)**:
   - Controle de despesas e custos por centro de custo e fornecedor.
   - Política de alçadas: despesas superiores a R$ 5.000,00 ficam retidas em `Aguardando Aprovação`.
   - Liquidação obrigatória com anexo do comprovante bancário (Pix/TED/Boleto).
   - Relatório financeiro por obra confrontando **Receitas Medidas vs Despesas Alocadas** e cálculo de **Margem Direta**.

---

## 🚀 Execução do Projeto

### Pré-requisitos
- Python 3.12+
- Gerenciador [`uv`](https://docs.astral.sh/uv/)

### Execução Local
1. Instale as dependências:
   ```bash
   uv sync
   ```
2. Execute as migrações:
   ```bash
   uv run python manage.py migrate
   ```
3. Inicialize os grupos de permissão RBAC:
   ```bash
   uv run python manage.py setup_rbac
   ```
4. Inicie o servidor:
   ```bash
   uv run python manage.py runserver 0.0.0.0:8000
   ```
5. Acesse no navegador: [http://localhost:8000](http://localhost:8000)
   - Usuário padrão: `admin@pangea.com`
   - Senha padrão: `admin123`

### Execução via Docker
```bash
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py setup_rbac
```

---

## 🧪 Bateria de Testes Automatizados

Para executar toda a suite de testes unitários e de integração:
```bash
uv run python manage.py test tests
```

---

## 💾 Rotinas de Backup & Recuperação de Desastre

### Gerar Backup
Executa o backup do banco de dados e arquivos de mídia gerando arquivo compactado com verificação criptográfica SHA256:
```bash
./scripts/backup.sh
```

### Restaurar Backup
Restaura e valida a integridade do arquivo em segundos:
```bash
./scripts/restore.sh backups/erpangea_backup_NOME.tar.gz
```
