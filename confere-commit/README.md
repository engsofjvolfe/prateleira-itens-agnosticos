# confere-commit

Serve para conferir um commit antes de ele se fazer: a peça roda, uma por uma, as conferências
de uma lista sobre os arquivos que vão no commit, como estão no índice do git, e sai com erro
quando alguma falha. Ligada no gancho `pre-commit` de um repositório, ela barra o commit que não
passa, qualquer que seja o programa que o faz. Cada conferência é um comando que já existe, como
um conferidor de forma ou de citações, com os padrões dos arquivos que ela olha; a lista é só
dados.

A peça serve quando:

- o repositório é git, e cada conferência é um programa que se roda por um comando e sai com 0
  quando está tudo certo;
- os arquivos que cada conferência olha se escolhem por padrões do git (pathspec);
- o que se confere é o que vai no commit, como está no índice, e não o que está na pasta.

Não serve para conferir a mensagem do commit (é o gancho `commit-msg`), nem para consertar os
arquivos: as conferências rodam numa cópia do índice, que some no fim, e nada do que um comando
grava nela vai para o repositório. Também não confere o que já está no histórico.

Um exemplo. Num repositório de receitas, com a ferramenta `ferramentas/confere_receitas.py` numa
pasta que o git não guarda, a configuração

```json
{
  "versao_schema": 1,
  "conferencias": [
    {"nome": "as receitas", "arquivos": ["receitas/*.md"], "fora": ["receitas/modelo.md"],
     "comando": ["python3", "{principal}/ferramentas/confere_receitas.py", "{arquivos}"]}
  ]
}
```

faz o commit que muda `receitas/bolo.md` e `LEIAME.md` rodar a ferramenta com
`receitas/bolo.md`, como ele está no índice; o commit que só muda o `LEIAME.md` não a roda.

Usa só a biblioteca padrão do Python, o git, o `extrator_comum.py`, do
[extrator](../extrator/README.md), que lê a configuração pelo molde dela, e o
`markdown_comum.py`, do [documentos](../documentos/README.md#o-módulo-de-markdown), que roda o
git e dá os caminhos e os padrões dele. Na prateleira, eles são achados nas pastas irmãs; numa
cópia fora da prateleira, na mesma pasta do script.

## Como rodar

    python3 -I <prateleira>/confere-commit/confere_commit.py <configuração.json>

Roda na pasta de um repositório git, ou de uma worktree dele; o gancho `pre-commit` a roda na
raiz. Mostra, de cada conferência, se ela rodou e com quantos arquivos do commit, a saída dela,
como o comando a escreve, e, quando ela sai com outro código que não 0, uma linha
`ERRO <nome>: motivo`; e um resumo, com quantas conferências, quantas rodaram e quantas deram
erro.

| Caso | Código |
| --- | --- |
| nenhuma conferência dá erro, também quando nenhuma roda | 0 |
| alguma conferência sai com outro código que não 0 | 1 |
| a entrada que não serve: a configuração, o git ou o programa de um comando | 2 |

A entrada que não serve sai como `ERRO: <motivo>`, sem rodar nenhuma conferência: a
configuração que não existe, que não é JSON ou que sai do molde, e o que o molde não vê (ver
[A configuração](#a-configuração)); a pasta que não é de um repositório git e o git que não se
acha; e o programa de um comando que não se acha. O programa que se acha e o sistema não roda,
como um arquivo que não é programa, dá a linha `ERRO <nome>: motivo` na hora dele, e a peça sai
com 2.

## O que se confere

- **Os arquivos do commit** são os que o índice muda em relação ao último commit (o `HEAD`),
  também os apagados; no primeiro commit, os do índice. No `git commit` com caminhos, o índice é
  o que o git monta para o commit, com o texto da pasta desses caminhos, e a peça o recebe pelo
  `GIT_INDEX_FILE`, como todo gancho.
- **Cada conferência**, na ordem da lista, roda quando o commit muda algum arquivo que segue um
  dos padrões dela e nenhum dos de fora. No comando, o argumento `{arquivos}` vira esses
  arquivos, os que o commit não apaga, em ordem, e a conferência que o tem e não tem nenhum deles
  não roda; a que não o tem roda também pelo arquivo apagado. O `{principal}`, dentro de
  qualquer argumento, vira a pasta principal do repositório (a da primeira worktree), onde
  ficam as pastas que o git não guarda, também quando o commit é feito numa worktree.
- **A cópia do índice:** os arquivos do índice se copiam para uma pasta nova, que some no fim, e
  cada comando roda nela. O caminho relativo de um argumento é, então, o do arquivo do índice; e
  o git, de dentro do comando, tem o repositório, a cópia e o índice do commit no ambiente
  (`GIT_DIR`, `GIT_WORK_TREE` e `GIT_INDEX_FILE`), de modo que a lista dele, como a do
  `git ls-files`, é a dos arquivos do commit.

O que fica no código é a forma que a peça trata: os dois campos do comando, `{arquivos}` e
`{principal}`, e o que o git dá (a lista das worktrees, os caminhos com `-z` e o ambiente do
índice). O resto vem da configuração.

## A configuração

O molde está em `esquemas/confere-commit.schema.json`, com a regra de linha do
[molde comum](../extrator/README.md#o-molde-comum) do extrator: cada texto tem uma linha só,
com alguma letra.

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `conferencias` | a lista das conferências, uma ou mais, na ordem em que rodam |

Cada conferência:

| Campo | O que é |
| --- | --- |
| `nome` | o nome dela, que vai na saída, sem repetir |
| `arquivos` | os padrões do git (pathspec) dos arquivos que ela olha, um ou mais, sem repetir, a partir da raiz do repositório |
| `fora` | os padrões dos arquivos que ficam de fora dela, que podem não ser nenhum, sem repetir |
| `comando` | o programa e os argumentos, um ou mais; o argumento `{arquivos}` sozinho vira os arquivos, e o `{principal}`, a pasta principal |

É `ERRO`, com código 2, que diz o arquivo: campo que o molde não conhece, campo que falta ou de
outro tipo, outra versão, nenhuma conferência, nome sem letra ou repetido, nenhum padrão ou
padrão repetido, comando vazio, e, num argumento, o `{arquivos}` no meio de outro texto ou um
campo entre chaves que não é o `{principal}`, também na conferência que não rodaria.

## Como ligar como gancho do git

O gancho `pre-commit` de um repositório roda a peça com a configuração dele e barra o commit
quando ela sai com outro código que não 0. Um exemplo, no arquivo `.git/hooks/pre-commit` do
repositório, com permissão de rodar, em que `<prateleira>` é o caminho inteiro da prateleira e a
configuração fica nos dados do repositório:

    #!/bin/sh
    # Antes de cada commit, roda as conferencias da configuracao sobre os arquivos do commit.
    exec python3 -I <prateleira>/confere-commit/confere_commit.py "$(git rev-parse --show-toplevel)/dados/confere-commit.json"

A pasta `.git/hooks` não vai no commit: cada cópia do repositório põe o gancho de novo. As
worktrees de um repositório usam os ganchos dele.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../LICENSE-CONTENT.txt).*
