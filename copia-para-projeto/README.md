# copia-para-projeto

Leva arquivos de uma peça da prateleira para um projeto e confere que as cópias estão em
dia. Cada arquivo vai para o destino dado. O arquivo com a mesma extensão de um script do
projeto, o script de referência, recebe na frente o cabeçalho de comentário dele, como a
linha da licença; os outros, como os moldes em JSON, vão como estão.

Usa só a biblioteca padrão do Python, o `grava_ou_confere.py`, do
[grava-ou-confere](../grava-ou-confere/README.md), que grava cada cópia ou confere que ela
está em dia, e o `extrator_comum.py`, do [extrator](../extrator/README.md), que lê os
arquivos em UTF-8. Na prateleira, eles são achados nas pastas irmãs.

## Como rodar

    python3 -I <prateleira>/copia-para-projeto/copia.py <peça> <projeto> <script de referência> <arquivo da peça>=<destino no projeto>... --comentario <sinal>

- `--comentario <sinal>`: o sinal que começa uma linha de comentário nos scripts do
  projeto, como `#`. O cabeçalho são as linhas do começo do script de referência que
  começam com ele, e a linha em branco depois delas.
- `--conferir`: não grava nada; diz, para cada arquivo, se a cópia do projeto é a da peça,
  com o cabeçalho, e sai com código 1 se alguma não é.

O sinal de comentário vazio, o par sem destino e o arquivo da peça ou o script de
referência que não existe ou não se lê em UTF-8 são `ERRO`, que sai com código 2, e nada é
gravado.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../LICENSE-CONTENT.txt).*
