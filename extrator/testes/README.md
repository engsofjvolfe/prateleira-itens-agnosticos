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

Precisa do Poppler e do Tesseract com o idioma `eng`. Diz `0 falha(s)` quando passa; senão,
uma linha `FALHA` para cada conferência que não passou, e sai com código 1.

`pdf_inventado.py`, que não se roda, monta os PDFs inventados do teste; outro teste que
precise de um PDF inventado o importa.

As cópias estragadas do extrator estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md):

    python3 -I ../../copias-estragadas/estraga.py .. teste_extrator.py estragos.json <pasta de trabalho nova>
