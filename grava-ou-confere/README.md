# grava-ou-confere

Grava um documento que um script gera a partir de dados, ou confere que o documento
gravado está em dia: o mesmo que o script gravaria agora. Serve a qualquer script que gera
um documento, como um glossário, uma lista, um índice ou a cópia de um arquivo, e que
precisa de uma conferência antes de cada versão, sem gravar nada.

Usa só a biblioteca padrão do Python. Não se roda: o script que gera o documento importa o
`grava_ou_confere.py`.

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

## Testes

Em [testes/](testes/README.md).
