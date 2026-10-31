# regras-de-codigo

Gancho que cobra regras de código da IA em três momentos de cada tarefa:

- **Antes de escrever um arquivo** de código ou de dados: na primeira escrita da tarefa,
  entrega as regras. Anota cada arquivo escrito. O arquivo de um formato da lista
  `sem_conferencia` da configuração, como um texto ou uma planilha, fica de fora.
- **Antes de um comando de terminal**: bloqueia o comando que escreve em arquivo (`>`,
  `tee`, `sed -i`…), que roda código escrito dentro dele (`python3 -c`, `<<FIM`, um
  interpretador sem arquivo…) ou que não se lê (aspas sem fechar). Entre aspas, `>` e `<<`
  são texto e passam; dentro de `$( )` e de crases, o comando é lido também.
- **Ao encerrar a resposta**: se a tarefa escreveu arquivos de código ou de dados, não
  deixa encerrar e pede a conferência de cada um contra as regras. Na volta da
  conferência, libera.

Pode barrar a mais, nunca a menos: uma palavra que aparece depois de um prefixo (como
`xargs`) conta como comando, um interpretador chamado sem arquivo é barrado, e o arquivo
sem extensão, ou de uma extensão que a lista `sem_conferencia` não traz, pede a
conferência.

Usa só a biblioteca padrão do Python; lê a configuração pelo molde dela e os textos com o
`extrator_comum.py`, do [extrator](../../extrator/README.md), o comando de terminal e os
prefixos do shell com a [leitura-do-terminal](../leitura-do-terminal/README.md) e o
protocolo do programa com o [protocolo](../protocolo/README.md), das pastas irmãs. Nenhum
texto, nome de ferramenta ou lista de comandos fica no código: tudo vem das configurações,
do protocolo e dos arquivos de texto.

## Como rodar

O programa que roda os ganchos chama este antes de cada chamada das ferramentas que
escrevem arquivo e da de terminal, e no fim de cada resposta, e manda o evento pela entrada
padrão, em JSON. O mesmo comando serve aos três momentos:

    python3 -I <prateleira>/ganchos/regras-de-codigo/regras_de_codigo.py --config <configuração.json> \
        --terminal <terminal.json> --protocolo <protocolo.json> --regras <texto> --fim <texto> --bloqueio <texto>

- `--terminal`: a configuração da
  [leitura-do-terminal](../leitura-do-terminal/README.md#a-configuração), com os prefixos
  do shell, como a `configuracao.json` de lá.
- `--protocolo`: o protocolo do programa, na forma do [protocolo](../protocolo/README.md):
  dele vêm o evento, as respostas (a que dá contexto, com as regras; a que nega, com o
  bloqueio; e a que trava o fim), a ferramenta de terminal, com o campo do comando, e os
  campos do caminho do arquivo escrito.
- `--regras <arquivo>`: um texto de regras; pode repetir, e os textos são entregues na
  ordem dada. A regra que só vale para um projeto fica num texto guardado no próprio
  projeto.
- `--fim <arquivo>`: a ordem de conferir, que vem depois das regras e antes da lista dos
  arquivos.
- `--bloqueio <arquivo>`: o aviso do bloqueio no terminal, que vem antes da parte do comando
  que bloqueou.

A resposta sai pela saída padrão, em JSON, só quando há o que dizer: as regras, o bloqueio
ou a trava do fim. Configuração, configuração da leitura do terminal ou protocolo fora do
molde, a falta da configuração da leitura do terminal, evento desconhecido, sessão sem id,
ferramenta sem campo de caminho conhecido e texto que falta no comando dão erro.

## A configuração

O molde está em `esquemas/regras-de-codigo.schema.json`. O caminho da pasta parte da pasta
da configuração. A `configuracao.json` desta pasta é a de uso geral: os comandos do
terminal e os formatos de texto, que valem para qualquer programa. Os prefixos do shell
ficam na configuração da leitura do terminal.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `estado` | a pasta da anotação: um arquivo por sessão, com o nome tirado do id dela, que guarda os arquivos escritos e se apaga ao fim de cada tarefa |
| `sem_conferencia` | os formatos de arquivo, pela extensão (como `.md`), que não recebem as regras nem a conferência, sem contar maiúsculas |
| `terminal.destinos_livres` | destinos para onde escrever não conta como escrita, como `/dev/null` |
| `terminal.sempre_escrevem` | comandos que sempre escrevem, como `tee` |
| `terminal.escrevem_com_opcao` | para cada comando, as opções que o fazem escrever ou rodar código escrito no comando; a opção curta conta também junto de outras (`-pi` tem `-i`), e a longa também com `=valor` |
| `terminal.leem_codigo_sem_arquivo` | interpretadores: chamados sem nenhum arquivo, leem código do terminal |

## Os textos

- `gerais.md`: as regras de código, para qualquer projeto.
- `fim.md`: a ordem de conferir.
- `terminal.md`: o aviso do bloqueio.

## Testes

Em [testes/](testes/README.md).
