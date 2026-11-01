# Changelog

Todas as mudanças significativas da prateleira serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e a
prateleira segue o [Versionamento Semântico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).

## [Não publicado]

### Adicionado

- `confere-forma`: o `marcas-de-ia.json`, com as marcas que uma ferramenta de IA deixa num
  texto (o caractere invisível ou o espaço especial, e o resto de citação), para qualquer
  projeto dar ao conferidor ao lado dos padrões dele.
- `dicionario-das-duvidas`: confere os códigos dos títulos de um dicionário das dúvidas (só
  códigos entre as marcas, cada um com as partes na forma dada, nenhum o começo de outro, em
  ordem natural), com a forma dos códigos na configuração; e o teste, com a lista de
  estragos dele.
- `divergencias`: confere a lista dos fatos que as fontes dizem de formas diferentes, cada
  um com a forma que o material ensina e as outras, cada forma com a fonte, e grava o
  documento deles, ou confere que o gravado está em dia; e o teste, com a lista de estragos
  dele.
- `documentos`: o teste do `linhas_longas.py`, com a lista de estragos dele.
- `documentos`: o módulo comum de Markdown, `markdown_comum.py`, que lê um texto Markdown como
  o GitHub o lê: as linhas fora dos blocos de código, o texto sem o código, a âncora de um
  título, os títulos, com a linha, o nível e a âncora de cada um, e os marcadores; e o teste
  dele, com a lista de estragos. O `confere_links.py`, que fazia isso por conta própria, passa
  a usá-lo.
- `extrator`: o molde dos moldes (`esquemas/molde.schema.json`), que diz as palavras do
  JSON Schema que o leitor de molde do módulo comum entende e a forma do valor de cada uma;
  e o teste do módulo comum, com a lista de estragos dele.
- `extrator`: no módulo comum, a função `le_texto`, que lê um texto em UTF-8 com o erro que
  diz o arquivo, e a `conferido`, que confere contra um molde dados já lidos. O
  `confere-citacoes`, o `confere-forma`, o `extrator` (na transcrição que já existe), o
  `itens-numerados`, o `moldes` e os ganchos `busca-por-palavra`, `destino-da-limpeza` e
  `regras-de-codigo`, que liam os textos por conta própria, passam a usar a `le_texto`.
- `extrator`: no módulo comum, a função `codificacao`, que dá a codificação de um campo e
  confere que o Python a conhece, com o erro que diz o caminho; o `custo-de-agentes` e o
  `historico-de-arquivo`, que conferiam a codificação cada um por conta própria, passam a
  usá-la.
- `extrator`: no módulo comum, a função `repetidos`, que dá os valores que aparecem mais de
  uma vez numa lista; o próprio `extrator`, o `copias-estragadas`, o `historico-de-arquivo`,
  o `marcas`, o `moldes`, o `ganchos/chamadas-permitidas` e o `ganchos/protocolo`, que
  achavam os repetidos cada um por conta própria, passam a usá-la.
- `extrator`: o módulo de texto comum, `texto_comum.py`, com a função `nfc`, que passa o
  texto para a forma Unicode NFC, e a `espacos_juntos`, que junta cada trecho de espaços
  num espaço só; e o teste dele, com a lista de estragos. O leitor de marcação do
  `extrator`, o `confere-citacoes`, o `custo-de-agentes`, o `itens-numerados`, o `marcas`, o
  `moldes` e o `texto-em-comum`, que faziam isso cada um por conta própria, passam a usá-lo.
- `extrator`: o molde comum, `esquemas/comum.schema.json`, com as regras que os moldes de
  várias peças pedem do mesmo jeito (`linha`, um texto de uma linha só com alguma letra, e
  `texto`, um texto com alguma letra), e, no leitor de molde, o `$ref` para um molde comum
  pelo nome, como `comum.schema.json#/$defs/linha`, achado na pasta do molde que o aponta
  ou na pasta dos moldes. O `confere-forma`, nos arquivos de padrões proibidos, o
  `divergencias`, também nos rótulos do comando, e o `glossario` o usam.
- `ganchos/leitura-do-terminal`: a função `depois_do_comando`, que acha nas palavras de um
  comando simples um comando de uma ou mais palavras, como `git grep`, também com outras
  palavras no meio, e a `comandos_achados`, que dá cada vez que um comando, ou um de dentro
  dele, roda um dos comandos procurados; o `busca-por-palavra` passa a usá-las.
- `ganchos/leitura-do-terminal`: a configuração, com os prefixos do shell, e o molde dela; a
  de uso geral fica na peça, e a função `prefixos_do_terminal` a lê pelo molde, com o
  módulo comum.
- `ganchos/protocolo`: a função `anotacao`, que dá o arquivo em que um gancho anota o que
  guarda de uma sessão, ou de cada chave dela, como um documento, com o nome tirado do id
  da sessão e da chave; o `destino-da-limpeza` e o `regras-de-codigo` passam a usá-la.
- `glossario`: grava o glossário de um projeto, ou confere que o gravado está em dia: os
  termos da lista das definições, com a definição e a fonte, e os que os documentos marcam
  com `<dfn>`, com o link para o lugar da marca, em ordem alfabética, cada um num título; e
  o teste, com a lista de estragos dele.
- `grava-ou-confere`: o módulo `documento_gerado.py`, que lê o cabeçalho de um documento
  gerado, que não pode estar vazio, confere que o arquivo dele não é uma das entradas nem uma
  pasta e monta o texto, com o cabeçalho e os blocos; e o teste dele, com a lista de
  estragos. O `divergencias` e o `glossario` o usam.

### Modificado

- `confere-citacoes`, `confere-forma`, `copias-estragadas`, `custo-de-agentes` e
  `ganchos/protocolo`: o que o molde de cada um confere, como o campo que falta, o texto ou
  a lista vazios, os limites e a versão do protocolo, sai da conferência à mão, e o erro
  diz o caminho do valor.
- `confere-citacoes`: os pedaços de um trecho têm de estar na fonte na ordem do trecho, e
  cada supressão entre dois deles tem de omitir alguma coisa além das pontas e dos espaços.
- `confere-citacoes`, `custo-de-agentes`, `itens-numerados`, `marcas`, `moldes` e
  `texto-em-comum`: precisam do `texto_comum.py`, do `extrator`, na pasta irmã ou na mesma
  pasta.
- `confere-forma`: os padrões proibidos saem da configuração e vêm de arquivos de dados
  próprios, com o molde `esquemas/proibidos.schema.json`, dados pelo `--proibidos`, que pode
  se repetir; as regras de todos se somam, e duas com o mesmo nome são erro.
- `copia-para-projeto`, `copias-estragadas`, `documentos` (o `linhas_longas.py`),
  `extrator`, `historico-de-arquivo`, `itens-numerados` e `moldes`: a entrada que não serve
  sai com código 2, e não mais com 1, que fica para o problema achado; o
  `historico-de-arquivo` escreve o `ERRO` na saída padrão, como as outras peças.
- `copia-para-projeto`: lê os arquivos pelo `le_texto` do módulo comum e precisa do
  `extrator_comum.py`, do `extrator`, na pasta irmã ou na mesma pasta.
- `documentos`: na forma de uma peça. O `teste_linhas_longas.py`, que não é teste, passa a
  se chamar `linhas_longas.py`; os testes ficam em `testes/`, com o README deles, e o dos
  links sorteia os dados e confere regras, e não mais as linhas de saída prontas.
- `documentos`: o `linhas_longas.py` mostra cada linha acima do limite como
  `ERRO arquivo:linha: motivo`, com o tamanho dela, e um resumo no fim, como as outras
  peças; o `confere_links.py` escreve o `ERRO` da pasta sem git na saída padrão, e não mais
  na de erros.
- `documentos`: lê os textos pelo `le_texto` do módulo comum e precisa do
  `extrator_comum.py`, do `extrator`, na pasta irmã ou na mesma pasta.
- `extrator`: o leitor de molde do módulo comum confere o molde inteiro — o tipo, o valor
  fixo e a lista de valores, o tamanho, a forma do texto, os limites, os itens, os campos
  obrigatórios, o `allOf` e o `if`, com `$ref` para a raiz e para `$defs` — e diz o caminho
  de cada valor fora dele; antes, só acusava o campo que o molde não conhece. O próprio
  molde é conferido antes, contra o molde dos moldes.
- `ganchos/busca-por-palavra` e `ganchos/regras-de-codigo`: os prefixos do shell saem da
  configuração de cada um e vêm da configuração da `ganchos/leitura-do-terminal`, dada no
  `--terminal`, que passa a ser pedido.
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
- `marcas` e as peças comuns do `moldes` (`analises.py`, `limite.py` e `tabela.py`):
  precisam do `extrator_comum.py`, do `extrator`, na pasta irmã ou na mesma pasta.
- `moldes`: o molde da forma e o das regras pegam o campo que falta, o valor de outro tipo
  e o texto ou a lista vazios, com o caminho do valor; a forma e as regras conferem à mão
  só o que o molde não vê, e a entrada errada deixa de ser pega pelo `KeyError` e pelo
  `TypeError` do Python.

### Removido

- `ganchos/chamadas-permitidas`: o `dados.py`, que conferia os arquivos da peça valor por
  valor.

### Corrigido

- `copia-para-projeto` e `documentos`: o script de referência que não existe, no
  `copia-para-projeto`, e o limite que não é um inteiro de 1 para cima, no
  `linhas_longas.py`, dão `ERRO`, com código 2; antes, o erro do Python, ou nenhum erro com
  o limite abaixo de 1.
- `documentos`: o arquivo que não se lê em UTF-8, no `linhas_longas.py`, e o documento, ou
  o Markdown de destino de uma âncora, que não se lê em UTF-8, no `confere_links.py`, dão
  `ERRO`, que diz o arquivo, com código 2; antes, o erro do Python.
- `historico-de-arquivo`: duas ferramentas com o mesmo nome na configuração são erro, que
  diz o nome; antes, a última valia.
- `itens-numerados` e `moldes`: a transcrição, ou a análise, que não se lê em UTF-8 dá o
  erro que diz o arquivo; antes, o erro trazia só a mensagem do Python.

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
