# itens-numerados

Lista os itens numerados de transcrições de documentos — uma norma, um manual, um
regulamento — e confere a numeração deles, por programa. Serve para três coisas:

- achar o número que a extração do texto leu errado (o OCR que leu "7.143.1" no lugar de
  "7.13.1" aparece como número fora de sequência);
- dar a lista de tudo o que um documento numera, para outro programa conferir que nada
  ficou de fora;
- dividir o documento em grupos de tópicos do sumário, para dividir a leitura dele em
  partes.

Usa só a biblioteca padrão do Python e o `extrator_comum.py`, do
[extrator](../extrator/README.md), que divide a transcrição em páginas pelo mesmo modelo
de título que o extrator usa para escrevê-la. Na prateleira, ele é achado na pasta irmã
`extrator/`; numa cópia fora da prateleira, os dois ficam na mesma pasta.

## Como rodar

    python3 -I <prateleira>/itens-numerados/itens.py <configuração do extrator.json> <itens-numerados.json> <saída.json>

`--raiz <pasta>` diz de onde partem os caminhos das transcrições (padrão: a pasta do
terminal). A configuração do extrator é lida como o extrator a lê, contra o molde dela, e
dela se usa o padrão: o modelo do título de página, as marcas de destaque e os escapes. A
linha é lida como item ou entrada do sumário sem as marcas e sem os escapes, com o
caractere escapado no lugar. O padrão é conferido como no extrator: se uma marca pode se
confundir com o texto, é `ERRO`.

No fim, uma linha por documento, com quantos itens, grupos e problemas, e uma linha
`CONFERIR` por problema, com a linha da transcrição. Sai com código 1 quando há problema; a
saída é gravada assim mesmo, com os problemas. Com `ERRO` (uma expressão que não compila,
que diz o campo dela; uma informação que falta, um campo que o molde não conhece, uma faixa
fora das páginas, um grupo de tamanho zero, um padrão em que a marca se confunde com o
texto), nada é gravado.

## O que confere

- **A sequência:** cada número vem logo depois do anterior da mesma série — o próximo do
  mesmo nível (7.2 depois de 7.1), o primeiro filho (7.2.1 depois de 7.2) ou o próximo de
  um nível acima (8 depois de 7.2.1). O número que salta ou sai de ordem é
  `fora_de_sequencia`; o que aparece de novo é `repetido`.
- **O sumário:** cada entrada numerada do sumário tem o item no corpo
  (`sumario_sem_item`), e o título do item começa pelo título da entrada, sem contar
  espaços nem maiúsculas (`titulo_diferente`).

## A configuração (`itens-numerados.json`)

O molde está em `esquemas/itens-numerados.schema.json`.

| Chave | O que é |
| --- | --- |
| `formas.item` | as formas de uma linha de item no corpo, cada uma com a `expressao` (expressão regular com o grupo `numero` e, se houver, `titulo`), a `serie` e as opções abaixo |
| `formas.sumario` | as formas de uma entrada do sumário, do mesmo jeito |
| `formas.numero_sozinho` | opcional: a forma de uma linha do sumário que é só o número; ela se junta à linha seguinte |
| `formas.separador` | o que separa as partes do número de um item, como o ponto de 7.13.1 |
| `grupo` | quantas entradas do sumário vão em cada grupo |
| `documentos` | para cada documento, a `transcricao` e as faixas de páginas do arquivo do `sumario` e do `corpo`, cada faixa com `de` e `ate` |

O número de um item é uma sequência de partes separadas pelo separador, cada parte um
número ou uma letra (A = 1, B = 2). A sequência se confere dentro de cada série: as seções
numa, os anexos noutra, por exemplo.

Opções de uma forma de item:

- `linhas_do_titulo`: quando a linha só tem o número, quantas linhas seguintes, não vazias,
  fazem o título;
- `so_se_no_sumario`: o item só vale quando o sumário tem a entrada com o mesmo número e a
  linha começa pelo título dela. Assim, uma nota de rodapé numerada não passa por item.

## A saída

Um JSON com o molde `esquemas/itens-numerados-saida.schema.json`: para cada documento, os
`itens` (série, número, título, página do arquivo e linha), os `problemas` (tipo, número,
linha e o detalhe) e os `grupos` (os números dos itens de cada grupo e as páginas do
arquivo, da primeira à última).

## Testes

Em [testes/](testes/README.md).
