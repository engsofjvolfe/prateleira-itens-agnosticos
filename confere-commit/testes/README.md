# testes de confere-commit

    python3 -I teste_confere_commit.py <pasta do confere_commit.py> <pasta de trabalho nova>

A pasta de trabalho precisa ser nova; o teste escreve nela. Tudo é inventado e sorteado, sempre
igual, porque a semente é fixa, com letras de fora do ASCII e espaços nos nomes: os
repositórios git, as pastas, os arquivos e os textos, os nomes e os padrões das conferências e o
código da que falha. Cada conferência roda a `conferencia_inventada.py`, desta pasta, que grava
num registro o que recebeu (os arquivos, a pasta em que rodou, o texto de cada arquivo e os
arquivos que o git dá nela) e sai com o código dado. O teste confere regras, nunca uma frase
pronta, e precisa do git, que ele roda sem a configuração do sistema e da conta, sem nada do git
de fora e sem subir da pasta de trabalho, e das pastas irmãs `extrator/` e `documentos/` da peça.

O repositório tem, no commit, um arquivo que muda, com um texto no índice e outro na pasta, um
novo, um apagado, um que segue um padrão de fora e um de outro padrão; e, fora do commit, um
igual ao do último commit, um que não está no índice e uma pasta que o git não guarda, só na
pasta principal, com uma conferência dentro. Confere:

- cada conferência roda só quando o commit muda um arquivo dos padrões dela e de nenhum dos de
  fora; com o `{arquivos}`, ela recebe esses arquivos, em ordem, sem os apagados, sem os que não
  estão no índice e sem os de outros padrões, com o texto do índice, e não o da pasta; sem o
  `{arquivos}`, roda também pelo arquivo apagado;
- a conferência roda numa pasta que não é a do repositório, em que o git dá os arquivos do
  índice;
- o `{principal}` vira a pasta principal do repositório, também numa worktree, em que os
  arquivos do commit são os do índice dela;
- a conferência que sai com outro código que não 0 dá uma linha `ERRO` com o nome dela, e a peça
  sai com 1; sem nenhuma, com 0; o resumo conta as conferências, as rodadas e as com erro;
- pelo gancho `pre-commit` do git, o commit com uma conferência que falha não se faz, e o que
  passa se faz; no commit com caminhos, a conferência recebe só eles, com o texto da pasta, que
  vai no commit; com outro índice, dado ao git pelo caminho a partir da pasta, ela recebe os
  arquivos dele;
- no primeiro commit do repositório, os arquivos do índice contam;
- saem com 2, com uma linha `ERRO`, sem rodar nenhuma conferência: a configuração que não
  existe, que não é JSON, de outra versão, sem conferências, com campo que o molde não conhece,
  com conferência de campo que o molde não conhece ou sem um campo, com nome sem letra, com o
  mesmo nome duas vezes, sem padrões ou com padrão repetido, com comando vazio, com o
  `{arquivos}` no meio de outro texto ou com um campo que não existe, numa conferência que não
  rodaria; o programa que não se acha; a pasta que não é de um repositório git; e o git que não
  se acha;
- o programa que se acha e não roda sai com 2, com uma linha `ERRO` com o nome da conferência,
  contado no resumo;
- duas rodadas dão a mesma saída.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não passou, e
sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), rodado desta pasta, com as duas pastas irmãs:

    python3 -I ../../copias-estragadas/estraga.py .. teste_confere_commit.py estragos.json <pasta de trabalho nova> --irma ../../extrator --irma ../../documentos

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
