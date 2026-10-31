# confere-citacoes

Confere as citações de textos Markdown contra as transcrições das fontes: cada trecho
citado precisa estar, letra por letra, na fonte que a referência nomeia, e nas páginas que
ela dá, com os pedaços na ordem da fonte e cada supressão no lugar de alguma coisa. Serve a
qualquer texto que cita uma fonte transcrita em páginas, como os textos de estudo que citam
um livro.

Usa só a biblioteca padrão do Python e dois módulos do [extrator](../extrator/README.md): o
`extrator_comum.py`, que lê a configuração pelo molde dela, lê os textos e as fontes em
UTF-8 e divide a transcrição em páginas pelo modelo do título de página, e o
`texto_comum.py`, que passa o texto para a
forma NFC e junta os espaços. Na prateleira, eles são achados na pasta irmã `extrator/`;
numa cópia fora da prateleira, na mesma pasta do script.

## Como rodar

    python3 -I confere_citacoes.py <configuração.json> <pasta das fontes> <texto.md>...

Mostra uma linha `ERRO arquivo:linha: motivo` por problema, em ordem de texto e de linha, e
um resumo com quantos textos, citações, trechos e erros. Sai com código 0 sem erro, 1 com
erro e 2 quando a configuração ou um argumento não serve (então nada é conferido).

## A citação

Uma citação são duas linhas seguidas do texto: a de referência, reconhecida pela expressão
`referencia`, com o grupo `fonte` (o nome da fonte) e o grupo `paginas`; e a do trecho,
reconhecida pela expressão `citacao`, com o grupo `trecho`.

- **Páginas:** partes separadas pelo `separador`; cada parte é o rótulo de uma página, ou
  um intervalo entre dois números (os dois incluídos), com o `intervalo` no meio.
- **Trecho:** partido na marca de `supressao`; cada pedaço, sem os caracteres das `pontas`
  nas duas pontas, precisa aparecer na fonte, e pelo menos uma das vezes em que aparece
  precisa cair só em páginas citadas. Pedaço vazio não conta.
- **Ordem e supressão:** os pedaços aparecem na fonte na ordem do trecho, cada um depois do
  fim do anterior, e entre um e o seguinte a fonte tem alguma coisa além dos caracteres das
  `pontas` e dos espaços: a supressão marca o que foi omitido, e não pode estar onde nada
  foi. Cada pedaço vale pela primeira vez em que aparece nas páginas citadas depois do
  anterior. A supressão no começo ou no fim do trecho não se confere.
- **Comparação:** os dois lados vão para NFC; cada caractere de um grupo de `equivalentes`
  vira o primeiro do grupo; cada trecho de espaços (com quebras de linha) vira um espaço só.
  Maiúsculas contam.

| Caso | Onde sai o ERRO |
| --- | --- |
| trecho que não está na fonte (a mensagem avisa quando difere só em maiúsculas) | linha do trecho |
| trecho que só está em páginas não citadas (a mensagem diz em quais está) | linha do trecho |
| pedaço fora da ordem da fonte, ou supressão que não omite nada (só pontas e espaços entre dois pedaços) | linha do trecho |
| páginas que não se leem (parte vazia, intervalo ao contrário ou que não é de números) | linha da referência |
| fonte que não existe, que não se lê em UTF-8 ou com bloco ignorado que não fecha | linha da referência |
| referência sem a linha do trecho logo depois | linha da referência |
| trecho sem a linha de referência logo antes | linha do trecho |

## A fonte

A fonte de nome N é o arquivo que o modelo `fontes/arquivo` dá com `{fonte}` trocado por N,
na pasta das fontes. As páginas vêm do modelo `fontes/titulo_pagina`, com `{rotulo}` (o que
a referência cita) e `{arquivo}` (a posição da página no arquivo), o mesmo modelo do
extrator. O que vem antes do primeiro título não é de página nenhuma. As linhas de cada
bloco de `fontes/ignorar` (da que casa com `abre` até a que casa com `fecha`, as duas
incluídas), como o texto lido dentro de uma imagem, ficam de fora.

## A configuração

O molde está em `esquemas/confere-citacoes.schema.json`:

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `referencia` | expressão da linha de referência, com os grupos `fonte` e `paginas` |
| `citacao` | expressão da linha do trecho, com o grupo `trecho` |
| `paginas` | o `separador` das partes e a marca de `intervalo` |
| `fontes` | o modelo do nome do `arquivo` (com `{fonte}`), o `titulo_pagina` (com `{rotulo}` e `{arquivo}`) e a lista `ignorar`, de blocos com as expressões `abre` e `fecha` |
| `supressao` | a marca de uma parte omitida no trecho |
| `pontas` | os caracteres que saem das pontas de cada pedaço |
| `equivalentes` | grupos de caracteres que valem o mesmo, cada um um texto de dois caracteres ou mais |

É `ERRO`, com código 2: campo que o molde não conhece, campo que falta ou de outro tipo,
expressão que não compila ou sem os grupos dela, modelo de arquivo com outro campo além de
`{fonte}`, grupo de equivalentes de um caractere só, e separador, intervalo ou supressão
vazios.

## Testes

Em [testes/](testes/README.md).
