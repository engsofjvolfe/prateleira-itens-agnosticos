# confere-forma

Confere a forma de documentos Markdown contra uma descrição dela: a abertura, os títulos das
seções na ordem dada, o divisor antes de cada seção, o bloco de fecho no fim de cada seção,
os padrões proibidos, os nomes que só podem aparecer em itálico e o tamanho do texto. Serve
a qualquer coleção de documentos que seguem um mesmo modelo, como fichas, relatórios ou
textos de estudo.

Usa só a biblioteca padrão do Python e o `extrator_comum.py`, do
[extrator](../extrator/README.md), que lê a configuração e os arquivos de padrões proibidos
pelo molde de cada um, e os textos em UTF-8. Na prateleira, ele é achado na pasta irmã
`extrator/`; numa cópia fora da prateleira, na mesma pasta do script.

## Como rodar

    python3 -I confere_forma.py <configuração.json> <texto.md>... [--proibidos <arquivo.json>]...

O `--proibidos` dá um arquivo de [padrões proibidos](#os-padrões-proibidos) e pode se
repetir: as regras de todos se somam. Sem ele, nenhum padrão é proibido.

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
| **Proibidos:** a linha que casa com o `padrao` de uma regra dos arquivos de padrões proibidos, e não com o `exceto` dela | na linha, com o `nome` da regra |
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
| `italico` | os `nomes`, as `marcas` de itálico e a expressão `fora_de` (linhas que não se conferem) |
| `palavras` | a expressão `fora_de` (linhas que não se contam), o `minimo` e o `maximo` |

É `ERRO`, com código 2: campo que o molde não conhece, campo que falta ou de outro tipo,
expressão que não compila, `secao` sem o grupo `titulo`, item da abertura sem campo ou com
os dois, título, nome ou marca vazios, e mínimo maior que o máximo.

## Os padrões proibidos

Cada arquivo de padrões proibidos é só dados. O molde está em
`esquemas/proibidos.schema.json`, com a regra de linha do
[molde comum](../extrator/README.md#o-molde-comum) do extrator e a de expressão do molde da
configuração:

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `proibidos` | a lista das regras, que pode estar vazia; cada uma com o `nome`, numa linha só, com alguma letra, o `padrao` e, se houver, o `exceto`, expressões que não estão vazias |

Um projeto guarda nos dados dele os padrões que são só dele e dá também, quando lhe servem,
os arquivos desta pasta, com o caso comum a qualquer projeto:

| Arquivo | O que proíbe |
| --- | --- |
| `marcas-de-ia.json` | as marcas que uma ferramenta de IA deixa num texto: o caractere invisível ou o espaço especial, como o espaço sem quebra, o de largura zero e a marca de direção do texto; e o resto de citação da ferramenta, como `oaicite`, `contentReference` ou o `utm_source=` de um link |

É `ERRO`, com código 2, que diz o arquivo e, quando é o caso, a regra: arquivo que não
existe ou que não se lê como JSON, fora do molde (como o campo que ele não conhece e a regra
sem nome ou sem padrão), expressão que não compila, e duas regras com o mesmo nome, no mesmo
arquivo ou em dois.

## Testes

Em [testes/](testes/README.md).
