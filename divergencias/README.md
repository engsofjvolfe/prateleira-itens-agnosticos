# divergencias

Confere a lista dos fatos que as fontes dizem de formas diferentes e grava o documento
deles: para cada fato, a forma que o material ensina e as outras, cada uma com o que diz e
a fonte que a dá. Serve a qualquer projeto em que duas fontes, ou duas passagens de uma
mesma fonte, dizem um fato de formas diferentes e o material ensina uma delas, sem perder
as outras.

Usa só a biblioteca padrão do Python e quatro módulos de outras peças: o `extrator_comum.py`
e o `texto_comum.py`, do [extrator](../extrator/README.md), que leem a lista pelo molde dela
e põem os textos na forma em que se comparam, e o `documento_gerado.py` e o
`grava_ou_confere.py`, do [grava-ou-confere](../grava-ou-confere/README.md), que leem o
cabeçalho, conferem o arquivo do documento, montam o texto dele e o gravam, ou conferem que
ele está em dia. Na prateleira, eles são achados nas pastas irmãs; numa cópia fora da
prateleira, na mesma pasta do script.

## Como rodar

    python3 -I <prateleira>/divergencias/divergencias.py <divergencias.json> <cabeçalho.md> <documento.md> \
        --ensinada <rótulo> --outra <rótulo> [--conferir]

- `<divergencias.json>`: a lista, só com dados (ver [A lista](#a-lista)).
- `<cabeçalho.md>`: o começo do documento, como o título e a abertura.
- `<documento.md>`: o documento que o script grava, com as pastas que faltam.
- `--ensinada` e `--outra`: o rótulo da forma ensinada e o de cada uma das outras, como vão
  no documento, com a marcação que o projeto quiser, como `**Ensinada:**`.
- `--conferir`: nada é gravado; o documento gravado tem de ser o que o script gravaria
  agora.

O texto do documento, o cabeçalho e os rótulos, vem do projeto, no comando; a lista só tem
dados.

## A lista

O molde está em `esquemas/divergencias.schema.json`, com as regras de linha e de texto do
[molde comum](../extrator/README.md#o-molde-comum) do extrator:

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `divergencias` | a lista, que pode estar vazia; cada divergência com o `fato`, a forma `ensinada` e as `outras`, uma ou mais |
| `fato` | o fato que as fontes dizem de formas diferentes, numa linha só, com alguma letra |
| `ensinada` e cada uma das `outras` | a forma: o que ela `diz`, numa linha só, com alguma letra, e a `fonte`, um texto com alguma letra, que pode ter mais de uma linha |

## O documento

O cabeçalho, sem os espaços e as quebras do fim, e, para cada divergência, na ordem da
lista:

- o título de segundo nível (`## `) com o fato;
- para cada forma, a ensinada primeiro e as outras na ordem delas, um parágrafo com o
  rótulo dela, um espaço e o que ela diz, e um parágrafo com a fonte, sem os espaços e as
  quebras das pontas.

Os blocos se separam por uma linha em branco, e o documento termina com uma quebra de
linha. Sem divergência, o documento é só o cabeçalho. A mesma entrada dá sempre o mesmo
documento.

## A fonte

A fonte de cada forma vai para o documento como está, num parágrafo próprio: a forma da
citação é a do projeto, e a conferência dela fica com a peça que confere citações. Com o
[confere-citacoes](../confere-citacoes/README.md), a fonte é a citação na forma que a
configuração dele reconhece, como a linha de referência seguida da linha do trecho, e o
documento gravado se confere como qualquer texto:

    python3 -I <prateleira>/confere-citacoes/confere_citacoes.py <configuração.json> <pasta das fontes> <documento.md>

## Os problemas

São problema, e nada é gravado:

- o fato repetido, sem contar maiúsculas, a forma Unicode (NFC) e os espaços;
- a forma que diz o mesmo que outra do mesmo fato, sem contar a forma Unicode e os
  espaços; as maiúsculas contam.

Cada problema sai numa linha `ERRO <lista>: <caminho>: <motivo>`, com o caminho do valor na
lista, como `/divergencias/3/fato`, e o do valor que ele repete, seguida de um resumo com
quantas divergências e quantos erros.

## Os códigos de saída

| Caso | Código |
| --- | --- |
| o documento gravado, ou em dia com `--conferir` | 0 |
| problema na lista; com `--conferir`, o documento diferente ou que falta | 1 |
| a entrada que não serve, e então nada é gravado | 2 |

A entrada que não serve, que sai como `ERRO: <motivo>`: a lista ou o cabeçalho que não se
leem em UTF-8; a lista que não é JSON ou que sai do molde (campo que ele não conhece, campo
que falta, valor fora da forma); o cabeçalho vazio; o rótulo que falta, ou que não é uma
linha só com alguma letra, pelo molde `esquemas/rotulos.schema.json`, que aponta a regra de
linha do molde comum; e o documento que é a lista, o cabeçalho ou uma pasta.

## Testes

Em [testes/](testes/README.md).
