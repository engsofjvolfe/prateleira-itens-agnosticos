# dicionario-das-duvidas

Confere os códigos dos títulos de um dicionário das dúvidas: o documento Markdown em que um
projeto guarda as dúvidas que as fontes deixam, cada uma sob um título com os códigos do que
ela toca e com as respostas que teve. A busca por um código só acha as dúvidas dele quando
todo título segue a mesma regra, e é essa regra que a peça confere. Serve a qualquer projeto
que guarda dúvidas sob códigos, como os de uma aula, de uma página ou de um trecho, para a
mesma informação não se repetir em dois lugares.

Usa só a biblioteca padrão do Python e dois módulos de outras peças: o `extrator_comum.py`,
do [extrator](../extrator/README.md), que lê a configuração pelo molde dela e os dicionários
em UTF-8, e o `markdown_comum.py`, do [documentos](../documentos/README.md#o-módulo-de-markdown),
que separa as linhas dos blocos de código. Na prateleira, eles são achados nas pastas
irmãs; numa cópia fora da prateleira, na mesma pasta do script.

## Como rodar

    python3 -I <prateleira>/dicionario-das-duvidas/confere_dicionario.py <configuração.json> <dicionário.md>...

Mostra uma linha `ERRO arquivo:linha: motivo` por problema, na ordem dos dicionários e das
linhas, e um resumo com quantos dicionários, títulos e erros. Sai com código 0 sem problema,
1 com problema e 2 quando a configuração ou um dicionário não serve; então nada é conferido.

## A regra do título

Cada dúvida começa numa linha fora dos blocos de código que começa pelo `titulo` da
configuração. O resto da linha segue a regra:

- é só de códigos, cada um entre as marcas `abre` e `fecha`, com alguma coisa entre elas e
  sem elas dentro, separados pela marca `entre`;
- cada código é uma sequência de partes separadas pelo `separador`, com um número de partes
  que está em `tamanhos`, e cada parte casa inteira com a forma da posição dela, em
  `formas`;
- nenhum código é o começo de outro, parte por parte, nem se repete;
- os códigos vêm em ordem natural, parte por parte: os trechos de algarismos se comparam
  pelo valor (9 vem antes de 10), os outros pelo texto, e o código que é o começo de outro
  viria antes dele.

O que vem depois do título, como a dúvida, o estado dela e as respostas, fica com o
projeto.

## A configuração

O molde está em `esquemas/dicionario-das-duvidas.schema.json`:

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `titulo` | o começo da linha do título de cada dúvida, como `## ` |
| `codigo` | o que `abre` e o que `fecha` cada código, como a crase, e o que fica `entre` dois códigos, como um espaço |
| `partes` | o `separador` das partes de um código, como `/`; as `formas`, uma expressão regular para cada posição, na ordem; e os `tamanhos`, os números de partes que um código pode ter, de 1 até o número de formas |

As marcas e o separador são textos de uma linha só, que podem ser só de espaços. É `ERRO`,
com código 2: campo que o molde não conhece, campo que falta ou de outro tipo, marca vazia
ou com quebra de linha, nenhuma forma ou forma vazia, forma que não compila, nenhum tamanho,
tamanho repetido, menor que 1 ou maior que o número de formas; e o dicionário que falta ou
que não se lê em UTF-8.

Um exemplo, em que um código tem uma, duas ou quatro partes: a primeira, um número ou dois
ligados por hífen (como `9-10`); a segunda e a terceira, números; a quarta, quatro
algarismos hexadecimais:

    {
      "versao_schema": 1,
      "titulo": "## ",
      "codigo": {"abre": "`", "fecha": "`", "entre": " "},
      "partes": {"separador": "/", "formas": ["\\d+(-\\d+)?", "\\d+", "\\d+", "[0-9a-f]{4}"], "tamanhos": [1, 2, 4]}
    }

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../LICENSE-CONTENT.txt).*
