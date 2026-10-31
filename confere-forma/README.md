# confere-forma

Confere a forma de documentos Markdown contra uma descrição dela: a abertura, os títulos das
seções na ordem dada, o divisor antes de cada seção, o bloco de fecho no fim de cada seção,
os padrões proibidos, os nomes que só podem aparecer em itálico e o tamanho do texto. Serve
a qualquer coleção de documentos que seguem um mesmo modelo, como fichas, relatórios ou
textos de estudo.

Usa só a biblioteca padrão do Python e o `extrator_comum.py`, do
[extrator](../extrator/README.md), que lê a configuração pelo molde dela e os textos em
UTF-8. Na prateleira, ele é achado na pasta irmã `extrator/`; numa cópia fora da prateleira,
na mesma pasta do script.

## Como rodar

    python3 -I confere_forma.py <configuração.json> <texto.md>...

Mostra uma linha `ERRO arquivo:linha: motivo` por problema, em ordem de linha; uma
`AVISO arquivo: motivo` quando o tamanho sai dos limites; uma linha com as palavras de cada
texto; e um resumo com quantos textos, erros e avisos. Sai com código 0 sem erro (o aviso
não conta), 1 com erro e 2 quando a configuração ou um argumento não serve (então nada é
conferido).

## O que se confere

| Regra | Onde sai o ERRO |
| --- | --- |
| **Abertura:** as linhas com texto antes do primeiro divisor ou da primeira seção são, na ordem, uma para cada item; o item `igual` é a linha inteira, o `padrao` é uma expressão que casa com ela | na linha fora do modelo ou a mais; na linha 1 quando falta uma |
| **Seções:** os títulos (o grupo `titulo` da expressão `secao`) são os da lista, na mesma ordem, comparados letra por letra | no título fora do lugar ou a mais; na última linha com texto quando falta um |
| **Divisores:** a linha com texto logo antes de cada seção é um divisor, e a logo depois de cada divisor é uma seção | na seção sem divisor; no divisor fora do lugar |
| **Fecho:** cada seção tem um bloco de fecho (uma linha que casa com `abre`, seguida das que casam com `continua`), e ele é a última coisa da seção; linha que casa com `continua` fora de um bloco é erro | na seção sem fecho; no segundo fecho; na primeira linha com texto depois do fecho; na linha de bloco fora dele |
| **Proibidos:** a linha que casa com o `padrao` de uma regra, e não com o `exceto` dela | na linha, com o `nome` da regra |
| **Itálico:** nas linhas que não casam com `fora_de`, cada nome da lista só aparece em itálico, isto é, entre duas marcas iguais da lista, coladas ao texto; a marca dobrada (negrito) não conta. O nome vale como palavra inteira, e o mais longo vem primeiro: um nome mais curto dentro dele não conta de novo | na linha, com o nome |

**Tamanho:** as palavras do corpo das seções, sem os títulos, os divisores, os blocos de
fecho e as linhas que casam com `palavras/fora_de`. Fora do `minimo` e do `maximo` (os dois
incluídos), sai um `AVISO`.

## A configuração

O molde está em `esquemas/confere-forma.schema.json`:

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `abertura` | lista de itens, cada um com um só destes: `igual` (o texto da linha) ou `padrao` (uma expressão) |
| `secao` | expressão da linha de título de seção, com o grupo `titulo` |
| `titulos` | os títulos das seções, na ordem |
| `divisor` | expressão da linha de divisor |
| `fecho` | as expressões `abre` (a primeira linha do bloco de fecho) e `continua` (as outras) |
| `proibidos` | lista de regras, cada uma com o `nome`, o `padrao` e, se houver, o `exceto` |
| `italico` | os `nomes`, as `marcas` de itálico e a expressão `fora_de` (linhas que não se conferem) |
| `palavras` | a expressão `fora_de` (linhas que não se contam), o `minimo` e o `maximo` |

É `ERRO`, com código 2: campo que o molde não conhece, campo que falta ou de outro tipo,
expressão que não compila, `secao` sem o grupo `titulo`, item da abertura sem campo ou com
os dois, título, nome ou marca vazios, e mínimo maior que o máximo.

## Testes

Em [testes/](testes/README.md).
