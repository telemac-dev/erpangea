# Sistema de Menus Dinâmicos - Documentação

## Índice
1. [Visão Geral](#visão-geral)
2. [Estrutura do Sistema](#estrutura-do-sistema)
3. [Componentes Principais](#componentes-principais)
4. [Como Implementar](#como-implementar)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Melhores Práticas](#melhores-práticas)

## Visão Geral

O sistema de menus dinâmicos é uma solução flexível para gerenciar a navegação da aplicação baseada em permissões de usuário. 
Ele permite:
- Controle granular de acesso baseado em permissões
- Menus e submenus aninhados
- Ícones personalizados
- Estado ativo automático baseado na URL atual
- Suporte a múltiplos níveis de menu

## Estrutura do Sistema

O sistema é composto por quatro componentes principais:

1. **MenuItem (menu.py)**
   - Classe base para itens de menu
   - Gerencia permissões e hierarquia

2. **Template Tag (menu_tags.py)**
   - Renderiza o menu dinamicamente
   - Processa permissões e estados ativos

3. **Template HTML (menu.html)**
   - Define a estrutura visual do menu
   - Suporta múltiplos níveis de aninhamento

4. **View Temporária (views_temp.py)**
   - Gerencia URLs em desenvolvimento
   - Fornece feedback amigável ao usuário

## Componentes Principais

### MenuItem (Classe)

```python
MenuItem(
    title="Nome do Menu",
    url="url_do_menu",
    icon="classe_do_icone",
    permissions=["app.permission"],
    children=[...]
)
```

Atributos:
- `title`: Nome exibido no menu
- `url`: URL de destino do item
- `icon`: Classe CSS do ícone (Bootstrap Icons)
- `permissions`: Lista de permissões necessárias
- `children`: Lista de subitens do menu

### Métodos Principais

```python
has_permission(user)      # Verifica permissões do usuário
get_visible_children()    # Retorna filhos visíveis
is_active(current_url)    # Verifica se o item está ativo
```

## Como Implementar

### 1. Adicionar Novo Item de Menu

Em `menu.py`, adicione um novo MenuItem na função `get_menu_items`:

```python
MenuItem(
    title=_("Novo Menu"),
    url=reverse('app:view_name'),
    icon="bi bi-icon-name",
    permissions=['app.permission_name'],
    children=[
        MenuItem(
            title=_("Submenu"),
            url=reverse('app:subview_name'),
            icon="bi bi-sub-icon",
            permissions=['app.other_permission']
        )
    ]
)
```

### 2. Implementar Nova Funcionalidade

1. Criar o app Django:
```bash
python manage.py startapp novo_app
```

2. Adicionar views:
```python
# novo_app/views.py
@login_required
def minha_view(request):
    return render(request, 'novo_app/template.html')
```

3. Configurar URLs:
```python
# novo_app/urls.py
from django.urls import path
from . import views

app_name = 'novo_app'

urlpatterns = [
    path('rota/', views.minha_view, name='nome_view'),
]
```

4. Atualizar o menu:
```python
MenuItem(
    title=_("Novo Menu"),
    url=reverse('novo_app:nome_view'),
    icon="bi bi-icon-name",
    permissions=['novo_app.permission_name']
)
```

## Exemplos Práticos

### Menu Simples
```python
MenuItem(
    title=_("Clientes"),
    url=reverse('clientes:lista'),
    icon="bi bi-people",
    permissions=['clientes.view_cliente']
)
```

### Menu com Submenu
```python
MenuItem(
    title=_("Vendas"),
    icon="bi bi-cart",
    permissions=['vendas.view_venda'],
    children=[
        MenuItem(
            title=_("Nova Venda"),
            url=reverse('vendas:criar'),
            icon="bi bi-plus-circle",
            permissions=['vendas.add_venda']
        ),
        MenuItem(
            title=_("Listar Vendas"),
            url=reverse('vendas:listar'),
            icon="bi bi-list",
            permissions=['vendas.view_venda']
        )
    ]
)
```

### Menu apenas para Staff
```python
if user.is_staff:
    MenuItem(
        title=_("Configurações"),
        url=reverse('config:index'),
        icon="bi bi-gear",
    )
```

## Melhores Práticas

1. **Permissões**
   - Use permissões granulares
   - Combine permissões quando necessário
   - Evite verificar is_staff/is_superuser diretamente

2. **URLs**
   - Use sempre reverse() para URLs
   - Evite URLs hardcoded
   - Use URLs temporárias durante desenvolvimento

3. **Ícones**
   - Mantenha consistência nos ícones
   - Use Bootstrap Icons (bi-*)
   - Escolha ícones intuitivos

4. **Organização**
   - Agrupe itens relacionados
   - Limite a profundidade do menu (máx. 3 níveis)
   - Mantenha os nomes curtos e claros

5. **Performance**
   - Cache os menus quando possível
   - Evite queries desnecessárias
   - Use lazy loading para submenus grandes

## Manutenção

1. **Atualizando Menus**
   - Modifique `menu.py`
   - Atualize permissões se necessário
   - Teste todas as rotas

2. **Removendo Itens**
   - Remova o MenuItem correspondente
   - Mantenha as permissões no modelo
   - Atualize a documentação

3. **Depuração**
   - Verifique permissões no admin
   - Use o Django Debug Toolbar
   - Monitore logs de acesso

## Dicas para Desenvolvimento

1. **URLs Temporárias**
   - Use o prefixo `/temp/` durante desenvolvimento
   - Documente com TODO comments
   - Atualize gradualmente para URLs definitivas

2. **Testes**
   - Teste diferentes níveis de usuário
   - Verifique todas as permissões
   - Teste a navegação completa

3. **Segurança**
   - Sempre verifique permissões
   - Não confie apenas no menu para segurança
   - Implemente verificações nas views

---

## Notas de Atualização

Quando implementar uma nova funcionalidade:

1. Remova a URL temporária
2. Atualize o MenuItem com a URL definitiva
3. Verifique as permissões necessárias
4. Teste a navegação completa
5. Atualize esta documentação se necessário