# testes de grava-ou-confere

    python3 -I teste_grava_ou_confere.py <pasta do grava_ou_confere.py> <pasta de trabalho nova>

Tudo é inventado: os arquivos, em pastas que ainda não existem, os textos, sorteados e
sempre com letras de fora do ASCII, e as mensagens. O teste confere o que a peça faz, nunca
uma frase pronta:

- sem conferir, o texto vai para o arquivo, em UTF-8, com as pastas que faltam, por cima
  do que houver, sai a mensagem de gravado e o código é 0;
- conferindo, nada é gravado nem criado; sai a mensagem de em dia, com 0, quando o arquivo
  é o texto, e a de falta, com 1, quando é outro ou não existe;
- o arquivo pode vir como caminho ou como texto;
- a opção `--conferir` liga `conferir` nos argumentos lidos, e a ajuda dada aparece na
  ajuda do script;
- duas rodadas dão o mesmo.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md):

    python3 -I ../../copias-estragadas/estraga.py .. teste_grava_ou_confere.py estragos.json <pasta de trabalho nova>
