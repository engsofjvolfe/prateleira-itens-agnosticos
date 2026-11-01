# extrator

Tira o texto de documentos (PDF, HTML, XML, JSON) por programa e grava a transcrição de
cada um, página por página, na forma que o projeto usa. O texto não é lido nem copiado à
mão: o que sai é o texto do próprio arquivo.

Usa só a biblioteca padrão do Python. Nenhum caminho, nenhuma marca da transcrição e
nenhum tipo de arquivo fica no código: tudo vem de dois arquivos de dados.

## Como rodar

    python3 -I <prateleira>/extrator/extrator.py <configuração.json> <documentos.json>

- `--raiz <pasta>`: de onde partem os caminhos da lista de documentos (padrão: a pasta do
  terminal).
- `--so <arquivo>`: só esse documento, pelo arquivo ou pela transcrição; pode repetir.
- `--substituir`: grava por cima da transcrição que já existe. O que vem antes do primeiro
  título de página dela, como o registro de onde ela veio, fica como está.

Sem `--substituir`, a transcrição que já existe não é tocada. Com qualquer `ERRO`, em
qualquer documento, sai com código 2 e nada é gravado. No fim, uma linha por transcrição
gravada: quantas páginas, quantas sem texto, quantas lidas pelo OCR, quantas trocas e
quantas correções; e sai com código 0.

## O que precisa estar instalado

- Para PDF: o Poppler (`pdfinfo`, `pdftotext`, `pdftoppm` e, com destaques, `pdftohtml`).
- Para página lida pelo OCR: o Tesseract, com os dados do idioma.

## A configuração

Os moldes estão em `esquemas/`: `extrator.schema.json` para a configuração e
`extracao.schema.json` para a lista de documentos. Lá estão também o molde dos moldes,
`molde.schema.json`, do [módulo comum](#o-módulo-comum), e o
[molde comum](#o-molde-comum), `comum.schema.json`.

`padrao` diz a forma da transcrição:

| Chave | O que é |
| --- | --- |
| `titulo_pagina` | o título de cada página, com `{rotulo}` e `{arquivo}` (a posição da página no arquivo) |
| `rotulo_numerada` | o rótulo da página com número impresso, com `{numero}` |
| `rotulo_sem_numero` | o rótulo da página sem número impresso |
| `rotulo_sem_paginas` | o rótulo do documento que não tem páginas, como uma página da internet |
| `sem_texto` | a linha da página sem nenhum texto |
| `escape`, `escapar`, `escapar_no_comeco` | o sinal de escape e os caracteres que o recebem, cada um um caractere só: em qualquer lugar da linha, ou só no começo dela |
| `tabela` | a forma da tabela: `inicio`, `meio` e `fim` de cada linha e o `separador` da linha depois da primeira |
| `destaques` | opcional: as marcas de cada destaque, como `negrito`, `italico` e `riscado`, cada uma com o que `abre` e o que `fecha`; precisa existir quando um leitor traz destaques. As marcas vão só onde o destaque muda: as que fecham, na ordem contrária à da lista, e depois as que abrem, na ordem da lista. O espaço fica só com o destaque dos dois lados dele, assim a marca fica colada ao texto |

O padrão é conferido antes de tudo, e é `ERRO` quando uma marca pode se confundir com o
texto: um caractere das marcas de destaque, ou o próprio escape, fora de `escapar`; o escape
dentro de uma marca de destaque; a mesma marca em dois destaques; a marca entre células
sem nenhum caractere de `escapar`. Também é `ERRO`, ao escrever, a linha do texto que se lê
como título de página e a página cujo texto é a marca de página sem texto.

`trocas`, opcional, diz textos que a leitura dá e o que vai no lugar deles, em todo
documento: a ligadura tipográfica pelas letras dela, por exemplo. As trocas se fazem antes
de escrever, numa passada só, a mais longa primeiro, e o que uma troca escreve não é
trocado de novo. A troca da configuração que não acha nada num documento não é erro,
porque ela vale para todos.

`leitores` diz qual leitor lê qual tipo de arquivo: para cada leitor, pelo nome, as
`extensoes` dele e as `opcoes` padrão. Com `modulo`, um leitor usa o programa de outro com
outras opções — dois perfis do leitor de marcação, um para HTML e outro para o XML de
artigos, por exemplo.

## Os documentos

Uma lista, `documentos`, com um item por documento:

| Chave | O que é |
| --- | --- |
| `arquivo` | o documento |
| `saida` | a transcrição a gravar |
| `leitor` | opcional: o leitor, quando a extensão não basta |
| `opcoes` | opcional: as opções que valem por cima das do leitor |
| `numeracao` | opcional, só em documento com páginas: as faixas de páginas com número impresso, cada uma com `de` e `ate` (posições no arquivo), o `estilo` (`arabico`, `romano_minusculo` ou `romano_maiusculo`) e o número impresso da primeira, `primeiro`. Página fora das faixas leva o rótulo de sem número |
| `trocas` | opcional: as trocas só deste documento, do mesmo jeito das da configuração, como o símbolo que uma fonte do documento guarda com o código errado. A mesma troca aqui e na configuração é `ERRO`, e a troca do documento que não acha nada também |
| `correcoes` | opcional: as correções da leitura, cada uma com a `pagina` (posição no arquivo), o texto que a leitura deu (`de`), o que o documento diz (`para`), conferido na imagem da página, e quantas `vezes` o texto lido aparece na página (padrão 1). Elas se aplicam a cada extração, na ordem da lista; se o texto lido aparece outro número de vezes, porque a leitura mudou, é `ERRO` e nada é gravado |

## Os leitores

Cada leitor é um arquivo `leitor_<nome>.py` nesta pasta. O começo de cada um diz as opções
dele, uma por uma.

- **`pdf`** — a camada de texto do PDF, página por página. As páginas das faixas de `ocr`
  são lidas pelo Tesseract na imagem da página, para o PDF cujo texto não se lê. Quais
  páginas vão pelo OCR é dado do documento, decidido depois de ler o texto que sai. Com
  `destaques` (as etiquetas com que o `pdftohtml` marca a fonte de um trecho, `b` e `i`,
  cada uma com o nome do destaque no padrão), traz o negrito e o itálico que o próprio
  PDF marca, pela posição dos
  trechos destacados na página, tanto na camada de texto quanto no OCR; só a pontuação
  das pontas de uma palavra pode ficar fora do destaque dela. Um trecho do PDF que mistura
  partes com destaques diferentes é `ERRO`. A palavra partida no fim da linha fica como
  está, com o hífen.
- **`marcacao`** — HTML, XHTML e XML: um bloco por linha, com as etiquetas de bloco, as
  ignoradas e a parte do documento que conta dadas nas opções; a tabela sai como tabela.
  Com `destaques`, o texto dentro das etiquetas dadas sai com o destaque, como o texto
  riscado de uma lei. Sai uma página só.
- **`json`** — um documento cujo texto está numa lista de partes, como a resposta de um
  serviço de atos normativos; o texto de cada parte passa por outro leitor, o que as
  opções disserem, e os textos de fora das partes que as opções pedirem, como o título do
  ato, vêm antes delas. Parte sem texto em nenhum dos campos dados é erro. Sai uma página
  só.

**Um tipo de arquivo novo** é um leitor novo, `leitor_<nome>.py`, com
`ler(arquivo, opcoes, contexto)`, e o nome dele, com as extensões e as opções, na
configuração; os outros leitores não mudam. Uma extensão sem leitor é `ERRO`.

## O que não entra

O texto escrito dentro de uma imagem (uma figura num PDF, um logotipo numa página da
internet) não entra: o extrator lê o texto que o arquivo guarda como texto, e, no PDF, a
página inteira pelo OCR quando ela é pedida.

## O módulo comum

O `extrator_comum.py` guarda o que o extrator, os leitores dele e outras peças da prateleira
fazem do mesmo jeito. Não se roda: as peças o importam da pasta irmã `extrator/` ou da
própria pasta (numa cópia fora da prateleira, ao lado do script, com a pasta `esquemas/`
dele). O que as outras peças usam:

| Função | O que faz |
| --- | --- |
| `le_conferido(arquivo, molde)` | os dados de um arquivo JSON, conferidos contra o molde (JSON Schema), com `ErroDeDados` que diz o arquivo, o molde e o caminho de cada valor fora dele |
| `conferido(dados, molde, nome)` | o mesmo, com dados já lidos, como as partes de um evento; o erro diz o nome dado a eles |
| `fora_do_molde(dados, molde)` | o caminho e o motivo de cada valor dos dados fora do molde, todos, não só o primeiro |
| `le_texto(arquivo)` | o texto de um arquivo em UTF-8, com `ErroDeDados` que diz o arquivo quando ele falta ou não se lê |
| `le_json(arquivo)` | os dados de um arquivo JSON em UTF-8, sem molde, com `ErroDeDados` que diz o arquivo quando ele falta ou não se lê como JSON |
| `campo(dados, "a/b", tipo)` | o valor no caminho, do tipo pedido (um tipo ou uma tupla), com `ErroDeDados` que diz o caminho quando ele falta ou é de outro tipo; um booleano só vale quando o tipo pedido é `bool` |
| `expressao(dados, "a/b")` | a expressão regular do campo, compilada, com `ErroDeDados` que diz o caminho quando não compila |
| `compila(texto, onde)` | a expressão regular de um texto, compilada, com `ErroDeDados` que diz onde ela está quando não compila, para a expressão que não está num campo só, como a de uma lista |
| `codificacao(dados, "a/b")` | a codificação do campo, quando o Python a conhece, com `ErroDeDados` que diz o caminho e a codificação quando ela não existe |
| `repetidos(valores)` | os valores que aparecem mais de uma vez na lista, cada um uma vez, em ordem; nenhum quando nada se repete |
| `paginas_da_transcricao(texto, modelo)` | as páginas de uma transcrição pelo modelo do título de página (`{rotulo}` e `{arquivo}`), cada uma com as linhas numeradas |
| `preenche(modelo, campo=valor)` | o modelo com cada `{campo}` trocado; campo sem valor é `ErroDeDados` |

O leitor de molde entende o que o molde dos moldes, `esquemas/molde.schema.json`, diz, e
confere cada molde contra ele antes de usá-lo: o molde com uma palavra que o leitor não
entende, de outro dialeto que não o 2020-12, ou com um valor que não é da forma que a
palavra pede é `ErroDeDados`, que diz o lugar no molde. Ele confere `type`, `const` e
`enum`, `minLength` e `maxLength` (em letras), `pattern`, `minimum` e `maximum`,
`minItems`, `maxItems`, `uniqueItems` e `items`, `required`, `properties`,
`additionalProperties`, `minProperties` e `maxProperties`, `allOf`, `if`, `then` e `else`;
o `$ref` vai à raiz (`#`), a um molde de `$defs` (`#/$defs/nome`) ou, com o nome de um
molde comum antes do `#` (`comum.schema.json#/$defs/nome`), a um molde de `$defs` dele (ver
[O molde comum](#o-molde-comum)). As anotações (`$schema`, `$id`, `$comment`, `title`,
`description`, `default` e `examples`) não conferem nada. Duas diferenças do JSON Schema: o
`pattern` é a expressão regular do Python, buscada no texto, e o inteiro é o número escrito
sem ponto, como o Python o lê (`1.0` não é inteiro). O tipo que o leitor não conhece, a
referência para o que o molde não tem ou que volta a ela mesma, também passando por um molde
comum, o molde comum que falta ou que sai do molde dos moldes e a forma que não compila
também são `ErroDeDados`. Uma palavra nova é uma linha no molde dos moldes e o código que a
confere, com o caso dela no teste.

## O molde comum

O que os moldes de várias peças pedem do mesmo jeito fica num molde comum, só com `$defs`,
e cada molde o aponta pelo `$ref`, sem repetir a regra. O molde comum se acha pelo nome, só
de letras minúsculas, números e hífen, com `.schema.json` no fim: primeiro na pasta do molde
que o aponta e, senão, em `esquemas/`, aqui. Dentro dele, `#` é ele mesmo. Ele é conferido
contra o molde dos moldes, como qualquer molde.

O `esquemas/comum.schema.json` traz:

| Definição | O que pede |
| --- | --- |
| `linha` | um texto de uma linha só, com alguma letra |
| `texto` | um texto com alguma letra, que pode ter mais de uma linha |

## O módulo de texto

O `texto_comum.py` guarda o que as peças da prateleira fazem do mesmo jeito com um texto.
Não se roda: as peças o importam da pasta irmã `extrator/` ou da própria pasta (numa cópia
fora da prateleira, ao lado do script). Usa só a biblioteca padrão do Python.

| Função | O que faz |
| --- | --- |
| `nfc(texto)` | o texto na forma Unicode NFC, em que a mesma letra se escreve sempre do mesmo jeito: a letra com acento, escrita como um caractere só ou como a letra e o acento separados, vira um caractere só; o caractere de compatibilidade, como uma ligadura, fica como está |
| `espacos_juntos(texto)` | o texto com cada trecho de espaços (qualquer espaço do Unicode, com as quebras de linha e as tabulações) virando um espaço só, sem espaço nas pontas; as letras ficam como estão |

## Testes

Em [testes/](testes/README.md).
