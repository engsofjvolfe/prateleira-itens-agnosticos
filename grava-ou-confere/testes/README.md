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

## O documento gerado

    python3 -I teste_documento_gerado.py <pasta do documento_gerado.py> <pasta de trabalho nova>

Os arquivos e os textos são inventados, sorteados e com letras de fora do ASCII. O teste
confere regras, nunca uma frase pronta:

- o cabeçalho vem sem os espaços e as quebras do fim, e o vazio (também só de espaços e
  quebras), o que falta e o que não se lê em UTF-8 são `ErroDeDados` que diz o arquivo;
- o destino que é uma das entradas, também por outro caminho que dá no mesmo arquivo, e o
  que é uma pasta são `ErroDeDados` que diz o destino, e o que não existe ou é outro arquivo
  serve; a entrada que não veio (`None`) não conta, e as outras contam;
- o texto é o cabeçalho e os blocos, como vêm, com uma linha em branco entre um e o seguinte
  e uma quebra de linha no fim, e, sem bloco, só o cabeçalho com a quebra;
- duas montagens dão o mesmo.

Precisa do `extrator_comum.py`, na pasta irmã `extrator/` da peça. As cópias estragadas do
módulo estão em `estragos-documento-gerado.json`, nesta pasta:

    python3 -I ../../copias-estragadas/estraga.py .. teste_documento_gerado.py estragos-documento-gerado.json <pasta de trabalho nova> --irma ../../extrator

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
