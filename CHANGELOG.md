# Changelog

Todas as mudanças significativas da prateleira serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e a
prateleira segue o [Versionamento Semântico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [Não publicado]

### Adicionado

- `extrator`: o molde dos moldes (`esquemas/molde.schema.json`), que diz as palavras do
  JSON Schema que o leitor de molde do módulo comum entende e a forma do valor de cada uma;
  e o teste do módulo comum, com a lista de estragos dele.
- `extrator`: no módulo comum, a função `le_texto`, que lê um texto em UTF-8 com o erro que
  diz o arquivo, e a `conferido`, que confere contra um molde dados já lidos.
- `ganchos/leitura-do-terminal`: a função `depois_do_comando`, que acha nas palavras de um
  comando simples um comando de uma ou mais palavras, como `git grep`, também com outras
  palavras no meio, e a `comandos_achados`, que dá cada vez que um comando, ou um de dentro
  dele, roda um dos comandos procurados; o `busca-por-palavra` passa a usá-las.
- `ganchos/protocolo`: a função `anotacao`, que dá o arquivo em que um gancho anota o que
  guarda de uma sessão, ou de cada chave dela, como um documento, com o nome tirado do id
  da sessão e da chave; o `destino-da-limpeza` e o `regras-de-codigo` passam a usá-la.

### Modificado

- `confere-citacoes`, `confere-forma`, `copias-estragadas`, `custo-de-agentes` e
  `ganchos/protocolo`: o que o molde de cada um confere, como o campo que falta, o texto ou
  a lista vazios, os limites e a versão do protocolo, sai da conferência à mão, e o erro
  diz o caminho do valor.
- `confere-citacoes`: os pedaços de um trecho têm de estar na fonte na ordem do trecho, e
  cada supressão entre dois deles tem de omitir alguma coisa além das pontas e dos espaços.
- `extrator`: o leitor de molde do módulo comum confere o molde inteiro — o tipo, o valor
  fixo e a lista de valores, o tamanho, a forma do texto, os limites, os itens, os campos
  obrigatórios, o `allOf` e o `if`, com `$ref` para a raiz e para `$defs` — e diz o caminho
  de cada valor fora dele; antes, só acusava o campo que o molde não conhece. O próprio
  molde é conferido antes, contra o molde dos moldes.
- `ganchos/chamadas-permitidas`: a configuração e a lista das regras são lidas pelos moldes
  delas, em `esquemas/`, com o leitor do módulo comum, e as partes do evento também; o erro
  diz o caminho de cada valor fora do molde. Os dois arquivos passam a ter
  `"versao_schema": 1`.
- `ganchos/regras-de-codigo`: a anotação de cada sessão tem o nome tirado do id dela, como
  a do `destino-da-limpeza`, e o id com nome de caminho deixa de ser erro.
- `ganchos/regras-de-codigo`: a configuração é lida pelo leitor de molde do módulo comum,
  que diz o caminho de cada valor fora do molde, e não mais por uma conferência própria,
  que parava no primeiro.
- `itens-numerados`: o tamanho do grupo menor que 1 é pego pelo molde da configuração, que
  diz o caminho do campo.
- `itens-numerados`: a expressão do número sozinho e a de cada forma se compilam pelo
  módulo comum, e a que não compila é erro que diz o campo dela.
- `moldes`: o molde da forma e o das regras pegam o campo que falta, o valor de outro tipo
  e o texto ou a lista vazios, com o caminho do valor; a forma e as regras conferem à mão
  só o que o molde não vê, e a entrada errada deixa de ser pega pelo `KeyError` e pelo
  `TypeError` do Python.

### Removido

- `ganchos/chamadas-permitidas`: o `dados.py`, que conferia os arquivos da peça valor por
  valor.

## [0.1.0] - 2026-10-29

### Adicionado

- `confere-citacoes`: confere cada trecho citado num texto Markdown contra a transcrição da
  fonte, letra por letra, e contra as páginas citadas.
- `confere-forma`: confere a forma de documentos Markdown contra uma descrição dela.
- `copia-para-projeto`: leva os arquivos de uma peça para um projeto e confere que as cópias
  estão em dia.
- `copias-estragadas`: prova que o teste de uma peça pega os defeitos dela.
- `custo-de-agentes`: mostra o uso de tokens de cada transcrição de sessão.
- `documentos`: confere os links internos dos documentos de um repositório git e as linhas
  que passam de um limite de caracteres.
- `extrator`: tira o texto de documentos e grava a transcrição de cada um, página por
  página; e o módulo comum que lê dados JSON pelo molde.
- `ganchos`: as regras de código, a barreira à busca por palavra, o destino da limpeza, a
  cancela e o registro das chamadas de ferramenta, a leitura do comando de terminal e a
  leitura do protocolo dos ganchos de cada programa.
- `grava-ou-confere`: grava um documento gerado a partir de dados, ou confere que o gravado
  está em dia.
- `historico-de-arquivo`: tira das transcrições das sessões cada leitura e cada gravação de
  um arquivo, na ordem do tempo.
- `itens-numerados`: lista os itens numerados de uma transcrição e confere a numeração.
- `marcas`: confere se cada código escondido num comentário de um texto Markdown está no
  lugar em que deveria estar.
- `moldes`: diz em que documento cada trecho das análises cai, e conta e separa os trechos.
- `texto-em-comum`: diz quais arquivos de uma pasta têm texto igual ao de outras pastas.
- O teste de cada peça com código, com a lista de estragos que ele pega.
- O README, com o índice das peças e a regra das versões; a organização (`organizacao/`); o
  relatório das peças contra as regras; este changelog e a lista do que falta.
