# texto-em-comum

Diz quais arquivos de uma pasta têm texto igual ao de arquivos de outras pastas. Serve, por
exemplo, para saber se uma pasta de ferramentas leva texto de um projeto, como aulas, livros
ou normas, antes de ela ir para outro lugar.

Texto em comum é uma sequência de N palavras seguidas que aparece igual nos dois arquivos.
Na comparação não importa maiúscula ou minúscula, acento escrito de um jeito ou de outro, nem
o que fica entre as palavras (espaço, quebra de linha, pontuação). Exemplo, com N = 4: "a
parede da célula" e "A PAREDE, da célula" são a mesma sequência.

Usa só a biblioteca padrão do Python e o `texto_comum.py`, do
[extrator](../extrator/README.md#o-módulo-de-texto), que passa o texto para a forma NFC. Na
prateleira, ele é achado na pasta irmã `extrator/`; numa cópia fora da prateleira, na mesma
pasta do script.

## Como rodar

    python3 -I <prateleira>/texto-em-comum/texto_em_comum.py <pasta examinada> <pasta comparada> [<pasta comparada> …] --palavras <N> --saida <relatório.tsv>

- `--pular <padrão>`: nome de arquivo ou de pasta que fica de fora, com tudo o que tiver
  dentro, nos dois lados (como `.git` ou `__pycache__`); aceita `*` e `?`; pode repetir.
- `--lista <arquivo>`: examina só os arquivos dessa lista, um caminho por linha, a partir da
  pasta examinada; `-` lê a lista do terminal (por exemplo, a saída de `git ls-files`).

Texto é o arquivo que se lê em UTF-8 e não tem o byte zero. Um arquivo nunca é comparado com
ele mesmo, e o relatório nunca é lido. Atalhos para pastas não são seguidos.

## O relatório

Um TSV com cabeçalho e uma linha por arquivo examinado, em ordem de caminho:

| Coluna | O que é |
| --- | --- |
| `arquivo` | o caminho, a partir da pasta examinada |
| `texto` | `sim`, ou `não` quando o arquivo não é texto (então as outras colunas ficam vazias) |
| `sequencias` | quantas sequências de N palavras o arquivo tem, cada uma contada uma vez |
| `em_comum` | quantas delas aparecem em algum arquivo comparado |
| `mais_parecido` | o arquivo comparado que tem mais delas; no empate, o primeiro na ordem das pastas dadas e dos caminhos |
| `em_comum_com_ele` | quantas o mais parecido tem |

Na tela, uma linha diz quantos arquivos foram examinados e comparados, quantos têm texto em
comum e quantos não são texto.

Sai com código 0 quando todo arquivo examinado é texto e nenhum tem texto em comum; 1 quando
algum tem texto em comum ou não é texto; 2 quando um argumento ou a lista não serve, e então
não grava nada.

## Testes

Em [testes/](testes/README.md).
