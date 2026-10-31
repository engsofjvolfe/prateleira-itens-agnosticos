# grava-ou-confere

Grava um documento que um script gera a partir de dados, ou confere que o documento
gravado está em dia: o mesmo que o script gravaria agora. Serve a qualquer script que gera
um documento, como um glossário, uma lista, um índice ou a cópia de um arquivo, e que
precisa de uma conferência antes de cada versão, sem gravar nada.

Usa só a biblioteca padrão do Python. Não se roda: o script que gera o documento importa o
`grava_ou_confere.py`. O [documento gerado](#o-documento-gerado), o módulo que lê o
cabeçalho, confere o arquivo do documento e monta o texto dele, também mora aqui.

## Como usar

- `opcao_conferir(leitor, ajuda)`: põe no leitor de argumentos do script (`argparse`) a
  opção `--conferir`, com a ajuda dada; nos argumentos lidos, ela liga `conferir`.
- `grava_ou_confere(arquivo, texto, conferir, falta=..., em_dia=..., gravado=...)`: no fim
  do script, com o arquivo do documento, o texto gerado agora, se é para conferir e as três
  mensagens do script. Devolve o código de saída do script.

| Caso | O que acontece | Mensagem | Código |
| --- | --- | --- | --- |
| Sem conferir | o texto vai para o arquivo, em UTF-8, com as pastas que faltam, por cima do que houver | `gravado` | 0 |
| Conferindo, com o arquivo igual ao texto | nada é gravado | `em_dia` | 0 |
| Conferindo, com o arquivo diferente ou sem ele | nada é gravado nem criado | `falta` | 1 |

O arquivo pode vir como caminho ou como texto.

## O documento gerado

O `documento_gerado.py` guarda o que os scripts que geram um documento a partir de dados
fazem do mesmo jeito antes de gravá-lo. Não se roda: as peças o importam da pasta irmã
`grava-ou-confere/` ou da própria pasta. Precisa do `extrator_comum.py`, do
[extrator](../extrator/README.md), na pasta irmã `extrator/` ou na mesma pasta.

| Função | O que faz |
| --- | --- |
| `le_cabecalho(arquivo)` | o cabeçalho que o projeto escreve para o documento, como o título e a abertura, sem os espaços e as quebras do fim; `ErroDeDados`, que diz o arquivo, quando ele não se lê em UTF-8 ou está vazio |
| `confere_destino(destino, entradas)` | `ErroDeDados`, que diz o destino, quando o arquivo do documento é um dos arquivos de entrada, pelo caminho inteiro, ou existe e não é um arquivo |
| `em_blocos(cabecalho, blocos)` | o texto do documento: o cabeçalho e os blocos, como vêm, com uma linha em branco entre um e o seguinte e uma quebra de linha no fim |

## Testes

Em [testes/](testes/README.md).
