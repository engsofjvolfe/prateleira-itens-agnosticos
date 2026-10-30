# testes de busca-por-palavra

    python3 -I teste_busca_por_palavra.py <pasta de busca_por_palavra.py> <pasta de trabalho nova>

Tudo é inventado: os comandos de busca, as opções, o padrão livre, o prefixo, o texto do
motivo, o arquivo da busca exata e a forma dos padrões dela; e o protocolo do programa que
roda o gancho, sorteado pelo [`protocolo_inventado.py`](../../protocolo/testes/protocolo_inventado.py)
(os eventos, as chaves e as respostas), com a ferramenta de terminal e a de busca. Nada é de
um projeto real nem de um programa de verdade.

O teste confere o que o gancho faz, nunca uma frase pronta:

- no terminal, bloqueia a busca com padrão que não é livre, dado sem opção, com a opção
  curta sozinha, junto de outras ou com o valor colado, com a longa, com o valor depois do
  `=` ou na palavra seguinte, ou repetida; a busca com os padrões tirados de um arquivo e a
  busca sem padrão; a busca depois de um operador, de um prefixo e de uma atribuição, com o
  caminho e dentro de `$( )` ou de crases; a busca de duas palavras, também com outras no
  meio; a busca com o padrão livre dado na opção que só outra busca tem; e o comando que
  não se lê;
- deixa passar a busca só com o padrão livre, dado dessas formas, e o comando que não é uma
  busca, mesmo com o nome dela como argumento, entre aspas ou num comentário;
- com `--exatas`, deixa passar a busca exata — cada padrão inteiro na forma, dado dessas
  formas, e só o arquivo da exata, com o caminho a partir da pasta do evento, relativo ou
  inteiro, também depois de `--`, repetido e nas buscas sem opção de padrão e de duas
  palavras —, e o padrão livre continua passando; bloqueia o padrão fora da forma ou só com
  parte dela, a busca sem arquivo, com outro arquivo, com um a mais (também depois de `--`,
  ou o valor de uma opção que o gancho não conhece), a que mistura o padrão exato com uma
  palavra ou com o livre, a com os padrões tirados de um arquivo e a de outra pasta, que
  acha outro arquivo com o mesmo nome; sem `--exatas`, a busca exata é bloqueada, e a
  ferramenta de busca não muda com ele;
- com `--exatas` de dois arquivos, cada um com a sua forma, deixa passar a busca exata de
  cada um e bloqueia a busca num deles com a forma do outro e a que lê os dois;
- na ferramenta de busca, bloqueia o padrão que não é livre e a busca sem padrão, e deixa
  passar o livre;
- o bloqueio é a resposta que nega do protocolo, com o texto do motivo e a parte que
  bloqueou;
- configuração com campo desconhecido ou que falta, protocolo fora da forma, a falta do
  texto do motivo, evento de fim, evento desconhecido, ferramenta desconhecida, entrada que
  não é JSON e, com `--exatas`, o arquivo que não existe, também o segundo de dois, e a
  forma que não é expressão regular dão erro;
- duas rodadas dão o mesmo.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas de `busca_por_palavra.py` estão em `estragos.json`, nesta pasta, para
o [`estraga.py`](../../../copias-estragadas/README.md), com as pastas da leitura do
terminal, do extrator e do protocolo ao lado da cópia:

    python3 -I ../../../copias-estragadas/estraga.py .. teste_busca_por_palavra.py estragos.json <pasta de trabalho nova> --irma ../../leitura-do-terminal --irma ../../../extrator --irma ../../protocolo
