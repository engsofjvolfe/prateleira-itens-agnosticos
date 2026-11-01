# confere-changelog

Confere a forma de um changelog em Markdown, a do
[Keep a Changelog 1.1.0](https://keepachangelog.com/pt-BR/1.1.0/), com as versões do
[Versionamento Semântico 2.0.0](https://semver.org/lang/pt-BR/spec/v2.0.0.html). Serve para
o `CHANGELOG.md` de um repositório seguir, daqui a um ano como hoje, a mesma forma. Ligado
como gancho do git, antes do commit, vale em todo commit, qualquer que seja o programa que o
faz.

A forma do Markdown e a das versões ficam no código. O que muda de um uso para outro vem da
configuração, só dados: o nome da seção do que não foi publicado, a marca da versão
retirada, os tipos de mudança, o fim de cada item e os modelos dos links.

Usa só a biblioteca padrão do Python, o git (com `--indice`) e o `extrator_comum.py`, do
[extrator](../extrator/README.md), que lê a configuração pelo molde dela e o changelog em
UTF-8. Na prateleira, ele é achado na pasta irmã `extrator/`; numa cópia fora da prateleira,
na mesma pasta do script.

## Como rodar

    python3 -I <prateleira>/confere-changelog/confere_changelog.py <configuração.json> <CHANGELOG.md> [--indice]

- `--indice`: confere o changelog como o índice do git o tem, o que vai no próximo commit, e
  não o da pasta. O git o lê da pasta do arquivo, e as quebras de linha se leem como na
  leitura de um arquivo de texto.

Mostra uma linha `ERRO arquivo:linha: motivo` por problema, em ordem de linha, e um resumo
com quantos erros houve. Sai com código 0 sem erro, 1 com erro e 2 quando a configuração, o
changelog ou um argumento não serve; então nada é conferido. O changelog não serve quando
não existe ou não se lê em UTF-8 e, com `--indice`, quando o índice do git não o tem.

## O que se confere

| Parte | A forma |
| --- | --- |
| **Começo** | a primeira linha é o título, `# ` e um texto; as outras, até a primeira seção, são texto livre, sem título |
| **Seções** | a primeira é a do que não foi publicado, `## [<nao_publicado>]`, que não se repete; cada outra é uma versão, `## [<versão>] - AAAA-MM-DD`, com ` [<removida>]` no fim quando ela foi retirada |
| **Versões** | a do Versionamento Semântico inteiro, também com o pré-lançamento, como `1.0.0-rc.1`, e os metadados de construção, como `1.0.0+20130313`, pela expressão que a especificação dá; a data existe; da mais nova para a mais velha, pela precedência da especificação, sem duas com a mesma, com as datas na mesma ordem (duas versões podem ter a mesma data) |
| **Tipos de mudança** | `### <tipo>`: só os da lista, na ordem dela, sem repetir; cada tipo com um item ou mais, e cada versão com um tipo ou mais; a seção do que não foi publicado pode estar vazia |
| **Itens** | `- ` e o texto, com a continuação em linhas que começam por dois espaços; a última linha de cada item termina com o `fim_do_item` |
| **Linhas em branco** | uma antes e uma depois de cada título, e uma antes dos links; o arquivo termina com uma quebra de linha, sem linha em branco no fim |
| **Links** | só com os modelos na configuração e quando há versão: no fim, um por seção, na ordem delas, `[<título da seção>]: <link>`, com o link feito pelo modelo |

Toda outra linha é erro.

## As versões

A forma da versão é a expressão com grupos de nome que a especificação dá, na pergunta "Is
there a suggested regular expression (RegEx) to check a SemVer string?", lida só com os
algarismos do ASCII, como a especificação pede. A precedência é a do item 11 dela:

- os três números, pelo valor;
- com eles iguais, a versão com pré-lançamento vem antes da normal;
- entre dois pré-lançamentos, cada identificador, da esquerda para a direita: o que só tem
  algarismos, pelo valor e antes do que tem letra ou hífen; este, pela ordem do ASCII;
- com o começo igual, o pré-lançamento de mais identificadores vem depois;
- os metadados de construção não contam: duas versões que só mudam neles têm a mesma
  precedência e não entram as duas.

## A configuração

O molde está em `esquemas/confere-changelog.schema.json`, com a regra de linha do
[molde comum](../extrator/README.md#o-molde-comum) do extrator. A `configuracao.json` desta
pasta é a forma em português do Brasil, sem links, como a do changelog desta prateleira.

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `nao_publicado` | o nome da seção do que não foi publicado, como `Não publicado` |
| `removida` | a marca da versão retirada, como `REMOVIDO` |
| `tipos` | os tipos de mudança, na ordem em que vêm numa seção |
| `fim_do_item` | o texto com que termina cada item, como `.` |
| `links` | opcional: os modelos dos links, explicados abaixo |

Cada texto da configuração tem uma linha só, com alguma letra. Os três modelos dos links:

- `nao_publicado`: o link da seção do que não foi publicado, com `{anterior}`, a versão mais
  nova;
- `versao`: o link de uma versão, com `{versao}` e `{anterior}`, a versão logo abaixo dela;
- `primeira`: o link da versão mais velha, com `{versao}`.

É `ERRO`, com código 2: campo que o molde não conhece, campo que falta, de outro tipo, vazio
ou de mais de uma linha, nenhum tipo ou tipo repetido, e o modelo de link sem o lugar de um
campo dele ou com o de outro.

## Como ligar como gancho do git

O gancho `pre-commit` de um repositório confere, com `--indice`, o changelog que vai no
commit e barra o commit quando há erro. Um exemplo, no arquivo `.git/hooks/pre-commit` do
repositório, com permissão de rodar, em que `<prateleira>` é o caminho inteiro da
prateleira:

    #!/bin/sh
    # Antes de cada commit, confere a forma do CHANGELOG.md que vai no commit, o do indice.
    exec python3 -I <prateleira>/confere-changelog/confere_changelog.py \
        <prateleira>/confere-changelog/configuracao.json CHANGELOG.md --indice

O git roda o gancho na pasta principal do repositório, e por isso o `CHANGELOG.md` dela é o
conferido. A pasta `.git/hooks` não vai no commit: cada cópia do repositório põe o gancho de
novo.

## Testes

Em [testes/](testes/README.md).
