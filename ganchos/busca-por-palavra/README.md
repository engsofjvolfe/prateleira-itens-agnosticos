# busca-por-palavra

Gancho contra a busca por palavra para achar ou decidir o que ler ou mudar. O caminho é
listar os títulos de um texto e ler inteiros os arquivos que tratam do assunto; o gancho
barra o atalho:

- **No terminal**, bloqueia o comando, ou um comando de dentro dele, que roda uma busca
  (como `grep` ou `git grep`) com um padrão que não é um dos livres, como o `^#` da lista
  dos títulos; com os padrões tirados de um arquivo (`-f`); ou sem padrão que se leia. O
  comando que não se lê também é bloqueado.
- **Numa ferramenta de busca** do programa, bloqueia a busca cujo padrão não é um dos
  livres.
- **Com `--exatas`**, deixa passar também, no terminal, a busca exata: a que lê só um dos
  arquivos dados, com cada padrão inteiro na forma dada para ele, como um código que o
  arquivo guarda.
  Serve ao arquivo que se consulta pelo código de cada entrada, como um dicionário de
  dúvidas em que cada uma fica sob o código do trecho de que fala, ou, num curso de
  direito, sob o número do artigo de lei. Com o código, a busca acha todas as entradas que
  o guardam, sempre as mesmas, sem ler o arquivo inteiro.

Serve à etapa em que tudo se lê inteiro, como a construção da base de um material: a
análise de cada parte, a pesquisa, a forma. Quando a base já dá o endereço de cada coisa, a
busca só acha o lugar, e o que ela acha se lê inteiro, sem escolher o que ler dele; aí o
gancho sai da configuração do projeto.

O motivo do bloqueio é o texto que se dá ao gancho em `--motivo`, como o de `busca.md`, com a
parte do comando que o causou.

Pode barrar a mais, nunca a menos: os padrões de uma busca são o valor de cada opção de
padrão (`-e x`, `-ex`, `--regexp=x`) e, sem nenhuma, a primeira palavra solta; os arquivos
são as outras soltas. Solta é a palavra que não é opção nem valor de opção de padrão, e toda
palavra depois de `--`; assim, o valor de uma opção que o gancho não conhece, como o `5` de
`-m 5`, conta como arquivo. Um comando de busca de mais de uma palavra, como `git grep`,
conta também com outras palavras no meio (`git -C pasta grep`); e uma palavra depois de um
prefixo, como `xargs`, conta como comando. A busca feita por outro programa, como `sed` ou
`awk` com um padrão, não é vista.

Usa só a biblioteca padrão do Python, o `extrator_comum.py`, do
[extrator](../../extrator/README.md), que lê a configuração pelo molde dela, a
[leitura-do-terminal](../leitura-do-terminal/README.md), que lê o comando e os prefixos do
shell, e o [protocolo](../protocolo/README.md), que lê o protocolo do programa que roda o
gancho; os três são achados onde a prateleira os põe.

## Como rodar

O programa que roda os ganchos chama este antes de cada chamada da ferramenta de terminal e
das de busca, e manda o evento pela entrada padrão, em JSON:

    python3 -I <prateleira>/ganchos/busca-por-palavra/busca_por_palavra.py --config <configuração.json> \
        --terminal <terminal.json> --protocolo <protocolo.json> --motivo <texto>

- `--terminal`: a configuração da
  [leitura-do-terminal](../leitura-do-terminal/README.md#a-configuração), com os prefixos
  do shell, como a `configuracao.json` de lá.
- `--protocolo`: o protocolo do programa, na forma do [protocolo](../protocolo/README.md):
  dele vêm o evento, a resposta que nega e as ferramentas de terminal e de busca, com o
  campo do comando e o do padrão.
- `--motivo`: o texto do motivo do bloqueio, que vem antes da parte que bloqueou, como o
  `busca.md` desta pasta.
- `--exatas <arquivo> <forma>`: o arquivo de uma busca exata e a forma de cada padrão dela,
  uma expressão regular, que o padrão segue inteiro; a opção vem uma vez para cada arquivo,
  cada um com a sua forma. O caminho de cada arquivo da busca parte da pasta de onde o
  comando roda, que o evento traz. No comando que o programa roda, a forma vai entre aspas
  simples, para o terminal não ler nada dela. A forma não aceita sinal que a busca lê como
  expressão, como `.`, `*` ou `[`: com ele, o padrão acharia mais que o código, como uma
  palavra no meio de `.*`.

A resposta sai pela saída padrão só quando bloqueia: a que nega, do protocolo, com o motivo.
Configuração, configuração da leitura do terminal ou protocolo fora do molde ou com campo
que falta, a falta da configuração da leitura do terminal e do texto do motivo, evento que
não é o de antes de uma chamada, ferramenta que o protocolo não dá como de terminal nem de
busca e, com `--exatas`, o arquivo que não existe e a forma que não é expressão regular dão
erro.

## A configuração

O molde está em `esquemas/busca-por-palavra.schema.json`. A `configuracao.json` desta pasta
é a de uso geral: os comandos de busca do terminal, que valem para qualquer programa. Os
prefixos do shell ficam na configuração da leitura do terminal.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `padroes_livres` | os padrões que uma busca pode ter, como `^#`, que lista os títulos |
| `buscas` | cada comando de busca do terminal: o `comando`, de uma ou mais palavras, as `opcoes_do_padrao`, que trazem um padrão, e as `opcoes_de_arquivo`, que tiram os padrões de um arquivo |

## Testes

Em [testes/](testes/README.md).
