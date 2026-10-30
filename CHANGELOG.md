# Changelog

Todas as mudanças significativas da prateleira serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e a
prateleira segue o [Versionamento Semântico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [Não publicado]

### Adicionado

- `ganchos/leitura-do-terminal`: a função `depois_do_comando`, que acha nas palavras de um
  comando simples um comando de uma ou mais palavras, como `git grep`, também com outras
  palavras no meio, e a `comandos_achados`, que dá cada vez que um comando, ou um de dentro
  dele, roda um dos comandos procurados; o `busca-por-palavra` passa a usá-las.
- `ganchos/protocolo`: a função `anotacao`, que dá o arquivo em que um gancho anota o que
  guarda de uma sessão, ou de cada chave dela, como um documento, com o nome tirado do id
  da sessão e da chave; o `destino-da-limpeza` e o `regras-de-codigo` passam a usá-la.

### Modificado

- `ganchos/regras-de-codigo`: a anotação de cada sessão tem o nome tirado do id dela, como
  a do `destino-da-limpeza`, e o id com nome de caminho deixa de ser erro.

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
