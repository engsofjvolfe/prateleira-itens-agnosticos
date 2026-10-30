# testes do extrator

    python3 -I teste_extrator.py <pasta do extrator> <pasta de trabalho nova>

Monta, na pasta de trabalho, documentos inventados: PDFs feitos pelo próprio teste (um com
muitas páginas de linhas, uma página vazia e uma página que vai pelo OCR, com um texto que
só a camada de texto tem; um com negrito e itálico; um que mistura destaques num trecho),
um HTML em ISO-8859-1, um XML com etiquetas de outros nomes e dois JSON. O texto é sorteado
entre todos os caracteres que um texto pode ter, sempre o mesmo, porque a semente é fixa.
Entram também linhas que começam e terminam com cada caractere que os padrões tratam de um
jeito próprio, palavras destacadas com pontuação sem destaque nas pontas e a mesma palavra
duas vezes num trecho destacado. Três padrões de transcrição inventados, com marcas que não
são as de nenhum projeto, passam pelos mesmos testes.

O teste confere regras que valem para qualquer texto, nunca uma frase pronta. Cada linha
escrita é lida de volta pela definição do padrão, e as regras são estas:

- o texto é o do documento, linha por linha;
- nenhum caractere que se escapa fica sem escape, e cada marca fecha na mesma linha,
  colada ao texto;
- cada caractere tem o destaque que tem no documento, e o espaço, só o destaque dos dois
  lados;
- os títulos seguem o modelo, e o número impresso, lido de volta, é o da numeração; os
  estilos de numeração dão o número certo de 1 a 3999;
- as trocas e as correções dão o que a regra delas diz e são contadas no resumo;
- todo erro para tudo, sem gravar nada, e a mensagem diz o dado que o causou;
- duas rodadas dão a mesma saída.

O que o módulo comum dá para as peças lerem os próprios dados tem o teste dele, abaixo.

Precisa do Poppler e do Tesseract com o idioma `eng`. Diz `0 falha(s)` quando passa; senão,
uma linha `FALHA` para cada conferência que não passou, e sai com código 1.

`pdf_inventado.py`, que não se roda, monta os PDFs inventados do teste; outro teste que
precise de um PDF inventado o importa.

As cópias estragadas do extrator estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md):

    python3 -I ../../copias-estragadas/estraga.py .. teste_extrator.py estragos.json <pasta de trabalho nova>

## O módulo comum

    python3 -I teste_extrator_comum.py <pasta do extrator> <pasta de trabalho nova> [--semente N]

Testa o que o `extrator_comum.py` dá para as peças lerem os próprios dados: o leitor de
molde (`fora_do_molde`, `confere_molde` e `le_conferido`), `campo` e `expressao`. Não
precisa de PDF. Os nomes dos campos e os valores são sorteados, sempre iguais, porque a
semente é fixa (outra vem com `--semente`), e cada molde é inventado no teste. O teste
confere regras, nunca uma frase pronta:

- cada palavra do molde que o leitor confere aceita o valor que a segue e acusa o que não a
  segue, no caminho do valor, e só nele: `type` (um ou uma lista; o booleano não é número,
  e o número com ponto não é inteiro), `const` e `enum` (o booleano não é igual ao número,
  e o número é igual ao de mesmo valor), `minLength` e `maxLength` (em letras, também com
  acento), `pattern` (buscada no texto), `minimum` e `maximum` (com o próprio limite
  aceito), `minItems`, `maxItems`, `uniqueItems` (também com objetos), `items`, `required`,
  `properties`, `additionalProperties` (falso ou um molde), `minProperties`,
  `maxProperties`, `allOf`, `if`, `then` e `else`, o molde falso e o `$ref` (para `$defs`,
  para a raiz, com escape no nome, ao lado de outra palavra, e um molde que se repete
  dentro dos dados); as anotações não conferem nada;
- cada palavra do molde dos moldes tem um caso aqui, e cada molde do extrator, o próprio
  molde dos moldes também, segue o molde dos moldes;
- todos os erros saem, não só o primeiro; o valor do tipo errado dá um erro só;
- o molde fora do molde dos moldes (uma palavra que o leitor não conhece, outro dialeto, um
  valor que não é da forma que a palavra pede, uma referência que não vai à raiz nem a
  `$defs`) é erro, que diz o lugar no molde; o tipo desconhecido, também depois de um tipo
  certo, a referência para o que o molde não tem ou que volta a ela mesma e a forma que não
  compila são erro, que diz o quê;
- `le_conferido` dá os dados do arquivo que segue o molde e, senão, erro com o arquivo, o
  molde e o caminho de cada valor fora; o arquivo que falta ou que não é JSON é erro; o
  molde fora do molde dos moldes é erro, com o arquivo dele e o lugar;
- `campo` dá o valor no caminho com o tipo pedido e dá erro, dizendo o caminho, quando ele
  falta ou é de outro tipo; `expressao` compila o campo ou dá erro, dizendo o caminho;
- duas conferências dão o mesmo.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1. As cópias estragadas do módulo comum estão em
`estragos-extrator-comum.json`, nesta pasta:

    python3 -I ../../copias-estragadas/estraga.py .. teste_extrator_comum.py estragos-extrator-comum.json <pasta de trabalho nova>
