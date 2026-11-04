# confere-forma

Serve para conferir que cada documento Markdown de uma coleção segue a mesma forma: o texto
fixo do começo, os títulos das seções na ordem certa, o divisor antes de cada seção, o bloco de
fecho no fim de cada uma, a primeira linha de cada seção, a primeira vez de cada sigla, os
padrões proibidos, os nomes que só aparecem em itálico e o tamanho. O texto que todos os
documentos têm igual, a abertura e os títulos das seções, vem de um esqueleto em Markdown; a
forma, de uma configuração só com dados; e os padrões proibidos, de arquivos próprios.

A peça serve quando:

- os documentos são Markdown, um por arquivo, e seguem um mesmo modelo, como fichas,
  relatórios, receitas ou textos de estudo;
- cada parte que se confere cabe numa linha e se reconhece por uma expressão regular;
- o que muda de um documento para outro na abertura ou num título, como um nome, cabe numa
  lacuna do esqueleto.

Não serve para conferir o que o texto diz (o conteúdo, o tom, se a explicação de uma sigla está
certa), para documentos sem um modelo comum, nem para o que se espalha por mais de uma linha,
como um parágrafo inteiro ou uma tabela.

Um exemplo. Numa coleção de receitas, o esqueleto

```markdown
# Receita: {nome}

**Para cozinhar em casa.**

## Ingredientes

## Preparo
```

com a lacuna `{nome}` dada na configuração pela expressão `\*[^*]+\*`, faz cada receita
começar por um título como `# Receita: *Bolo de fubá*`, seguido da linha fixa, e ter as duas
seções, nessa ordem. Com o `comeco_das_secoes` de uma linha que não é item de lista, cada
seção abre com uma frase; com as `siglas`, a primeira `PANC` de cada receita vem entre
parênteses, logo depois do nome completo, como em `planta alimentícia não convencional (PANC)`.

Usa só a biblioteca padrão do Python, o `extrator_comum.py`, do
[extrator](../extrator/README.md), que lê a configuração pelo molde dela e os textos em UTF-8,
o [módulo dos padrões proibidos](#o-módulo-dos-padrões-proibidos), desta pasta, e o
`rodape_comum.py`, do [rodape](../rodape/README.md#o-módulo-do-rodapé), que acha o rodapé no
fim de um texto. Na prateleira, eles são achados nas pastas irmãs; numa cópia fora da
prateleira, na mesma pasta do script.

## Como rodar

    python3 -I confere_forma.py <configuração.json> <esqueleto.md> <texto.md>... [--proibidos <arquivo.json>]... [--rodape <modelo.md>]

- `<configuração.json>`: a forma, só com dados (ver [A configuração](#a-configuração)).
- `<esqueleto.md>`: o texto que os documentos têm igual (ver [O esqueleto](#o-esqueleto)).
- `--proibidos`: um arquivo de [padrões proibidos](#os-padrões-proibidos); pode se repetir, e
  as regras de todos se somam. Sem ele, nenhum padrão é proibido.
- `--rodape`: o modelo do rodapé que os textos têm no fim, como o aviso da licença. O rodapé
  do modelo no fim de um texto, com qualquer alvo nos links, fica fora da conferência e das
  palavras, e o resto se confere como sem ele, cada linha no número dela; o rodapé que não
  está no fim se confere como qualquer linha.

Mostra uma linha `ERRO arquivo:linha: motivo` por problema, em ordem de linha; uma
`AVISO arquivo: motivo` quando o tamanho sai dos limites; uma linha com as palavras de cada
texto; e um resumo com quantos textos, erros e avisos. Sai com código 0 sem erro (o aviso não
conta), 1 com erro e 2 quando a configuração, o esqueleto, o modelo do rodapé ou um argumento
não serve (então nada é conferido).

## O que se confere

| Regra | Onde sai o ERRO |
| --- | --- |
| **Abertura:** as linhas com texto antes do primeiro divisor ou da primeira seção são as da abertura do esqueleto, na ordem, uma para cada uma | na linha fora do esqueleto ou a mais; na linha 1 quando falta uma |
| **Seções:** os títulos (o grupo `titulo` da expressão `secao`) são os do esqueleto, na mesma ordem | no título fora do lugar ou a mais; na última linha com texto quando falta um |
| **Divisores:** a linha com texto logo antes de cada seção é um divisor, e a logo depois de cada divisor é uma seção | na seção sem divisor; no divisor fora do lugar |
| **Começo das seções:** com o `comeco_das_secoes`, a primeira linha com texto depois do título de cada seção casa com essa expressão | nessa linha; no título, quando a seção não tem nada depois dele |
| **Fecho:** cada seção tem um bloco de fecho (uma linha que casa com `abre`, seguida das que casam com `continua`), e ele é a última coisa da seção; linha que casa com `continua` fora de um bloco é erro | na seção sem fecho; no segundo fecho; na primeira linha com texto depois do fecho; na linha de bloco fora dele |
| **Siglas:** com as `siglas`, nas linhas que não casam com o `fora_de` delas, cada sigla (o trecho que casa com o `padrao`, buscado na linha sem os trechos que casam com os `trechos_fora`), na primeira vez em que aparece no texto, vem na forma da primeira vez: o texto da linha logo antes dela termina pelo que casa com o `antes`, e o logo depois começa pelo que casa com o `depois`, cada um quando há. A forma se confere na linha inteira, e as vezes seguintes de cada sigla não se conferem | na linha da primeira vez, com a sigla |
| **Proibidos:** a linha que casa com o `padrao` de uma regra dos arquivos de padrões proibidos, e não com o `exceto` dela | na linha, com o `nome` da regra |
| **Itálico:** nas linhas que não casam com `fora_de`, cada nome da lista só aparece em itálico, isto é, entre duas marcas iguais da lista, coladas ao texto; a marca dobrada (negrito) não conta. O nome vale como palavra inteira, e o mais longo vem primeiro: um nome mais curto dentro dele não conta de novo | na linha, com o nome |

**Tamanho:** as palavras do corpo das seções, sem os títulos, os divisores, os blocos de
fecho e as linhas que casam com `palavras/fora_de`. Fora do `minimo` e do `maximo` (os dois
incluídos), sai um `AVISO`.

## O esqueleto

O esqueleto é um texto Markdown só com o que os documentos têm igual, lido com as mesmas
expressões `secao` e `divisor` da configuração:

- a abertura dele são as linhas com texto antes do primeiro divisor ou da primeira seção;
- os títulos são o grupo `titulo` de cada linha de seção, na ordem;
- fora delas, só pode haver divisores, que não mudam nada, e linhas em branco.

Cada linha da abertura e cada título valem letra por letra, menos as lacunas: onde a marca de
uma lacuna da configuração aparece, vale o trecho do documento que casa com a expressão dela.
A marca mais longa vale primeiro, de modo que uma marca dentro de outra não a corta. Sem
lacunas, o esqueleto inteiro vale letra por letra.

É `ERRO`, com código 2, que diz o arquivo: o esqueleto que não existe ou que não se lê em
UTF-8, a linha com texto que não é da abertura, de uma seção nem um divisor, a lacuna da
configuração que o esqueleto não tem e a linha que, com as expressões das lacunas no lugar das
marcas, não compila (como a lacuna com um grupo de nome que aparece duas vezes na linha).

## A configuração

O molde está em `esquemas/confere-forma.schema.json`, com a regra de linha do
[molde comum](../extrator/README.md#o-molde-comum) do extrator. Nenhum texto dos documentos
fica nela: ela tem só a forma, e o texto que eles têm igual vem do esqueleto.

| Campo | O que é |
| --- | --- |
| `versao_schema` | 2 |
| `lacunas` | se houver, a lista das lacunas do esqueleto, cada uma com a `marca`, numa linha só, com alguma letra, e o `padrao`, a expressão do trecho que ela aceita |
| `secao` | expressão da linha de título de seção, com o grupo `titulo` |
| `comeco_das_secoes` | se houver, a expressão que a primeira linha com texto de cada seção casa; sem ela, o começo não se confere |
| `divisor` | expressão da linha de divisor |
| `fecho` | as expressões `abre` (a primeira linha do bloco de fecho) e `continua` (as outras) |
| `siglas` | se houver, o `padrao` (a expressão de uma sigla) e o `fora_de` (a expressão das linhas que não se conferem); o `antes` e o `depois` (as expressões do que vem logo antes e logo depois da sigla na primeira vez), pelo menos um deles; e, se houver, os `trechos_fora` (a expressão dos trechos da linha que não se leem como sigla, como uma marca do documento, que viram espaços no mesmo lugar); sem o campo, as siglas não se conferem |
| `italico` | os `nomes`, as `marcas` de itálico e a expressão `fora_de` (linhas que não se conferem) |
| `palavras` | a expressão `fora_de` (linhas que não se contam), o `minimo` e o `maximo` |

É `ERRO`, com código 2: campo que o molde não conhece (também a `abertura` e os `titulos`,
que vêm do esqueleto), campo que falta ou de outro tipo, outra versão, expressão que não
compila, `secao` sem o grupo `titulo`, título, nome ou marca vazios, marca de lacuna sem letra
ou repetida, expressão das siglas (o `padrao`, o `antes`, o `depois` ou os `trechos_fora`) que
casa com o texto vazio, siglas sem o `antes` nem o `depois` e mínimo maior que o máximo.

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

## O módulo dos padrões proibidos

O `proibidos_comum.py` lê os padrões proibidos num lugar só, para toda peça que confere um
texto contra eles, como o [baralho-anki](../baralho-anki/README.md). Não se roda; a peça o
importa desta pasta, na prateleira a pasta irmã `confere-forma/`. Usa só a biblioteca padrão e
o `extrator_comum.py`.

| Função | O que faz |
| --- | --- |
| `regras_proibidas(caminhos)` | lê os arquivos de padrões proibidos, cada um pelo molde dele, e dá as regras, na ordem dos arquivos e, em cada um, na da lista, cada uma com o nome, o padrão e o exceto (ou nenhum), compilados; os erros acima são `ErroDeDados` |
| `achados(texto, regras)` | os nomes das regras em que o texto cai, na ordem delas: o padrão casa com ele, e o exceto, quando há, não casa |

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../LICENSE-CONTENT.txt).*
