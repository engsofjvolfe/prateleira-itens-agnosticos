# testes de leitura-do-terminal

    python3 -I teste_leitura_do_terminal.py <pasta do leitura_do_terminal.py> <pasta de trabalho nova>

Os comandos, os prefixos e as opções são inventados: nenhum é de um programa de verdade. A
pasta de trabalho não é usada, porque a leitura não grava nada. O teste confere o que a
leitura dá, nunca uma frase pronta:

- as palavras de cada comando simples: aspas simples e duplas, escape, continuação de
  linha, comentário só no começo de palavra, operadores com e sem espaço em volta, e os
  alvos de redirecionamento fora das palavras;
- as palavras que rodam como comando: a primeira, menos a atribuição, e todas as que vêm
  depois de um prefixo, também dado com o caminho; o argumento, não;
- os comandos de dentro de `$( )` e de crases, também entre aspas e um dentro do outro, na
  ordem: o de fora e, depois, cada um de dentro;
- o comando com aspa, crase ou substituição sem fechar é ilegível, e o resto não;
- a opção curta, sozinha ou junto de outras, e a longa, sozinha ou com `=valor`, batem; a
  parecida não;
- quais operadores são de redirecionamento;
- duas leituras dão o mesmo.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../../copias-estragadas/README.md):

    python3 -I ../../../copias-estragadas/estraga.py .. teste_leitura_do_terminal.py estragos.json <pasta de trabalho nova>
