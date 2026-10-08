# Padrão Arquitetural: Autocomplete On-The-Fly com Criação Confirmada
## ERPangea - Sistema Integrado de Gestão Empresarial

**Organização:** Pangea Engenharia Ltda.  
**Domínio:** Padrões de Interface Reativa, Busca Preditiva e Governança Cadastral  
**Versão:** 1.0 (Padrão Corporativo Reutilizável)  

---

## 1. Visão Geral e Justificativa

No ambiente corporativo de engenharia civil e consultoria geotécnica, formulários densos frequentemente exigem o preenchimento de itens vinculados a catálogos padronizados (ex: **Insumos da Contratante para $D_0$**, **Tipos de Serviços e Disciplinas de Escopo**, **Clientes/SPEs**, **Equipamentos de Sondagem**, **Subempreiteiros** e **Normas Técnicas**).

Menus suspensos convencionais (`<select>` estáticos) tornam-se ineficientes quando o catálogo cresce além de dezenas de registros, e campos de texto puro geram inconsistências graves de dados (duplicidades com grafias diferentes, erros de digitação e impossibilidade de indexação). O elemento nativo `<datalist>` do HTML5, por sua vez, apresenta limitações intransponíveis de estilização de largura no *Shadow DOM* dos navegadores.

Para solucionar esse desafio de forma uniforme em todos os módulos do ERPangea, foi instituído o padrão **Autocomplete Preditivo On-The-Fly com Criação Confirmada** (*Search-as-you-Type with Confirmation-Gated Creation*).

### Benefícios Centrais:
1. **Performance e Fluidez:** Busca assíncrona com *debounce* de 250ms que consulta o banco de dados em tempo real sem sobrecarregar o servidor.
2. **Seleção Ampla e Sem Cortes:** Menus dropdown que ocupam 100% da largura do formulário (`w-100`), com quebra de linha automática e *badges* informativos de metadados.
3. **Governança Anti-Poluição Cadastral:** Caso o usuário digite um item inexistente, a criação **não ocorre silenciosamente**. O sistema exibe um **Modal de Confirmação** detalhando a nova entidade, exigindo validação explícita antes de persistir o registro no catálogo corporativo.
4. **Preenchimento em Cascata:** A seleção de um item preenche automaticamente campos dependentes (categoria, especificações técnicas, normas ABNT padrão e flags de obrigatoriedade).

---

## 2. Diagrama de Fluxo e Sequência

```
  USUÁRIO                   FRONTEND (DOM/JS)                  BACKEND (Django View)             BANCO (PostgreSQL)
     |                              |                                    |                              |
     |--- 1. Digita termo (ex: "sond")->|                                |                              |
     |                              |--- 2. Debounce (250ms) ----------->|                              |
     |                              |--- 3. GET /autocomplete/?q=sond -->|                              |
     |                              |                                    |--- 4. Query Q(name__icontains)|
     |                              |                                    |    com limite [:15] -------->|
     |                              |                                    |<-- 5. Retorna registros -----|
     |                              |<-- 6. Resposta JSON {results, ...}-|                              |
     |                              |                                    |                              |
     |                              |--- 7. Renderiza Dropdown (.dropdown-menu w-100)                   |
     |                              |       com badges, códigos e prévia técnica                        |
     |                              |                                    |                              |
[CENÁRIO A: Item Existente Encontrado]                                   |                              |
     |--- 8A. Clica no item -------->|                                    |                              |
     |                              |--- 9A. Auto-preenche campos e fecha menu                          |
     |                              |                                    |                              |
[CENÁRIO B: Item Inexistente / Novo Registro]                            |                              |
     |                              |--- 8B. Exibe opção no rodapé: "+ Cadastrar novo: '{termo}'"       |
     |--- 9B. Clica em "+ Cadastrar"->|                                   |                              |
     |                              |--- 10B. Abre Modal de Confirmação (#modalConfirmCreate)           |
     |                              |         (exibe resumo: Nome, Categoria, D0, Alerta)               |
     |--- 11B. Clica em "Confirmar"->|                                   |                              |
     |                              |--- 12B. POST /quick-create/ JSON ->|                              |
     |                              |         com CSRF Token             |--- 13B. get_or_create()      |
     |                              |                                    |    + Registro no AuditLog -->|
     |                              |                                    |<-- 14B. ID e Objeto Criado---|
     |                              |<-- 15B. JSON {success: true, input}|                              |
     |                              |--- 16B. Seleciona no formulário e fecha modal                     |
```

---

## 3. Especificação das APIs Backend

Cada recurso que adota este padrão deve expor **dois endpoints REST leves e seguros**:

### 3.1. Endpoint de Busca Preditiva (`GET /<module>/<resource>/autocomplete/`)

- **Autenticação:** Obrigatória (`LoginRequiredMixin`).
- **Parâmetros Query String:**
  - `q` *(string, opcional)*: Termo de busca digitado pelo usuário.
  - `category` ou filtros específicos *(string, opcional)*: Restrição de contexto (ex: `TECNICO` ou `ADMINISTRATIVO`).
- **Otimização de Performance:**
  - Utilizar operadores `Q(name__icontains=q) | Q(code__icontains=q)`.
  - Aplicar `[:15]` para limitar o tráfego de rede e tempo de processamento.
  - Garantir `db_index=True` no campo `name` ou trigram index (`gin_trgm_ops` em PostgreSQL).
- **Contrato de Resposta JSON (HTTP 200):**
```json
{
  "results": [
    {
      "id": "76f2c265-ab69-480f-8ec8-5d18756cf219",
      "name": "Laudo de Sondagem a Percussão SPT (ABNT NBR 6484)",
      "code": "TEC-GEO-01",
      "category": "TECNICO",
      "category_display": "Técnico",
      "default_description": "Laudo completo de sondagem a percussão SPT conforme NBR 6484...",
      "is_mandatory_default": true
    }
  ],
  "total": 1,
  "query": "sond",
  "exact_match": false
}
```

### 3.2. Endpoint de Criação Rápida com Confirmação (`POST /<module>/<resource>/quick-create/`)

- **Autenticação e Segurança:** Obrigatória com validação de `CSRF Token`.
- **Payload Aceito:** JSON (`application/json`) ou Form Data (`multipart/form-data`).
- **Contrato de Entrada:**
```json
{
  "name": "Laudo de Ensaio Dilatométrico Marchetti DMT",
  "category": "TECNICO",
  "description": "Ensaio de lâmina dilatômetro para estimativa de módulo de deformabilidade.",
  "is_mandatory_default": true
}
```
- **Regras de Negócio e Governança:**
  1. **Validação de Não-Vazio:** `name` não pode ser nulo ou composto apenas por espaços.
  2. **Prevenção de Duplicidade:** Busca prévia insensível a maiúsculas/minúsculas (`name__iexact=name`). Se já existir, retorna o registro pré-existente sem duplicar (`created: false`).
  3. **Geração de Código:** Atribuição determinística de código referencial caso omitido (ex: `TEC-AUTO-XX`).
  4. **Trilha Imutável de Auditoria:** Gravação imediata no `AuditLog` com ação `CREATE`, registrando o usuário autor da inclusão.
- **Contrato de Resposta JSON (HTTP 201 Created):**
```json
{
  "success": true,
  "created": true,
  "message": "Novo insumo cadastrado com sucesso no catálogo corporativo.",
  "input": {
    "id": "b7c359bf-cd3b-49ae-8879-bad8362ae9e1",
    "name": "Laudo de Ensaio Dilatométrico Marchetti DMT",
    "code": "TEC-AUTO-10",
    "category": "TECNICO",
    "category_display": "Técnico",
    "default_description": "Ensaio de lâmina dilatômetro...",
    "is_mandatory_default": true
  }
}
```

---

## 4. Implementação no Frontend

### 4.1. Estrutura HTML do Componente Combobox

```html
<div class="col-12">
    <label class="form-label small fw-semibold text-dark">
        Insumo Obrigatório <span class="text-danger">*</span>
        <span class="text-muted fw-normal">(selecione da lista abaixo ou digite um novo)</span>
    </label>
    <div class="dropdown position-relative">
        <div class="input-group">
            <input type="text" name="input_type_name" id="id_input_type_name" 
                   class="form-control" autocomplete="off"
                   placeholder="Selecione da lista abaixo ou digite um novo insumo...">
            <button class="btn btn-outline-secondary dropdown-toggle" type="button" 
                    data-bs-toggle="dropdown" aria-expanded="false" id="btnToggleInputTypes" 
                    title="Ver catálogo de insumos">
            </button>
            <ul class="dropdown-menu dropdown-menu-start shadow p-2 w-100" 
                id="dropdown_input_types" 
                style="min-width: 100%; max-height: 360px; overflow-y: auto; z-index: 1060;">
                <!-- Resultados da busca on-the-fly inseridos dinamicamente aqui -->
            </ul>
        </div>
    </div>
</div>
```

### 4.2. Estrutura HTML do Modal de Confirmação

```html
<div class="modal fade" id="modalConfirmCreateInput" tabindex="-1" aria-hidden="true" style="z-index: 1070;">
    <div class="modal-dialog">
        <div class="modal-content shadow-lg border-0">
            <div class="modal-header bg-primary bg-opacity-10 border-bottom border-primary border-opacity-25">
                <h5 class="modal-title fw-bold text-dark">
                    <i class="bi bi-question-circle-fill text-primary me-2"></i>Confirmar Cadastro de Novo Registro
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
            </div>
            <div class="modal-body p-4">
                <p class="mb-3 text-dark small">
                    O item digitado não foi localizado no catálogo corporativo. Deseja cadastrá-lo como um novo registro oficial no ERPangea?
                </p>
                <div class="p-3 bg-light rounded border mb-3">
                    <div class="mb-2">
                        <span class="text-muted small fw-semibold d-block">Nome do Registro:</span>
                        <span class="fw-bold text-dark fs-6" id="confirm_input_name_text"></span>
                    </div>
                    <div class="mb-2">
                        <span class="text-muted small fw-semibold d-block">Categoria / Classificação:</span>
                        <span id="confirm_input_category_badge"></span>
                    </div>
                    <div>
                        <span class="text-muted small fw-semibold d-block">Condição Suspensiva:</span>
                        <span id="confirm_input_mandatory_text" class="small fw-semibold"></span>
                    </div>
                </div>
                <div class="alert alert-info py-2 px-3 small mb-0 border-start border-4 border-info">
                    <i class="bi bi-info-circle-fill me-1"></i>
                    <strong>Padrão Corporativo:</strong> Uma vez confirmado, este registro será persistido no banco de dados e ficará permanentemente disponível para todos os projetos e colaboradores da empresa.
                </div>
            </div>
            <div class="modal-footer bg-light">
                <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancelar</button>
                <button type="button" class="btn btn-primary btn-sm px-4 fw-semibold shadow-sm" id="btnConfirmQuickCreateInput">
                    <i class="bi bi-check2-circle me-1"></i>Confirmar e Cadastrar
                </button>
            </div>
        </div>
    </div>
</div>
```

---

## 5. Diretrizes para Manutenção e Atualização

1. **Campos Obrigatórios vs. Opcionais na Adição:**
   - No modal de adição, os campos de texto devem **iniciar estritamente vazios** (`value=""`), deixando visível apenas o *placeholder*.
   - Apenas seleções com valores pré-determinados (como a categoria *Técnico*) podem conter seleção padrão.
2. **Debounce Mandatório:**
   - Toda rotina de *input* conectada a endpoint de busca deve utilizar `setTimeout(..., 250)` com cancelamento do temporizador anterior (`clearTimeout`). Nunca disparar requisições em todo evento `keydown`.
3. **Escalonamento em Dispositivos Móveis e Tablets:**
   - O dropdown possui `z-index: 1060` para sobrepor o corpo do modal e `max-height: 360px` com `overflow-y: auto`, garantindo usabilidade em tablets de obra e telas de resolução reduzida.
4. **Acessibilidade e Usabilidade:**
   - Ao teclar `Escape` ou clicar fora do elemento, o dropdown deve recolher suavemente sem limpar o texto digitado.

---

## 6. Onde Reutilizar este Padrão no ERPangea

| Módulo | Entidade Alvo | Campo | Justificativa de Governança |
| :--- | :--- | :--- | :--- |
| **Comercial** | `TechnicalInputType` | Insumo da Contratante ($D_0$) | Padronização de requisitos contratuais e alçadas de início de obra. |
| **Comercial** | `TechnicalServiceType` | Tipo de Serviço / Escopo | Vinculação correta a normas ABNT vigentes e tabelas de honorários. |
| **Comercial** | `TechnicalDiscipline` | Disciplina Técnica | Estruturação uniforme de especialidades de engenharia. |
| **Contatos** | `Contact` (Holding / SPE) | Empresa Controladora | Prevenção de duplicidade de clientes corporativos e grupos econômicos. |
| **Projetos (EDMS)** | `DocumentCategory` | Tipo de Documento Técnico | Classificação de pranchas DWG, laudos periciais e relatórios de sondagem. |
| **Financeiro** | `FinancialCostCenter` | Centro de Custo / Obra | Apuração precisa de despesas alocadas por projeto. |

---

## 7. Interações e Dependências entre Módulos

```
       +-----------------------+
       |   apps.commercial     |
       | (Propostas/Contratos) |
       +-----------+-----------+
                   |
     +-------------+-------------+
     |                           |
     ▼                           ▼
+--------------------+   +-----------------------+
|  apps.audit_log    |   |     apps.accounts     |
| (Trilha Imutável)  |   | (Controle de Alçadas) |
| - Registra autoria |   | - Valida permissão do |
|   da criação rápida|   |   usuário autenticado |
+--------------------+   +-----------------------+
```

1. **`apps.audit_log`:**
   - Toda execução bem-sucedida do endpoint `quick-create` dispara a criação de um `AuditLog` com `action=CREATE`. Isso impede que novos itens surjam no catálogo corporativo sem registro de quem os introduziu.
2. **`apps.accounts`:**
   - Endpoints decorados com `LoginRequiredMixin`.
   - Podem ser estendidos com o decorador `@require_role` caso determinada entidade exija nível mínimo de alçada (ex: apenas *Operacional* ou *Coordenação* pode criar novos centros de custo).
