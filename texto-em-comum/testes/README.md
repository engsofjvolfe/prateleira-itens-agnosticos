# testes de texto-em-comum

    python3 -I teste_texto_em_comum.py <pasta do texto_em_comum.py> <pasta de trabalho nova> [semente]

Monta pastas e textos inventados. As palavras são sorteadas, cada uma diferente das outras e
com acento; a semente fixa faz o sorteio ser o mesmo em toda rodada, e outra semente pode vir
no fim. O teste confere regras, nunca uma frase pronta:

- um trecho de L palavras copiado (L pelo menos N), com outras maiúsculas, acentos escritos
  do outro jeito e outra pontuação entre as palavras, dá L − N + 1 sequências em comum,
  contadas no arquivo de onde veio; um trecho de N − 1 palavras não dá nenhuma;
- o mais parecido é o arquivo com mais sequências; no empate, o da primeira pasta dada;
- arquivo vazio é texto sem sequências; arquivo com o byte zero (também longe do começo) ou
  fora do UTF-8 não é texto; o código de saída diz se há texto em comum ou arquivo que não é
  texto;
- o que casa com `--pular` fica de fora nos dois lados, também com `--lista`, e sem
  `--pular` entra;
- um arquivo não é comparado com ele mesmo, nem quando duas pastas comparadas chegam a ele,
  e o relatório não é lido;
- com `--lista` (de arquivo ou do terminal), só os arquivos dela, cada um uma vez; lista ou
  argumento que não serve dá o código 2 e não grava nada;
- o relatório tem uma linha por arquivo, em ordem de caminho, e duas rodadas dão a mesma
  saída.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md):

    python3 -I ../../copias-estragadas/estraga.py .. teste_texto_em_comum.py estragos.json <pasta de trabalho nova>
