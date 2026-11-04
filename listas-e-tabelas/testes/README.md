# testes de listas-e-tabelas

    python3 -I teste_listas_e_tabelas.py <pasta do listas_e_tabelas.py> <pasta de trabalho nova>

Tudo é inventado e sorteado, com letras de fora do ASCII. Cada projeto tem a configuração, os
modelos (o texto do item, com palavras e campos em ordem sorteada, um campo duas vezes e linhas
com dois espaços no fim, e o texto entre), três listas num arquivo JSON (de objetos com campo
único e campos montados, também dentro de uma lista da entrada; de textos; e de objetos sem
campo único), uma tabela CSV noutra pasta, com valores com vírgula, aspas e quebras de linha, e
as mudanças noutra; a peça roda de outra pasta. O teste confere regras, nunca uma frase pronta:

- em cada forma do JSON (cada recuo, também nenhum e o vazio, com e sem o escape fora do ASCII,
  e o fim sorteado) e do CSV (cada quebra de linha), o arquivo gravado é o que o `json.dumps` e
  o módulo `csv` do Python gravam nessa forma, com as entradas no fim de cada lista, na ordem,
  com as chaves na ordem das mudanças, e os campos trocados, e o resto como estava; os arquivos
  de entrada não mudam;
- o campo montado, no primeiro nível ou dentro de uma lista da entrada, é cada item pelo texto
  do modelo, lido com as quebras `\r\n` como `\n` e sem a quebra do fim, com cada campo trocado
  pelo valor (também o número), os itens juntos com as linhas do texto entre no meio (vazio, de
  uma linha ou de duas), ou um na linha seguinte ao outro sem ele;
- a chave da troca acha a linha também em outra forma Unicode;
- o arquivo sem nada de fora do ASCII nos dados recebe as entradas novas como são, sem escape;
- o valor único com outras maiúsculas, e o objeto que só difere de outro no 1 e no verdadeiro,
  não são problema;
- duas rodadas, em cópias do mesmo projeto, dão o mesmo; as mesmas mudanças de novo saem com 1,
  sem gravar nada;
- o arquivo que não volta igual (no JSON, um espaço no fim de uma linha, as quebras `\r\n`, os
  separadores sem espaço, uma chave repetida e o escape em maiúsculas; no CSV, aspas onde não
  precisa, a falta da quebra do fim e as quebras misturadas), o valor único repetido (da lista,
  em outra forma Unicode, ou das mudanças), a entrada sem ele, a entrada repetida numa lista sem
  campo único (o texto e o objeto, com as chaves e os textos em outra forma Unicode), o campo
  montado que não é lista de itens, o item sem um campo do modelo, com um a mais ou com um valor
  que não é texto nem inteiro (também dentro de uma lista da entrada), a troca sem a chave, com
  a chave de nenhuma linha ou de duas, com uma coluna que a tabela não tem, que não muda nada ou
  que troca de novo a mesma coluna da mesma linha saem com 1, com o lugar no `ERRO` (o arquivo e
  a linha em que ele deixa de voltar igual, ou as mudanças e o caminho do valor), e nada é
  gravado;
- a configuração, as mudanças, um modelo, a lista e a tabela que não servem (que faltam, que não
  se leem, que saem do molde, também com um grupo vazio, que nomeiam o que não existe, o arquivo
  de lista e de tabela, o caminho que não leva a uma lista, a tabela sem cabeçalho, com coluna
  repetida, com linha de outro tamanho ou sem a chave, o arquivo que é uma pasta ou uma das
  entradas, a configuração, as mudanças ou um modelo, mesmo quando ele se lê como lista ou como
  tabela, e o valor que não se escreve em UTF-8) saem com 2, e nada é gravado.

Precisa do `extrator_comum.py`, do `texto_comum.py` e do `documento_gerado.py`, nas pastas irmãs
da peça. Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), com as pastas do extrator e do
grava-ou-confere ao lado da cópia:

    python3 -I ../../copias-estragadas/estraga.py .. teste_listas_e_tabelas.py estragos.json <pasta de trabalho nova> --irma ../../extrator --irma ../../grava-ou-confere

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
