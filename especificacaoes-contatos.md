# Especificação do Aplicativo de Contatos — ERPangea

## 1. Objetivo

Desenvolver, utilizando Python e Django, um aplicativo de contatos para o ERPangea capaz de gerenciar pessoas físicas e jurídicas em um cadastro unificado.

O aplicativo deverá permitir que os contatos sejam classificados como:

- Clientes;
- Profissionais;
- Órgãos públicos;
- Parceiros;
- Fornecedores;
- Empreendimentos;
- Prestadores de serviço;
- Tomadores de serviço.

O mesmo contato poderá exercer mais de um papel simultaneamente.

O aplicativo deverá servir de base para os seguintes módulos atuais ou futuros:

- CRM;
- Vendas;
- Compras;
- Contratos;
- Financeiro;
- Fornecedores;
- Profissionais;
- Empreendimentos;
- Integrações fiscais;
- Futura emissão de NFS-e;
- Futura emissão de outros documentos fiscais.

> Esta especificação trata exclusivamente do aplicativo de contatos. Não deverá ser criado, nesta etapa, um aplicativo Django de NFS-e.

---

## 2. Tecnologias

Utilizar:

- Python;
- Django;
- PostgreSQL, preferencialmente;
- Django Templates;
- Tailwind CSS;
- HTMX;
- Biblioteca `requests` para futuras integrações HTTP;
- UUID como chave primária;
- `DecimalField` para valores decimais;
- Django Forms;
- Django Admin;
- Django Migrations;
- Testes automatizados com o framework de testes do Django.

Instalar a biblioteca HTTP com:

```bash
python -m pip install requests
```

Registrar as dependências do projeto com:

```bash
python -m pip freeze > requirements.txt
```

---

## 3. Diretrizes de arquitetura

O aplicativo deverá ser organizado preferencialmente como:

```text
contatos/
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── services.py
├── urls.py
├── views.py
├── validators.py
├── migrations/
├── templates/
└── tests/
```

Caso seja necessário separar responsabilidades, poderão ser utilizados aplicativos complementares:

```text
contatos/
fiscal/
auditoria/
```

### Aplicativo `contatos`

Responsável por:

- Pessoas físicas;
- Pessoas jurídicas;
- Tipos e papéis de contatos;
- Endereços;
- Telefones;
- E-mails;
- Documentos;
- Vínculos entre pessoas físicas e jurídicas;
- Dados comerciais;
- Dados de profissionais;
- Dados de órgãos públicos;
- Dados para futura integração fiscal.

### Aplicativo `fiscal`

Poderá ser criado somente para armazenar:

- Inscrições fiscais;
- Municípios;
- Regimes tributários;
- Códigos de atividade;
- Configurações fiscais do contato.

Não deverá conter, nesta etapa:

- Notas fiscais;
- Itens de NFS-e;
- Emissão de documentos;
- Cancelamento de documentos;
- Comunicação com provedores fiscais.

### Aplicativo `auditoria`

Poderá ser utilizado para:

- Histórico de alterações;
- Usuários responsáveis;
- Registro de alterações cadastrais;
- Auditoria de documentos e dados fiscais.

---

## 4. Modelo central de contato

Criar o modelo `Contato`.

A entidade `Contato` será o cadastro principal de pessoas físicas e jurídicas.

## Campos

- `id`: UUID, chave primária;
- `tipo_pessoa`;
- `nome_razao_social`;
- `nome_fantasia`;
- `nome_social`;
- `apelido`;
- `ativo`;
- `observacoes`;
- `created_at`;
- `updated_at`;
- `created_by`;
- `updated_by`;
- `deleted_at`, para exclusão lógica.

### Definição dos campos

#### `tipo_pessoa`

Deverá indicar se o contato representa:

- Pessoa física;
- Pessoa jurídica.

#### `nome_razao_social`

- Para pessoa física, armazenará o nome completo.
- Para pessoa jurídica, armazenará a razão social.

#### `nome_fantasia`

Deverá ser utilizado principalmente para pessoas jurídicas.

#### `nome_social`

Deverá ser utilizado quando aplicável a pessoas físicas.

#### `ativo`

Indica se o contato pode ser utilizado em novos lançamentos.

#### `deleted_at`

Quando preenchido, indica que o contato foi excluído logicamente.

## Regras

- Não utilizar CPF ou CNPJ como chave primária.
- Utilizar UUID como identificador principal.
- Não excluir fisicamente contatos utilizados em contratos, vendas, compras ou documentos fiscais.
- Aplicar exclusão lógica.
- Permitir pesquisa por:
  - nome;
  - razão social;
  - nome fantasia;
  - CPF;
  - CNPJ;
  - e-mail;
  - telefone;
  - município.
- Criar índices para os campos mais pesquisados.
- Armazenar CPF e CNPJ sem pontuação.
- Formatar CPF e CNPJ somente na apresentação.
- Impedir que um contato sem nome seja salvo.
- Impedir que uma pessoa jurídica seja salva sem razão social.

---

# 4.0.1 Integração com o projeto global ERPangea

O aplicativo de contatos não deverá ser desenvolvido como um sistema isolado. Ele fará parte do projeto global do ERPangea e deverá respeitar integralmente a arquitetura, os padrões, as convenções e os módulos já existentes no projeto principal.

Antes de criar ou alterar qualquer código, o agente de codificação deverá analisar a estrutura atual do ERPangea, incluindo:

- Aplicativos Django já existentes;
- Modelos compartilhados;
- Classes abstratas;
- Mixins;
- Sistema de autenticação;
- Sistema de usuários;
- Sistema de permissões;
- Organização de URLs;
- Padrão de templates;
- Componentes Tailwind existentes;
- Configuração do HTMX;
- Sistema de auditoria;
- Sistema de logs;
- Sistema de mensagens;
- Configuração de banco de dados;
- Convenções de nomes;
- Padrão de testes;
- Políticas de exclusão lógica;
- Padrão de migrations;
- Configuração de ambientes;
- Sistema de multiempresa, caso já exista;
- Sistema de filiais, estabelecimentos ou unidades de negócio, caso já exista.

## 4.1. Reutilização da arquitetura existente

O agente não deverá criar estruturas duplicadas quando já existirem recursos equivalentes no ERPangea.

Antes de criar um novo modelo, deverá verificar se o projeto já possui:

- Modelo base com UUID;
- Modelo base com datas de criação e atualização;
- Modelo para usuário responsável;
- Modelo de empresa ou organização;
- Modelo de filial ou estabelecimento;
- Modelo de endereço;
- Modelo de município;
- Modelo de país;
- Modelo de estado ou UF;
- Modelo de documentos;
- Modelo de auditoria;
- Modelo de anexos;
- Modelo de tags;
- Modelo de status;
- Sistema de permissões;
- Componentes visuais reutilizáveis.

Quando já existir um recurso equivalente, o aplicativo de contatos deverá reutilizá-lo em vez de criar uma implementação paralela.

## 4.2. Compatibilidade com os módulos globais

O aplicativo deverá ser projetado para integração com os demais módulos do ERPangea, incluindo, quando existirem:

- CRM;
- Vendas;
- Compras;
- Financeiro;
- Contas a receber;
- Contas a pagar;
- Contratos;
- Estoque;
- Projetos;
- Empreendimentos;
- Recursos humanos;
- Serviços;
- Fiscal;
- Relatórios;
- Notificações;
- Auditoria.

O modelo `Contato` deverá funcionar como uma entidade compartilhada e reutilizável por esses módulos.

Os demais aplicativos deverão referenciar o contato por relacionamento Django, preferencialmente utilizando:

- `ForeignKey`, quando houver um contato principal;
- `ManyToManyField`, quando houver múltiplos contatos;
- modelos intermediários, quando a relação possuir atributos próprios;
- `GenericForeignKey` somente quando houver justificativa arquitetural clara.

Não duplicar nome, CPF, CNPJ, endereço ou telefone em outros módulos sem uma razão específica. Quando um módulo precisar preservar um histórico, deverá utilizar um snapshot ou registro histórico claramente documentado.

## 4.3. Regras de integração entre aplicativos

O aplicativo de contatos deverá:

- Utilizar os modelos globais já existentes;
- Respeitar os namespaces de URLs do ERPangea;
- Respeitar o padrão de nomes de tabelas;
- Utilizar as configurações globais do projeto;
- Utilizar o sistema global de autenticação;
- Utilizar as permissões globais;
- Utilizar o sistema global de auditoria;
- Utilizar o sistema global de mensagens;
- Utilizar o sistema global de tratamento de erros;
- Utilizar os componentes visuais existentes;
- Respeitar o padrão global de testes;
- Respeitar as configurações globais de banco de dados;
- Respeitar o padrão de logs;
- Respeitar as políticas de exclusão lógica.

O aplicativo não deverá alterar configurações globais sem justificativa e sem avaliar o impacto nos demais módulos.

## 4.4. Multiempresa, filiais e escopo dos dados

Caso o ERPangea possua suporte a múltiplas empresas, organizações, filiais ou estabelecimentos, o aplicativo de contatos deverá respeitar esse escopo.

O agente deverá verificar:

- Se o contato pertence a uma empresa;
- Se o contato pode ser compartilhado entre empresas;
- Se existem contatos privados e contatos globais;
- Se os endereços pertencem à empresa ou ao contato;
- Se os vínculos possuem escopo por empresa;
- Se os usuários podem acessar contatos de outras empresas;
- Se clientes e fornecedores são compartilhados ou independentes por empresa;
- Se inscrições fiscais pertencem ao contato, à empresa ou ao estabelecimento.

Não assumir que um contato é necessariamente exclusivo de uma única empresa do ERPangea.

Quando o projeto já possuir uma regra de isolamento entre empresas, ela deverá ser aplicada em:

- Consultas;
- Formulários;
- Views;
- APIs;
- Administração;
- Relatórios;
- Endpoints HTMX;
- Tarefas assíncronas.

Nunca permitir que um usuário visualize ou altere contatos de outra empresa sem autorização explícita.

## 4.5. Integração com modelos existentes

Antes de implementar os modelos `Contato`, `PessoaFisica`, `PessoaJuridica`, `Endereco`, `ContatoEmail` ou `ContatoTelefone`, o agente deverá verificar se já existem modelos equivalentes no ERPangea.

Caso existam modelos semelhantes, deverá:

1. Avaliar se podem ser reutilizados;
2. Avaliar se precisam ser estendidos;
3. Evitar a criação de registros duplicados;
4. Planejar uma migração segura, caso seja necessário substituir a estrutura existente;
5. Preservar os dados atuais;
6. Atualizar os relacionamentos dos módulos dependentes;
7. Criar testes de regressão;
8. Documentar qualquer alteração estrutural.

Não criar dois cadastros independentes para a mesma finalidade, como:

- `Cliente` e `Contato`, quando ambos representarem pessoas;
- `Fornecedor` e `PessoaJuridica`, quando o fornecedor puder ser apenas um papel;
- `EnderecoContato` e outro endereço global equivalente;
- `Empresa` e `PessoaJuridica`, sem esclarecer a relação entre os conceitos.

## 4.6. Compatibilidade com usuários e permissões

O aplicativo deverá utilizar o usuário e o sistema de permissões já existentes no ERPangea.

Não criar um sistema paralelo de login ou de permissões.

As permissões deverão contemplar, quando compatível com o padrão global:

- Visualizar contatos;
- Criar contatos;
- Editar contatos;
- Inativar contatos;
- Visualizar CPF;
- Visualizar CNPJ;
- Editar dados fiscais;
- Visualizar dados bancários;
- Editar dados bancários;
- Criar vínculos;
- Encerrar vínculos;
- Exportar contatos;
- Administrar tipos de contato.

## 4.7. Compatibilidade de banco de dados e migrations

As migrations deverão ser criadas dentro do padrão do projeto global.

O agente deverá:

- Verificar o banco de dados utilizado;
- Verificar convenções de nomes;
- Verificar tabelas existentes;
- Verificar constraints existentes;
- Verificar índices já criados;
- Evitar nomes de tabelas conflitantes;
- Evitar alteração destrutiva de dados;
- Criar migrations reversíveis sempre que possível;
- Testar as migrations em banco limpo;
- Testar as migrations em banco com dados existentes;
- Documentar qualquer operação de migração de dados.

Não executar alterações manuais diretamente no banco de produção.

## 4.8. Compatibilidade visual

Os templates deverão seguir o padrão visual global do ERPangea.

Antes de criar novos componentes Tailwind, o agente deverá verificar se já existem componentes para:

- Botões;
- Formulários;
- Campos;
- Tabelas;
- Modais;
- Alertas;
- Badges;
- Paginação;
- Menus;
- Abas;
- Cards;
- Indicadores de carregamento;
- Mensagens de validação.

Os componentes existentes deverão ser reutilizados sempre que possível.

O aplicativo não deverá introduzir uma identidade visual independente ou estilos incompatíveis com os demais módulos.

## 4.9. Compatibilidade com HTMX

O uso do HTMX deverá respeitar a configuração global do ERPangea.

O agente deverá verificar:

- Como o projeto configura o token CSRF;
- Como são identificadas requisições HTMX;
- Qual é o padrão de retorno de fragments;
- Como são exibidas mensagens;
- Como são tratados erros de validação;
- Como são tratados redirecionamentos;
- Como os modais são implementados;
- Como os indicadores de carregamento são definidos;
- Como o foco é reposicionado após atualizações parciais.

Não criar uma segunda estratégia de integração HTMX que seja incompatível com a já utilizada no projeto.

## 4.10. URLs e navegação

As URLs do aplicativo deverão ser incluídas no roteamento global do ERPangea utilizando o padrão já existente.

O agente deverá:

- Utilizar namespaces;
- Evitar conflitos de nomes;
- Respeitar o padrão de versionamento;
- Integrar as páginas ao menu global;
- Respeitar breadcrumbs existentes;
- Utilizar o layout global;
- Respeitar o sistema de navegação e permissões;
- Não substituir URLs existentes sem análise de compatibilidade.

## 4.11. Serviços e regras de negócio

Os serviços do aplicativo de contatos deverão ser reutilizáveis pelos demais módulos do ERPangea.

Criar serviços para operações como:

- Criar contato;
- Atualizar contato;
- Inativar contato;
- Criar pessoa física;
- Criar pessoa jurídica;
- Criar vínculo;
- Encerrar vínculo;
- Adicionar endereço;
- Definir endereço principal;
- Adicionar telefone;
- Adicionar e-mail;
- Validar CPF;
- Validar CNPJ;
- Consultar contatos;
- Obter dados fiscais do contato.

As regras não deverão ficar espalhadas entre templates, JavaScript, views e models.

Os serviços deverão utilizar transações atômicas quando uma operação alterar várias tabelas.

## 4.12. Contratos de integração

O aplicativo deverá expor interfaces claras para uso por outros módulos, evitando que os módulos dependentes acessem diretamente detalhes internos desnecessários.

Quando apropriado, disponibilizar:

- Métodos de serviço;
- QuerySets especializados;
- Managers;
- Signals somente quando indispensáveis;
- APIs internas;
- Serializers;
- Eventos de domínio, caso o ERPangea utilize esse padrão.

Evitar dependências circulares entre aplicativos.

O aplicativo de contatos não deverá importar diretamente módulos de vendas, compras ou financeiro para executar regras que pertençam a esses módulos.

Quando houver necessidade de integração, utilizar:

- Serviços;
- Interfaces;
- Eventos;
- Relacionamentos bem definidos;
- Camadas de aplicação.

## 4.13. Compatibilidade e não regressão

A implementação deverá preservar o funcionamento dos módulos existentes.

Antes de finalizar, o agente deverá:

- Executar todos os testes do projeto;
- Executar os testes do aplicativo de contatos;
- Verificar as migrations;
- Verificar os imports;
- Verificar as URLs;
- Verificar as permissões;
- Verificar as telas existentes;
- Verificar os componentes Tailwind;
- Verificar as operações HTMX;
- Verificar as consultas em escopo de empresa;
- Verificar o comportamento em banco com dados existentes.

Nenhuma alteração deverá quebrar funcionalidades existentes sem documentação, justificativa e plano de migração.

## 4.14. Documentação da integração

O agente deverá documentar:

- Quais modelos globais foram reutilizados;
- Quais modelos novos foram criados;
- Quais modelos existentes foram alterados;
- Quais módulos dependem de `Contato`;
- Como outros módulos devem referenciar um contato;
- Como funciona o escopo por empresa ou filial;
- Quais permissões foram adicionadas;
- Quais URLs foram adicionadas;
- Quais migrations foram criadas;
- Quais decisões arquiteturais foram tomadas;
- Quais pontos foram deixados preparados para futuras integrações fiscais.

## 4.15. Regra fundamental

O aplicativo de contatos deverá ser tratado como um componente central do ERPangea, e não como um aplicativo independente.

Toda decisão de modelagem deverá considerar:

- Reutilização;
- Consistência;
- Segurança;
- Compatibilidade;
- Não duplicação de dados;
- Integração entre módulos;
- Evolução futura;
- Preservação do histórico;
- Manutenção do projeto global.
## 5. Tipos de pessoa

O campo `tipo_pessoa` deverá possuir inicialmente as opções:

```text
FISICA
JURIDICA
```

Poderá ser incluída futuramente a opção:

```text
ESTRANGEIRA
```

A opção `ESTRANGEIRA` não deverá ser implementada nesta etapa, salvo se houver requisito específico do ERPangea.

---

## 6. Papéis dos contatos

O contato não deverá possuir somente um tipo fixo, pois uma mesma pessoa ou empresa poderá desempenhar funções diferentes.

Criar o modelo `TipoContato`.

## Tipos iniciais

- `CLIENTE`;
- `PROFISSIONAL`;
- `ORGAO_PUBLICO`;
- `PARCEIRO`;
- `FORNECEDOR`;
- `EMPREENDIMENTO`;
- `PRESTADOR_SERVICO`;
- `TOMADOR_SERVICO`.

## Modelo intermediário `ContatoTipo`

Campos:

- `id`;
- `contato`;
- `tipo_contato`;
- `principal`;
- `data_inicio`;
- `data_fim`;
- `ativo`;
- `observacoes`.

## Regras

- Um contato poderá possuir vários papéis.
- O mesmo contato poderá ser cliente e fornecedor.
- O mesmo contato poderá ser parceiro e prestador de serviço.
- O mesmo contato poderá ser classificado como tomador e cliente.
- Os papéis deverão possuir histórico.
- Não permitir duplicidade de um mesmo papel ativo para o mesmo contato.
- Permitir o encerramento de um papel sem apagar o histórico.

---

## 7. Pessoa física

Criar o modelo `PessoaFisica`, relacionado com `Contato` por meio de `OneToOneField`.

## Campos

- `contato`;
- `cpf`;
- `rg`;
- `orgao_emissor_rg`;
- `uf_rg`;
- `data_nascimento`;
- `sexo`, caso necessário;
- `estado_civil`, caso necessário;
- `profissao`;
- `registro_profissional`;
- `conselho_profissional`;
- `uf_conselho`;
- `especialidade`;
- `nacionalidade`;
- `naturalidade`;
- `email_pessoal`;
- `telefone_pessoal`;
- `whatsapp`;
- `observacoes`.

## Regras

- Validar CPF utilizando algoritmo oficial.
- Impedir CPF inválido.
- Impedir CPF com todos os dígitos iguais.
- CPF deverá ser único quando informado.
- Não utilizar CPF como chave primária.
- Permitir pessoa física sem CPF somente quando houver justificativa operacional.
- Restringir o acesso a dados pessoais sensíveis.
- Não criar campos sem finalidade operacional definida.
- Permitir o cadastro de profissão e registro profissional.

---

## 8. Pessoa jurídica

Criar o modelo `PessoaJuridica`, relacionado com `Contato` por meio de `OneToOneField`.

## Campos cadastrais

- `contato`;
- `cnpj`;
- `razao_social`;
- `nome_fantasia`;
- `inscricao_estadual`;
- `indicador_inscricao_estadual`;
- `inscricao_municipal`;
- `codigo_municipio`;
- `municipio`;
- `uf`;
- `natureza_juridica`;
- `porte_empresa`;
- `cnae_principal`;
- `cnaes_secundarios`;
- `situacao_cadastral`;
- `data_abertura`;
- `regime_tributario`;
- `optante_simples_nacional`;
- `optante_simei`;
- `incentivador_cultural`;
- `responsavel_legal`;
- `email_comercial`;
- `telefone_comercial`;
- `site`;
- `observacoes`.

## Regimes tributários

Utilizar inicialmente:

```text
SIMPLES_NACIONAL
LUCRO_PRESUMIDO
LUCRO_REAL
MEI
IMUNE
ISENTA
NAO_INFORMADO
```

## Indicador de inscrição estadual

Utilizar inicialmente:

```text
CONTRIBUINTE
NAO_CONTRIBUINTE
ISENTO
NAO_INFORMADO
```

## Situação cadastral

Utilizar inicialmente:

```text
ATIVA
BAIXADA
SUSPENSA
INAPTA
NULA
NAO_INFORMADA
```

## Regras

- Validar CNPJ utilizando algoritmo oficial.
- Impedir CNPJ inválido.
- Impedir CNPJ com todos os dígitos iguais.
- CNPJ deverá ser único quando informado.
- Não utilizar CNPJ como chave primária.
- Utilizar o código IBGE do município separadamente do nome.
- Permitir o armazenamento de inscrições municipais e estaduais.
- Não assumir que todas as filiais possuem a mesma inscrição municipal.
- Permitir configurações fiscais diferentes por estabelecimento.
- Permitir atualização da situação cadastral sem apagar o histórico.
- Permitir empresas sem inscrição estadual quando forem não contribuintes ou isentas.

---

## 9. Inscrições fiscais

Criar o modelo opcional `InscricaoFiscal` para permitir maior flexibilidade.

O modelo deverá ser utilizado para inscrições adicionais, sem substituir os campos principais de CNPJ, inscrição estadual e inscrição municipal existentes em `PessoaJuridica`.

## Campos

- `id`;
- `contato`;
- `tipo`;
- `numero`;
- `uf`;
- `municipio`;
- `codigo_municipio`;
- `principal`;
- `situacao`;
- `data_inicio`;
- `data_fim`;
- `observacoes`.

## Tipos

- `CPF`;
- `CNPJ`;
- `INSCRICAO_ESTADUAL`;
- `INSCRICAO_MUNICIPAL`;
- `REGISTRO_PROFISSIONAL`;
- `OUTRO`.

## Regras

- Validar o formato conforme o tipo de inscrição.
- Permitir histórico de alterações.
- Não permitir duas inscrições principais do mesmo tipo para o mesmo contato, salvo configuração específica.
- Inscrições utilizadas em documentos ou integrações não deverão ser excluídas fisicamente.

---

# 10. Vínculo entre pessoa física e pessoa jurídica

Criar o modelo `VinculoContato`.

Esse modelo deverá associar pessoas físicas e jurídicas existentes no mesmo banco de dados.

## Campos

- `id`;
- `pessoa_fisica`;
- `pessoa_juridica`;
- `tipo_vinculo`;
- `cargo`;
- `departamento`;
- `email_corporativo`;
- `telefone_corporativo`;
- `ramal`;
- `principal`;
- `responsavel_legal`;
- `representante_comercial`;
- `pode_assinar`;
- `pode_receber_documentos`;
- `pode_receber_cobrancas`;
- `data_inicio`;
- `data_fim`;
- `ativo`;
- `observacoes`.

## Tipos de vínculo

- `SOCIO`;
- `ADMINISTRADOR`;
- `RESPONSAVEL_LEGAL`;
- `CONTATO_COMERCIAL`;
- `CONTATO_FINANCEIRO`;
- `CONTATO_FISCAL`;
- `CONTATO_OPERACIONAL`;
- `PROCURADOR`;
- `EMPREGADO`;
- `PRESTADOR`;
- `REPRESENTANTE`;
- `OUTRO`.

## Regras

- Uma pessoa jurídica poderá possuir vários contatos físicos.
- Uma pessoa física poderá possuir vínculos com várias empresas.
- Deverá ser possível definir uma empresa principal para a pessoa física.
- Deverá ser possível encerrar um vínculo sem apagá-lo.
- Deverá ser preservado o histórico dos vínculos.
- Não permitir duplicidade de vínculos ativos iguais.
- Permitir mais de um responsável legal quando necessário.
- Permitir múltiplos contatos comerciais, financeiros e fiscais.
- Impedir a associação de uma pessoa jurídica com outra pessoa jurídica por meio deste modelo.
- Impedir a associação de uma pessoa física com outra pessoa física por meio deste modelo.

---

# 11. Endereços

Criar o modelo `Endereco`.

## Campos

- `id`;
- `logradouro`;
- `numero`;
- `complemento`;
- `bairro`;
- `cep`;
- `codigo_municipio`;
- `municipio`;
- `uf`;
- `pais`;
- `referencia`;
- `latitude`;
- `longitude`;
- `observacoes`.

Criar o modelo intermediário `ContatoEndereco`.

## Campos

- `contato`;
- `endereco`;
- `tipo_endereco`;
- `principal`;
- `correspondencia`;
- `cobranca`;
- `entrega`;
- `fiscal`;
- `prestacao_servico`;
- `data_inicio`;
- `data_fim`.

## Tipos de endereço

- `RESIDENCIAL`;
- `COMERCIAL`;
- `FISCAL`;
- `COBRANCA`;
- `ENTREGA`;
- `PRESTACAO_SERVICO`;
- `OUTRO`.

## Regras

- Um contato poderá possuir vários endereços.
- Um endereço poderá ter mais de uma finalidade.
- Deverá ser possível indicar o endereço principal.
- Deverá ser possível indicar o endereço fiscal.
- Deverá ser possível manter endereços antigos.
- Endereços utilizados em documentos ou contratos não deverão ser apagados fisicamente.

O endereço deverá permitir informar:

- Logradouro;
- Número;
- Complemento;
- Bairro;
- CEP;
- Código IBGE do município;
- Município;
- UF;
- País.

O `codigo_municipio` deverá ser armazenado separadamente do nome do município.

---

# 12. Telefones

Criar o modelo `ContatoTelefone`.

## Campos

- `id`;
- `contato`;
- `numero`;
- `tipo`;
- `principal`;
- `whatsapp`;
- `ramal`;
- `ativo`;
- `observacoes`.

## Tipos

- `CELULAR`;
- `FIXO`;
- `COMERCIAL`;
- `RESIDENCIAL`;
- `WHATSAPP`;
- `OUTRO`.

## Regras

- Permitir vários telefones por contato.
- Permitir marcar um telefone como principal.
- Permitir informar ramal.
- Normalizar o número antes de armazená-lo.
- Não apagar fisicamente telefones utilizados em históricos.

---

# 13. E-mails

Criar o modelo `ContatoEmail`.

## Campos

- `id`;
- `contato`;
- `email`;
- `tipo`;
- `principal`;
- `recebe_documentos`;
- `recebe_cobranca`;
- `recebe_comunicados`;
- `recebe_integracoes`;
- `ativo`;
- `observacoes`.

## Tipos

- `PESSOAL`;
- `COMERCIAL`;
- `FINANCEIRO`;
- `FISCAL`;
- `COBRANCA`;
- `DOCUMENTOS`;
- `OUTRO`.

## Regras

- Validar o formato do e-mail.
- Permitir vários e-mails por contato.
- Permitir indicar e-mail principal.
- Permitir indicar e-mail para documentos.
- Permitir indicar e-mail financeiro.
- Normalizar e-mails em letras minúsculas.
- Não excluir fisicamente e-mails utilizados em históricos.

---

# 14. Dados comerciais e financeiros

Criar o modelo `ContatoComercial`.

## Campos

- `contato`;
- `codigo_externo`;
- `limite_credito`;
- `condicao_pagamento`;
- `prazo_pagamento_dias`;
- `forma_pagamento_preferencial`;
- `banco`;
- `agencia`;
- `conta`;
- `tipo_conta`;
- `pix`;
- `classificacao_risco`;
- `vendedor_responsavel`;
- `centro_custo`;
- `categoria_financeira`;
- `observacoes_financeiras`.

## Regras

- Os dados bancários deverão possuir controle de acesso próprio.
- Não exibir dados bancários para usuários sem permissão.
- Registrar auditoria nas alterações financeiras.
- Permitir que clientes e fornecedores possuam configurações diferentes.
- Não tornar esses campos obrigatórios para todos os contatos.

---

# 15. Órgãos públicos

Criar o modelo `OrgaoPublico`.

## Campos

- `contato`;
- `esfera`;
- `poder`;
- `orgao_superior`;
- `codigo_unidade_gestora`;
- `codigo_siasg`;
- `codigo_ug`;
- `unidade_administrativa`;
- `responsavel_contrato`;
- `email_fiscal_contrato`;
- `exige_retencao`;
- `exige_empenho`;
- `numero_empenho`;
- `processo_administrativo`;
- `observacoes`.

## Esferas

- `MUNICIPAL`;
- `ESTADUAL`;
- `FEDERAL`;
- `OUTRA`.

## Poderes

- `EXECUTIVO`;
- `LEGISLATIVO`;
- `JUDICIARIO`;
- `MINISTERIO_PUBLICO`;
- `TRIBUNAL_DE_CONTAS`;
- `OUTRO`.

Nenhum campo específico de órgão público deverá ser obrigatório para os demais contatos.

---

# 16. Profissionais

Os contatos classificados como profissionais poderão possuir:

- Profissão;
- Registro profissional;
- Conselho profissional;
- UF do conselho;
- Especialidade;
- Tipo de contratação;
- Data de início;
- Data de término;
- Valor da hora;
- Percentual de comissão;
- Dados bancários;
- Documentos complementares;
- Observações profissionais.

## Conselhos profissionais

O sistema deverá permitir conselhos como:

- CREA;
- CRM;
- CRC;
- OAB;
- CAU;
- CRP;
- CREF;
- Outros.

O registro profissional não deverá ser confundido com:

- CPF;
- CNPJ;
- Inscrição estadual;
- Inscrição municipal.

---

# 17. Empreendimentos

Os contatos classificados como empreendimentos poderão utilizar o modelo `Empreendimento`.

## Campos sugeridos

- `contato`;
- `codigo_interno`;
- `descricao`;
- `tipo_empreendimento`;
- `data_inicio`;
- `data_prevista_termino`;
- `data_termino`;
- `responsavel`;
- `cliente_principal`;
- `endereco`;
- `status`;
- `observacoes`.

## Status

- `PLANEJADO`;
- `EM_ANDAMENTO`;
- `PAUSADO`;
- `CONCLUIDO`;
- `CANCELADO`;
- `ARQUIVADO`.

O empreendimento poderá ser associado a clientes, fornecedores, profissionais e parceiros por meio de relacionamentos específicos dos módulos correspondentes.

---

# 18. Preparação para futuras integrações fiscais

Embora o aplicativo de NFS-e não seja criado nesta etapa, o cadastro deverá possuir informações suficientes para futuras integrações fiscais.

Para pessoas jurídicas, manter:

- CNPJ;
- Razão social;
- Nome fantasia;
- Inscrição municipal;
- Inscrição estadual;
- Indicador de inscrição estadual;
- Código IBGE do município;
- Município;
- UF;
- Endereço fiscal;
- Regime tributário;
- Optante pelo Simples Nacional;
- Optante pelo SIMEI;
- Incentivador cultural;
- CNAE principal;
- CNAEs secundários;
- E-mail fiscal;
- E-mail para documentos;
- Telefone comercial.

Para pessoas físicas, manter:

- CPF;
- Nome completo;
- Nome social, quando aplicável;
- Endereço;
- Município;
- Código IBGE;
- UF;
- E-mail;
- Telefone.

O cadastro deverá permitir que os dados fiscais sejam consultados por módulos futuros, mas não deverá conter regras de emissão de notas nesta etapa.

---

# 19. Validações

## Contatos

- CPF válido;
- CNPJ válido;
- E-mail válido;
- CEP válido;
- UF válida;
- Código IBGE consistente;
- Nome obrigatório;
- Razão social obrigatória para pessoa jurídica;
- Documento único;
- Vínculos válidos;
- Ausência de autoassociação;
- Ausência de duplicidade de vínculo ativo;
- Endereço válido quando marcado como fiscal;
- Município compatível com a UF.

## Pessoas físicas

- CPF válido quando informado;
- Data de nascimento válida;
- Registro profissional consistente quando informado;
- UF do conselho válida;
- E-mail válido;
- Telefone normalizado.

## Pessoas jurídicas

- CNPJ válido quando informado;
- Razão social obrigatória;
- Regime tributário válido;
- Inscrição estadual compatível com o indicador;
- Código do município válido;
- CNAE com formato válido;
- Inscrição municipal sem caracteres inválidos;
- UF válida.

---

# 20. Exclusão lógica e histórico

O sistema deverá utilizar exclusão lógica para os principais registros.

Registros que possuam relacionamento com outros módulos não deverão ser excluídos fisicamente.

A exclusão lógica deverá:

- Marcar o registro como inativo;
- Preencher `deleted_at`;
- Registrar o usuário responsável;
- Registrar a data da operação;
- Impedir o uso em novos lançamentos;
- Permitir consulta por usuários autorizados;
- Preservar os relacionamentos existentes.

---

# 21. Auditoria

Registrar:

- Usuário que criou o contato;
- Usuário que alterou o contato;
- Usuário que alterou CPF ou CNPJ;
- Usuário que alterou inscrições fiscais;
- Usuário que criou ou encerrou vínculos;
- Usuário que alterou dados bancários;
- Data e hora da operação;
- Dados anteriores;
- Dados posteriores;
- Identificação técnica da operação, quando aplicável.

Dados sensíveis deverão possuir permissões específicas.

---

# 22. Interface com Django Templates, Tailwind CSS e HTMX

A interface deverá ser desenvolvida utilizando:

- Django Templates;
- Tailwind CSS;
- HTMX.

Não criar uma SPA para as funções administrativas comuns.

O Django deverá continuar responsável por:

- Renderização dos templates;
- Autenticação;
- Autorização;
- Validação;
- Regras de negócio;
- Persistência;
- Transações;
- Auditoria.

O HTMX deverá ser utilizado para as partes dinâmicas da interface.

## Operações com HTMX

- Pesquisa de contatos;
- Filtros;
- Paginação;
- Carregamento de detalhes;
- Inclusão de endereços;
- Edição de endereços;
- Exclusão lógica de endereços;
- Inclusão de telefones;
- Edição de telefones;
- Inclusão de e-mails;
- Edição de e-mails;
- Inclusão e remoção de vínculos;
- Pesquisa de pessoas físicas;
- Pesquisa de pessoas jurídicas;
- Atualização de municípios conforme a UF;
- Carregamento de campos específicos de pessoa física;
- Carregamento de campos específicos de pessoa jurídica;
- Exibição de mensagens;
- Abertura e fechamento de modais;
- Validação parcial de formulários.

## Atributos HTMX

Utilizar, quando apropriado:

- `hx-get`;
- `hx-post`;
- `hx-put`;
- `hx-delete`;
- `hx-target`;
- `hx-swap`;
- `hx-trigger`;
- `hx-indicator`;
- `hx-confirm`;
- `hx-include`.

As requisições HTMX deverão retornar fragments HTML quando somente parte da página precisar ser atualizada.

---

# 23. Organização dos templates

Utilizar estrutura semelhante a:

```text
templates/
├── base.html
├── components/
│   ├── _button.html
│   ├── _modal.html
│   ├── _alert.html
│   ├── _badge.html
│   ├── _pagination.html
│   └── _form_field.html
└── contatos/
    ├── lista.html
    ├── detalhe.html
    ├── formulario.html
    ├── confirmar_exclusao.html
    └── partials/
        ├── _contato_row.html
        ├── _contato_form.html
        ├── _pessoa_fisica_form.html
        ├── _pessoa_juridica_form.html
        ├── _endereco_form.html
        ├── _endereco_row.html
        ├── _telefone_form.html
        ├── _telefone_row.html
        ├── _email_form.html
        ├── _email_row.html
        ├── _vinculo_form.html
        ├── _vinculo_row.html
        ├── _resultados_busca.html
        └── _mensagens.html
```

Os fragments deverão:

- Ser pequenos;
- Ser reutilizáveis;
- Ter responsabilidade única;
- Não conter regras de negócio;
- Utilizar escaping automático;
- Receber dados explicitamente pelo contexto.

---

# 24. Indicadores de carregamento

Toda operação HTMX que possa demorar deverá apresentar indicador de carregamento.

Exemplos:

- Spinner;
- Texto “Carregando...”;
- Texto “Salvando...”;
- Botão desabilitado;
- Bloqueio contra duplo clique;
- Mensagem de sucesso;
- Mensagem de erro.

Os indicadores deverão utilizar classes Tailwind reutilizáveis.

---

# 25. Segurança

Todas as requisições deverão respeitar:

- Autenticação;
- Autorização;
- Proteção CSRF;
- Validação no servidor;
- Controle de acesso por objeto;
- Controle de acesso a dados sensíveis;
- Escaping automático dos templates;
- Proteção contra conteúdo HTML não confiável;
- Auditoria;
- Exclusão lógica.

O HTMX não deverá ser utilizado como mecanismo de segurança.

Os seguintes dados deverão possuir acesso restrito:

- CPF;
- RG;
- Data de nascimento;
- Dados bancários;
- Informações financeiras;
- Inscrições fiscais;
- Documentos anexados.

---

# 26. Acessibilidade

Os templates deverão possuir:

- Labels associados aos campos;
- Mensagens de erro acessíveis;
- Navegação por teclado;
- Contraste adequado;
- Foco após atualizações HTMX;
- Modais acessíveis;
- Botões com textos claros;
- Indicadores visuais e textuais;
- Tabelas responsivas;
- Formulários compatíveis com dispositivos móveis;
- Estados de erro claramente identificados.

---

# 27. Testes obrigatórios

Criar testes automatizados para:

- Criação de contato;
- Criação de pessoa física;
- Criação de pessoa jurídica;
- Validação de CPF;
- Validação de CNPJ;
- Duplicidade de CPF;
- Duplicidade de CNPJ;
- Papéis múltiplos;
- Criação de vínculos;
- Encerramento de vínculos;
- Empresa com vários contatos;
- Pessoa física com empresa principal;
- Endereços;
- Telefones;
- E-mails;
- Inscrições fiscais;
- Dados comerciais;
- Dados de órgãos públicos;
- Dados de profissionais;
- Exclusão lógica;
- Permissões;
- CSRF;
- Operações HTMX;
- Renderização de fragments;
- Auditoria;
- Campos obrigatórios;
- Consultas e filtros;
- Paginação.

---

# 28. Variáveis de ambiente

Utilizar variáveis de ambiente para:

```text
DJANGO_SECRET_KEY
DJANGO_DEBUG
DATABASE_URL
DJANGO_ALLOWED_HOSTS
```

Não armazenar credenciais ou informações sensíveis diretamente no código-fonte.

---

# 29. Entregáveis

O agente de codificação deverá entregar:

- Models;
- Migrations;
- Forms;
- Validators;
- Services;
- Views;
- URLs;
- Admin Django;
- Templates;
- Partials HTMX;
- Estilos Tailwind;
- Testes automatizados;
- Fixtures ou comando para carga dos tipos de contato;
- Arquivo `requirements.txt`;
- Documentação de instalação;
- Documentação das variáveis de ambiente;
- Documentação das regras de negócio;
- Documentação dos endpoints;
- Guia de execução dos testes.

Não deverá ser criado nesta etapa:

- Aplicativo `nfse`;
- Modelo `NFSe`;
- Modelo `NFSeItem`;
- Emissão de NFS-e;
- Cancelamento de NFS-e;
- Integração com Focus NFe;
- Consulta de autorização de notas;
- Geração de DANFSe;
- Rotinas de comunicação com prefeitura ou provedor fiscal.

A biblioteca `requests` poderá permanecer instalada no projeto para uso futuro, mas não deverá ser utilizada para emissão de NFS-e nesta etapa.

---

# 30. Critérios de integração com o ERPangea

A implementação será considerada adequada somente se:

1. O aplicativo respeitar a arquitetura existente do ERPangea.
2. O agente tiver analisado os aplicativos, modelos e componentes já existentes.
3. Não forem criados modelos duplicados para funcionalidades já existentes.
4. O aplicativo utilizar o sistema global de usuários e permissões.
5. O aplicativo respeitar o escopo de empresa, filial ou organização, quando existente.
6. As migrations não causarem perda de dados.
7. As URLs utilizarem namespaces e não conflitarem com URLs existentes.
8. Os templates utilizarem o layout e os componentes visuais globais.
9. O HTMX seguir o padrão já adotado pelo ERPangea.
10. Os serviços puderem ser utilizados por outros módulos.
11. Não forem criadas dependências circulares entre aplicativos.
12. Os testes existentes do ERPangea continuarem funcionando.
13. Os dados de contatos puderem ser utilizados por vendas, compras, contratos e financeiro.
14. O aplicativo documentar todos os pontos de integração com o projeto global.
15. O aplicativo permanecer preparado para futuras integrações fiscais sem criar o aplicativo de NFS-e nesta etapa.