# testes de documentos

    python3 -I teste_linhas_longas.py <pasta do linhas_longas.py> <pasta de trabalho nova> [--semente N]
    python3 -I teste_confere_links.py <pasta do confere_links.py> <pasta de trabalho nova> [--semente N]
    python3 -I teste_markdown_comum.py <pasta do markdown_comum.py> <pasta de trabalho nova>

A pasta de trabalho precisa ser nova ou vazia; o teste escreve nela. Os três sorteiam tudo o
que testam, sempre igual, porque a semente é fixa (nos dois primeiros, outra semente vem com
`--semente`), com letras de fora do ASCII, e conferem regras, nunca uma frase pronta. Os dois
primeiros precisam do `extrator_comum.py`, do extrator, na pasta irmã `extrator/` da peça ou
na própria pasta da peça. Cada um diz `0 falha(s)` quando passa; senão, uma linha `FALHA`
para cada conferência que não passou, e sai com código 1.

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

## O módulo de Markdown

O `teste_markdown_comum.py` confere o que só as peças que importam o `markdown_comum.py`
usam; a âncora, o código na linha, os marcadores e os links, o teste dos links confere. Ele
monta um documento sorteado, com títulos de nível 1 a 6, com recuo de zero a três espaços e
com ou sem os `#` do fim, um título repetido três vezes, parágrafos, blocos de código com
cercas dos dois sinais, com títulos dentro e com cercas que não fecham o bloco (a do outro
sinal, a mais curta e a com texto depois, cada uma com um título logo depois), e linhas que
não são título (sete `#`, `#` sem espaço, recuo de quatro espaços); e um repositório git, com
nomes sorteados, com espaço e letras de fora do ASCII. Confere:

- cada título fora de bloco de código, e só ele, sai na ordem, com a linha, o nível, o texto
  sem os `#` e os espaços das pontas e a âncora, com `-1` e `-2` no título repetido;
- as linhas fora de código são as do documento menos as dos blocos, cercas incluídas, cada
  uma com o número dela, a partir de 1;
- o caminho de um arquivo a partir de uma pasta, de outra, da do arquivo e de uma dada com
  `..`, com espaços nos nomes;
- o alvo vai entre `<` e `>` com espaço, tabulação ou parênteses, e só então, também no link;
- os documentos do repositório são, em ordem, os versionados e os novos que seguem um dos
  padrões, sem os que o `.gitignore` deixa de fora, os apagados, os que seguem um padrão de
  fora e os de outros padrões; sem os padrões de fora, os que seguem um deles entram; a pasta
  sem git é erro do git;
- duas leituras dão o mesmo.

Ele precisa do git, que roda sem a configuração do sistema e da conta e sem subir da pasta de
trabalho.

## As cópias estragadas

Estão em três listas, nesta pasta, para o [`estraga.py`](../../copias-estragadas/README.md),
rodado desta pasta: `estragos-linhas-longas.json`, para o `teste_linhas_longas.py`;
`estragos-confere-links.json`, para o `teste_confere_links.py`, com os do
`markdown_comum.py` que o `confere_links.py` usa; e `estragos-markdown-comum.json`, para o
`teste_markdown_comum.py`:

    python3 -I ../../copias-estragadas/estraga.py .. teste_linhas_longas.py estragos-linhas-longas.json <pasta de trabalho nova> --irma ../../extrator
    python3 -I ../../copias-estragadas/estraga.py .. teste_confere_links.py estragos-confere-links.json <pasta de trabalho nova> --irma ../../extrator
    python3 -I ../../copias-estragadas/estraga.py .. teste_markdown_comum.py estragos-markdown-comum.json <pasta de trabalho nova>

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
