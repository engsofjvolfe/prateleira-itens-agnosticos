# leitura-do-terminal

Lê um comando de terminal como o shell lê, para o programa que precisa saber o que ele roda,
como um gancho que barra um comando. Divide o comando em palavras e operadores, respeitando
aspas, escapes e comentários; separa os comandos simples, sem os alvos de redirecionamento;
acha as palavras que o shell roda como comando, que são a primeira, menos uma atribuição
como `VAR=1`, e todas as que vêm depois de um prefixo, como `xargs`; acha um comando de uma
ou mais palavras, como `git grep`, também com outras palavras no meio (`git -C pasta grep`),
e cada vez que um comando, ou um de dentro dele, roda um dos comandos procurados; diz se uma
opção aparece numa palavra (`-q` também em `-zq`, `--opcao` também em `--opcao=1`); e dá o
comando e cada comando de dentro dele, de `$( )` e de crases, também entre aspas, um depois
do outro. Comando com aspa, crase ou substituição sem fechar é ilegível.

Usa só a biblioteca padrão do Python e o `extrator_comum.py`, do
[extrator](../../extrator/README.md), que lê a configuração pelo molde dela; ele é achado
onde a prateleira o põe. Não se roda: o `leitura_do_terminal.py` é importado. Os ganchos
[regras-de-codigo](../regras-de-codigo/README.md),
[busca-por-palavra](../busca-por-palavra/README.md) e
[leitura-completa](../leitura-completa/README.md) a usam, da pasta irmã, e recebem a
configuração dela no `--terminal`.

## O que dá

| Nome | O que é |
| --- | --- |
| `lidos(comando)` | para o comando e cada comando de dentro dele, na ordem: as partes (cada palavra ou operador) e as palavras de cada comando simples |
| `prefixos_do_terminal(arquivo)` | os prefixos da configuração, lida pelo molde dela; `ErroDeDados`, do módulo comum, que diz o caminho de cada valor fora do molde |
| `posicoes_de_comando(palavras, prefixos)` | as posições das palavras que rodam como comando |
| `depois_do_comando(comando, palavras)` | as palavras depois do comando (a lista das palavras dele, uma ou mais), quando as palavras começam por ele: a primeira pelo nome, sem o caminho, e as outras na ordem, com outras palavras no meio; `None` quando não começam |
| `comandos_achados(comando, procurados, prefixos)` | cada vez que o comando, ou um comando de dentro dele, roda um dos procurados (cada um a lista das palavras dele), na ordem: o índice do procurado, as palavras depois dele e a parte do comando simples da palavra dele em diante; `ComandoIlegivel` quando um comando não se lê |
| `opcao_bate(opcao, palavra)` | se a opção aparece na palavra |
| `eh_redirecionamento(operador)` | se o operador redireciona de um arquivo ou para um arquivo |
| `ComandoIlegivel` | o erro do comando que não se lê |

Os sinais da gramática do shell, como `ESCRITA` (`>`) e `TEXTO_EMBUTIDO` (`<<`), ficam no
começo do arquivo, para o programa que o importa.

## A configuração

O molde está em `esquemas/leitura-do-terminal.schema.json`. A `configuracao.json` desta
pasta é a de uso geral: os prefixos do shell, que valem para qualquer programa.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `prefixos` | palavras depois das quais as outras também contam como comando, como `xargs` ou `-exec` |

## Testes

Em [testes/](testes/README.md).
