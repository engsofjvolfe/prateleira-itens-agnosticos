# leitura-do-terminal

Lê um comando de terminal como o shell lê, para o programa que precisa saber o que ele roda,
como um gancho que barra um comando. Divide o comando em palavras e operadores, respeitando aspas,
escapes e comentários; separa os comandos simples, sem os alvos de redirecionamento; acha
as palavras que o shell roda como comando, que são a primeira, menos uma atribuição como
`VAR=1`, e todas as que vêm depois de um prefixo, como `xargs`; diz se uma opção aparece
numa palavra (`-q` também em `-zq`, `--opcao` também em `--opcao=1`); e dá o comando e cada
comando de dentro dele, de `$( )` e de crases, também entre aspas, um depois do outro.
Comando com aspa, crase ou substituição sem fechar é ilegível.

Usa só a biblioteca padrão do Python. Não se roda: o `leitura_do_terminal.py` é importado, e
os prefixos vêm do programa que o importa. Os ganchos
[regras-de-codigo](../regras-de-codigo/README.md) e
[busca-por-palavra](../busca-por-palavra/README.md) a usam, da pasta irmã.

## O que dá

| Nome | O que é |
| --- | --- |
| `lidos(comando)` | para o comando e cada comando de dentro dele, na ordem: as partes (cada palavra ou operador) e as palavras de cada comando simples |
| `posicoes_de_comando(palavras, prefixos)` | as posições das palavras que rodam como comando |
| `opcao_bate(opcao, palavra)` | se a opção aparece na palavra |
| `eh_redirecionamento(operador)` | se o operador redireciona de um arquivo ou para um arquivo |
| `ComandoIlegivel` | o erro do comando que não se lê |

Os sinais da gramática do shell, como `ESCRITA` (`>`) e `TEXTO_EMBUTIDO` (`<<`), ficam no
começo do arquivo, para o programa que o importa.

## Testes

Em [testes/](testes/README.md).
