# testes de documentos

    python3 -I teste_linhas_longas.py <pasta do linhas_longas.py> <pasta de trabalho nova> [--semente N]
    python3 -I teste_confere_links.py <pasta do confere_links.py> <pasta de trabalho nova> [--semente N]

A pasta de trabalho precisa ser nova ou vazia; o teste escreve nela. Os dois sorteiam tudo o
que testam, sempre igual, porque a semente é fixa (outra semente vem com `--semente`), com
letras de fora do ASCII, e conferem regras, nunca uma frase pronta. Precisam do
`extrator_comum.py`, do extrator, na pasta irmã `extrator/` da peça ou na própria pasta da
peça. Cada um diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência
que não passou, e sai com código 1.

## As linhas longas

O `teste_linhas_longas.py` monta uma pasta com subpastas, uma delas com um nome que segue o
padrão, e, em cada uma, arquivos que seguem o padrão e um que não segue, com uma linha longa.
O limite, o padrão, os nomes e o tamanho, o texto e a quebra de cada linha são sorteados,
com muitas linhas em volta do limite e com letras que são um caractere só e mais de um byte.
Confere:

- cada linha acima do limite, e só ela, sai numa linha `ERRO` com o arquivo e o número da
  linha, em ordem de arquivo e de linha, e o `ERRO` diz o tamanho dela; depois delas, só sai
  o resumo; a linha do tamanho do limite passa;
- o tamanho é o número de caracteres, sem a quebra do fim, seja ela LF ou CR LF, e a última
  linha conta também sem quebra no fim;
- o arquivo dado é conferido qualquer que seja o nome; numa pasta, só os arquivos que seguem
  o padrão, também nas subpastas e na subpasta cujo nome segue o padrão; o arquivo dado e
  achado numa pasta é conferido uma vez só;
- o resumo diz, nessa ordem, o número de arquivos conferidos, o de linhas acima do limite e o
  limite;
- o código de saída é 1 com linha acima do limite e 0 sem nenhuma;
- o limite zero ou negativo, o caminho que não existe e o arquivo que não se lê em UTF-8 saem
  com 2 e só com uma linha `ERRO`, que diz o limite ou o caminho; o limite que não é um
  número inteiro sai com 2, sem nada na saída padrão;
- duas rodadas dão a mesma saída.

## Os links

O `teste_confere_links.py` monta repositórios git inventados, com o git rodado sem a
configuração do sistema e da conta (que poderia deixar arquivos de fora) e sem subir da
pasta de trabalho (que poderia estar dentro de outro repositório). Os nomes dos documentos,
dos arquivos e das pastas, os títulos, os marcadores, os textos dos links, o número de
linhas dos arquivos e a ordem dos casos são sorteados. O repositório com erros tem:

- um documento principal com links, de um a três por linha, cada um com ou sem `!`, com ou
  sem colchetes no texto, com ou sem título, com ou sem espaços nos parênteses e com o alvo
  entre `<>` ou não: para arquivo que existe e que falta, com e sem âncora; para uma linha (a
  primeira, a última, depois da última, a zero, com `l` minúsculo, num arquivo sem quebra no
  fim, num Markdown, no próprio documento, numa pasta e num caminho com espaço); para pasta e
  para imagem, com e sem âncora; para caminho com espaço, entre `<>` e codificado, também na
  âncora; para os títulos do próprio documento e para as âncoras do documento de destino;
  externos, de esquema sorteado; num código na linha e em blocos de código, um deles com uma
  cerca do outro sinal e uma mais curta dentro, e um link logo depois dele; e links com o
  texto quebrado em duas linhas;
- um documento de destino com um título com maiúsculas, pontuação, código, link, tag HTML e
  pontuação solta; um título repetido, com e sem maiúsculas; marcadores pelo `id` e pelo
  `name`, entre aspas duplas, entre simples e sem aspas, com o atributo em maiúsculas e
  depois de outro atributo; e, que não valem, o valor do outro atributo, um texto sem tag e
  um título e marcadores num bloco de código, num código na linha e num comentário de várias
  linhas;
- um documento novo, fora do git, e um que o `.gitignore` deixa de fora, cada um com um link
  quebrado.

Confere:

- cada link quebrado, e só ele, sai numa linha `ERRO` com o documento, a linha do começo do
  alvo e o alvo, em ordem de documento e de linha, e depois delas só sai o resumo;
- o mesmo problema sai sempre com o mesmo motivo, e problemas diferentes (o arquivo que
  falta, a linha que falta, a âncora num arquivo que não é Markdown e a âncora que falta),
  com motivos diferentes;
- o resumo diz, nessa ordem, o número de links internos, o dos com âncora e o de erros;
- o código de saída é 1 com link quebrado e, num repositório só com os links que valem, 0;
- a pasta sem git e o documento, ou o Markdown de destino de uma âncora, que não se lê em
  UTF-8 saem com 2 e só com uma linha `ERRO`, que diz a pasta ou o arquivo, mesmo com um link
  quebrado antes;
- duas rodadas dão a mesma saída.

## As cópias estragadas

Estão em duas listas, nesta pasta, para o [`estraga.py`](../../copias-estragadas/README.md),
rodado desta pasta: `estragos-linhas-longas.json`, para o `teste_linhas_longas.py`, e
`estragos-confere-links.json`, para o `teste_confere_links.py`:

    python3 -I ../../copias-estragadas/estraga.py .. teste_linhas_longas.py estragos-linhas-longas.json <pasta de trabalho nova> --irma ../../extrator
    python3 -I ../../copias-estragadas/estraga.py .. teste_confere_links.py estragos-confere-links.json <pasta de trabalho nova> --irma ../../extrator
