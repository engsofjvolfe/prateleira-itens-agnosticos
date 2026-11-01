# glossario

Grava o glossário de um projeto, ou confere que o gravado está em dia: cada termo que o
projeto define, em ordem alfabética, com a definição e a fonte que a dá, ou com o link para
o lugar do documento em que ele é definido. Serve a qualquer projeto que define os termos
que usa, numa lista com a definição tirada das fontes ou no próprio texto, com a marca do
HTML para o termo definido.

Usa só a biblioteca padrão do Python e cinco módulos de outras peças: o `extrator_comum.py`
e o `texto_comum.py`, do [extrator](../extrator/README.md), que leem a lista pelo molde dela
e põem os termos na forma em que se comparam; o `markdown_comum.py`, do
[documentos](../documentos/README.md#o-módulo-de-markdown), que lê os títulos e o texto
fora do código; e o `documento_gerado.py` e o `grava_ou_confere.py`, do
[grava-ou-confere](../grava-ou-confere/README.md), que leem o cabeçalho, conferem o arquivo
do glossário, montam o texto dele e o gravam, ou conferem que ele está em dia. Na
prateleira, eles são achados nas pastas irmãs; numa cópia fora da prateleira, na mesma
pasta do script.

## Como rodar

    python3 -I <prateleira>/glossario/glossario.py <definições.json> <cabeçalho.md> <glossário.md> [<documento.md>...] [--conferir]

- `<definições.json>`: a lista dos termos, só com dados (ver [A lista](#a-lista)).
- `<cabeçalho.md>`: o começo do glossário, como o título e a abertura.
- `<glossário.md>`: o glossário que o script grava, com as pastas que faltam.
- `<documento.md>...`: os documentos com as marcas `<dfn>`; o próprio glossário, se vier
  entre eles, fica de fora.
- `--conferir`: nada é gravado; o glossário gravado tem de ser o que o script gravaria
  agora.

## A lista

O molde está em `esquemas/glossario.schema.json`, com as regras de linha e de texto do
[molde comum](../extrator/README.md#o-molde-comum) do extrator:

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `termos` | a lista, que pode estar vazia; cada termo com o `termo`, a `definicao` e a `fonte` |
| `termo` | o termo, numa linha só, com alguma letra |
| `definicao` e `fonte` | textos com alguma letra, que podem ter mais de uma linha, como uma citação em bloco |

## As marcas

Um documento define um termo marcando-o com `<dfn>termo</dfn>`, a marca do HTML para "aqui
este termo é definido", fora dos blocos de código e do código na linha. A marca pode ter
atributos, ser escrita em maiúsculas e passar de uma linha para a outra; o termo é o texto
dela como aparece: sem as tags de dentro, com os espaços juntos e na forma Unicode NFC.

## O glossário

O cabeçalho, sem os espaços e as quebras do fim, e, para cada termo, em ordem alfabética
sem contar acentos nem maiúsculas, o título de segundo nível (`## `) com o termo, cuja
âncora é o endereço dele, e:

- o termo da lista: um parágrafo com a definição e outro com a fonte, como estão, sem os
  espaços e as quebras das pontas;
- o termo de uma marca: um parágrafo com o link para o lugar dela, a partir da pasta do
  glossário, entre `<` e `>` quando o caminho tem espaço ou parênteses. O lugar é a seção,
  o título mais perto acima da marca, também o da própria linha, de nível 2 em diante; ou o
  documento, quando o título mais perto é o de nível 1 ou não há título. O texto do link é
  o título do documento (o de nível 1, ou o caminho dele), com o da seção depois de ` › `,
  os dois como aparecem.

O termo que está na lista e numa marca sai só com a definição da lista. Os blocos se
separam por uma linha em branco, e o glossário termina com uma quebra de linha. Sem termo, o
glossário é só o cabeçalho. A mesma entrada dá sempre o mesmo glossário.

## A fonte

A fonte de cada definição vai para o glossário como está, num parágrafo próprio: a forma da
citação é a do projeto, e a conferência dela fica com a peça que confere citações, como o
[confere-citacoes](../confere-citacoes/README.md), rodado sobre o glossário gravado.

## Os problemas

São problema, e nada é gravado:

- o termo repetido na lista, sem contar maiúsculas, a forma Unicode (NFC) e os espaços;
- a marca vazia, também a que só tem tags e espaços;
- o termo marcado em mais de um lugar, sem contar maiúsculas, a forma Unicode e os espaços;
- dois títulos do glossário com a mesma âncora, como dois termos que só diferem na
  pontuação, ou um termo e um título do cabeçalho.

Cada problema sai numa linha `ERRO`: o da lista, com o caminho do valor nela, como
`/termos/3/termo`, e o do valor que ele repete; o de uma marca, com o documento e a linha
dela, em cada lugar; o da âncora, com o glossário e a âncora. Depois, um resumo com quantos
termos e quantos erros.

## Os códigos de saída

| Caso | Código |
| --- | --- |
| o glossário gravado, ou em dia com `--conferir` | 0 |
| problema; com `--conferir`, o glossário diferente ou que falta | 1 |
| a entrada que não serve, e então nada é gravado | 2 |

A entrada que não serve, que sai como `ERRO: <motivo>`: a lista, o cabeçalho ou um
documento que faltam ou não se leem em UTF-8; a lista que não é JSON ou que sai do molde; o
cabeçalho vazio; e o glossário que é a lista, o cabeçalho ou uma pasta.

## Testes

Em [testes/](testes/README.md).
