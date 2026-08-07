# ERPangea — Pangea Engenharia

**ERPangea** é o sistema web de Gestão Integrada (ERP) desenvolvido especialmente para a **Pangea Engenharia** por **Harold Gautschi**.

O sistema foi projetado em arquitetura de Monólito Modular Django para centralizar os processos comerciais, operacionais, documentais e financeiros do escritório de engenharia civil, abrangendo as áreas de:
- Projetos e Consultoria em Geotecnia
- Projetos de Fundação
- Soluções de Contenção e Muros de Arrimo
- Obras de Terra
- Estruturas e Pavimentação

---

## 🚀 Módulos do Sistema

1. **`accounts` (Usuários & Acesso)**: Autenticação, perfis de acesso (**Administrador**, **Gerente**, **Colaborador**) e gestão de usuários.
2. **`contacts` (Contatos & Histórico)**: Cadastro de Clientes, Fornecedores, Parceiros, Órgãos Públicos e Subcontratados com suporte a pessoa física/jurídica e registro de interações.
3. **`commercial` (Comercial)**: Gestão de Leads, Propostas Técnicas com **versionamento histórico (`v1`, `v2`...)** e Contratos.
4. **`projects` (Projetos & Operacional)**: Acompanhamento de projetos de engenharia, tarefas operacionais em CAD/BIM e entregas aos clientes com indicador automático de atraso.
5. **`documents` (Documentos Técnicos)**: Upload e controle de revisão de pranchas CAD, modelos BIM, memoriais de cálculo, laudos e ARTs (`R00`, `R01`...).
6. **`measurements` (Medições de Obra)**: Registro de medições físicas e fluxo de aprovação gerencial.
7. **`billing` (Faturamento & Contas a Receber)**: Emissão de faturas/NFs vinculadas a medições aprovadas, controle de vencimentos e quitação.
8. **`payables` (Contas a Pagar & Despesas)**: Registro de contas de fornecedores, upload de boletos/NFs em PDF/imagem, gestão de comprovantes/recibos de pagamento e relatórios gerenciais.
9. **`core` (Dashboard Executivo)**: Indicadores em tempo real de vendas, operação, medições e financeiro.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.14+
- **Framework Web**: Django 6.1
- **Gerenciador de Dependências**: `uv`
- **Configuração de Ambiente**: `python-decouple`
- **Frontend & Estilos**: Tailwind CSS 4.3 (app `theme`) + Alpine.js
- **Formatação Monetária**: Padrão Brasileiro (`R$ 1.234,56`)

---

## 💻 Como Rodar o Projeto

```bash
# Instalar dependências
uv sync

# Aplicar migrações
uv run python manage.py migrate

# Compilar estilos CSS do Tailwind
uv run python manage.py tailwind build

# Executar servidor de desenvolvimento
uv run python manage.py runserver
```

---

*Desenvolvido por Harold Gautschi — Pangea Engenharia.*
