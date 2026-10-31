# marcas

Lê os códigos escondidos num texto Markdown e confere se cada um está no lugar em que
deveria estar. Os códigos vão em comentários, que a visualização não mostra:
`<!-- artigo 5-iii -->`. Serve para ligar um texto ao que ele precisa explicar sem que a
ligação apareça na leitura. Num material de Direito, por exemplo, cada seção do texto
levaria escondido o código de cada artigo de lei que ela explica, e a peça diria qual
artigo falta, qual está na seção errada e qual não existe.

Usa só a biblioteca padrão do Python e o `extrator_comum.py`, do
[extrator](../extrator/README.md), que acha o nível e o código repetidos; ele é achado na
pasta irmã `extrator/` ou na mesma pasta. Não roda sozinha: o programa que a usa importa o
`marcas.py`.

## As marcas

Uma marca é um comentário HTML com um nível e um código, separados por espaço. O programa
que usa a peça dá os níveis (`Niveis`):

- os que abrem uma região, do de fora para o de dentro. O primeiro abre a unidade, e abrir
  um nível fecha os de dentro dele. No Direito: `lei`, `capitulo` e `secao`; uma marca
  `capitulo` fecha a seção aberta;
- o das marcas de dentro, que não abrem região: cada uma diz um código que está na região
  aberta (no Direito, `artigo`).

Comentário cujo texto não começa por um nível não é marca. Um comentário pode ocupar mais
de uma linha e vai até o primeiro `-->`. Cada arquivo começa sem nada aberto. Níveis,
códigos e texto se comparam em NFC: o mesmo acento escrito de dois jeitos é igual.

A peça não decide o que é código no Markdown. O programa que a usa dá as linhas de cada
arquivo que ficam fora dos blocos de código e do código de dentro da linha, cada uma com o
número dela no arquivo; assim, a regra do que é código fica só no leitor de Markdown dele.

## O que a peça recebe

| O quê | O que é |
| --- | --- |
| `Niveis(abrem, dentro)` | os níveis que abrem região, numa lista, do de fora para o de dentro, e o das marcas de dentro |
| as linhas de cada arquivo | `[(número, texto)]`, só as de fora do código |
| o esperado | `{unidade: Esperado(regioes, livres)}`: de cada unidade, as regiões em ordem, cada uma `Regiao(caminho, codigos, recebe)`, e os códigos que valem em qualquer região dela que recebe códigos |
| os códigos que existem | todos, de todas as unidades e de fora delas |

O caminho de uma região tem um código para cada nível que abre região, com `None` nos que
não estão abertos. Com os níveis `lei`, `capitulo` e `secao`, `("lei-8078", None,
"disposicoes")` é a seção aberta direto na lei, e `("lei-8078", "cap-1", "direitos")`, a
do capítulo 1. A região que o texto abre só para chegar às do esperado (a da lei antes da
primeira seção, a de um capítulo antes da primeira seção dele) pode ser aberta e não
recebe códigos.

Níveis ou esperado que não servem (como regiões numa ordem que não se escreve sem abrir uma
delas duas vezes, ou um código que não está entre os que existem) dão `ErroDeMarcas`, que
diz o que está errado.

## O que a peça entrega

- `marcas_das_linhas(linhas, arquivo, niveis)`: as marcas de um arquivo, na ordem, cada uma
  `Marca(arquivo, linha, nivel, codigo)`. A marca fora da forma sai sem código; o
  comentário que não fecha, sem nível e sem código.
- `com_caminho(marcas, niveis)`: cada marca com o caminho da região dela.
- `confere(marcas, niveis, esperados, existem)`: os avisos, em ordem de arquivo e linha,
  cada um `Aviso(tipo, caso, arquivo, linha, unidade, codigo, texto)`: o tipo (`FALTA` ou
  `ERRO`), o caso, onde, a unidade aberta ali, o código de que ele trata e o texto que diz
  o que houve.

| Caso | Tipo | Quando |
| --- | --- | --- |
| `falta` | FALTA | um código esperado não está na região dele (o aviso fica na linha da marca que abre a região, ou na da unidade quando a região não foi aberta); ou um código que vale em qualquer região não está em nenhuma (na linha da unidade) |
| `fora-da-forma` | ERRO | marca com o nível e sem código, ou com mais de um |
| `comentario-sem-fim` | ERRO | comentário que não fecha; o que vem depois dele não se lê |
| `fora-de-unidade` | ERRO | marca antes da primeira unidade do arquivo |
| `regiao-desconhecida` | ERRO | região que o esperado não tem; numa unidade que o esperado não tem, o que está dentro dela não se confere, a não ser a forma das marcas |
| `regiao-repetida` | ERRO | região aberta outra vez na mesma unidade |
| `fora-de-ordem` | ERRO | região aberta depois de uma que, no esperado, vem depois dela |
| `unidade-em-dois-lugares` | ERRO | unidade aberta outra vez; o que vem depois conta para a mesma unidade |
| `nao-existe` | ERRO | código que não está entre os que existem |
| `outra-unidade` | ERRO | código que existe, mas não é desta unidade |
| `regiao-que-nao-recebe` | ERRO | código numa região que não recebe códigos |
| `outra-regiao` | ERRO | código desta unidade fora das regiões em que ele é esperado |

## Testes

Em [testes/](testes/README.md).
