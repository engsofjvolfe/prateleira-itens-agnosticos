# testes de copia-para-projeto

    python3 -I teste_copia.py <pasta do copia.py> <pasta de trabalho nova>

Monta uma peça e um projeto inventados, com uma extensão de código e um sinal de
comentário que não são os de nenhuma linguagem, e um script de referência com um
cabeçalho de tamanho sorteado. O teste confere regras, nunca uma frase pronta:

- a cópia do arquivo de código é o cabeçalho mais o arquivo da peça, e a dos outros é o
  arquivo da peça, no destino dado;
- com `--conferir`, nada é gravado, as cópias em dia passam e a cópia mudada é acusada,
  pelo nome;
- sem cabeçalho no script de referência, a cópia é o arquivo como está;
- arquivo da peça que não existe e par sem destino são erro, sem gravar nada;
- duas rodadas dão o mesmo.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), com a pasta do `grava_ou_confere.py` ao
lado da cópia:

    python3 -I ../../copias-estragadas/estraga.py .. teste_copia.py estragos.json <pasta de trabalho nova> --irma ../../grava-ou-confere
