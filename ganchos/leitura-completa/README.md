# leitura-completa

Gancho da leitura completa: todo documento se lê inteiro e se analisa, do começo ao fim. O
gancho barra todo meio de ler um documento cortando partes:

- **No terminal**, barra o comando que roda um comando que corta um documento, seja busca
  por palavra (`grep`, `rg`, `git grep`), seja recorte de linhas ou de trechos (`head`,
  `tail`, `sed`, `awk`, `cut`, `jq`). Vale também dentro de outro comando, de `$( )` ou de
  crases, e depois de um prefixo, como `xargs`. O comando que não se lê (aspas sem fechar)
  também é barrado.
- **Nas ferramentas de busca e nas que resumem** do programa, barra sempre: a busca acha
  pedaços, e o resumo é a leitura feita por outro modelo.
- **Nas ferramentas de leitura**, deixa passar só três leituras: a que começa na primeira
  linha do arquivo, a que continua na linha seguinte à última lida e a que repete o último
  pedaço, como quando ele não chegou porque o programa recusou a leitura grande demais. A
  leitura que começa em outra linha é barrada. O gancho anota, para a sessão, até onde cada
  arquivo foi lido; o arquivo lido até o fim perde a anotação.
- **Ao encerrar a resposta**, se há arquivo lido só em parte, trava, com o texto de `--fim`
  e, para cada arquivo, as linhas lidas e as que ele tem. As anotações ficam, para a leitura
  continuar. Na volta da trava, libera e apaga as anotações da sessão: a trava vem uma vez
  só.

O motivo do bloqueio é o texto de `--motivo`, como o de `motivo.md`, seguido da parte que
bloqueou:

- no terminal, a parte do comando da palavra que corta em diante;
- numa busca ou num resumo, o nome da ferramenta;
- numa leitura, o arquivo, as linhas lidas e as que ele tem, como `caminho: lidas/total`.

A trava do fim lista os arquivos do mesmo jeito, um por linha, na ordem dos caminhos.

Pode barrar a mais, nunca a menos:

- um comando que corta conta em qualquer lugar de comando, também quando corta a saída de
  outro comando, e não um arquivo;
- o comando de mais de uma palavra, como `git grep`, conta também com outras palavras no
  meio (`git -C pasta grep`), e uma palavra depois de um prefixo conta como comando;
- a leitura que volta para o meio do que já foi lido é barrada, menos a repetição do último
  pedaço.

O erro ao tratar uma chamada também a barra, com o erro como motivo: a configuração ou a da
leitura do terminal fora do molde, o texto do motivo que falta, a ferramenta que o protocolo
não dá, a entrada fora da forma.

O que o gancho não vê:

- o arquivo que não é texto UTF-8, como uma imagem ou um PDF, que fica de fora;
- o corte que o próprio programa faz no que a ferramenta entrega, como a linha longa demais
  encurtada ou a saída do terminal grande demais;
- a leitura feita por um meio que nem a configuração nem o protocolo dão, como um script que
  mostra um pedaço de um arquivo;
- se o programa recusou uma leitura que passou pelo gancho, ela continua anotada como
  feita; a repetição do último pedaço serve a esse caso.

Serve no lugar do [busca-por-palavra](../busca-por-palavra/README.md) quando nem a busca por
um padrão livre, como a lista dos títulos, deve passar.

Usa só a biblioteca padrão do Python e três outras peças, achadas onde a prateleira as põe:

- a [leitura-do-terminal](../leitura-do-terminal/README.md), que lê o comando e os prefixos
  do shell;
- o [protocolo](../protocolo/README.md), que lê o protocolo do programa que roda o gancho e
  dá o arquivo da anotação de cada arquivo lido, na pasta da sessão;
- o `extrator_comum.py`, do [extrator](../../extrator/README.md), que lê a configuração pelo
  molde dela e os textos do motivo e do fim.

## Como rodar

O programa que roda os ganchos chama este antes de cada chamada da ferramenta de terminal,
das de busca, das que resumem e das de leitura, e no fim de cada resposta. O evento chega
pela entrada padrão, em JSON, e o mesmo comando serve aos dois momentos:

    python3 -I <prateleira>/ganchos/leitura-completa/leitura_completa.py --config <configuração.json> \
        --terminal <terminal.json> --protocolo <protocolo.json> --motivo <texto> --fim <texto>

- `--terminal`: a configuração da
  [leitura-do-terminal](../leitura-do-terminal/README.md#a-configuração), com os prefixos
  do shell, como a `configuracao.json` de lá.
- `--protocolo`: o protocolo do programa, na forma do [protocolo](../protocolo/README.md).
  Dele vêm os eventos, a resposta que nega e a que trava, e o aviso de que o fim já foi
  travado uma vez. Vêm também as ferramentas:
  - a de terminal, com o campo do comando;
  - as de busca e as que resumem;
  - as de leitura, com os campos do caminho, do começo e das quantas, as linhas que ela lê
    sem o campo das quantas e o número que ela dá à primeira linha.
- `--motivo`: o texto do motivo do bloqueio, que vem antes da parte que bloqueou, como o
  `motivo.md` desta pasta.
- `--fim`: o texto da trava do fim, que vem antes da lista dos arquivos lidos em parte, como
  o `fim.md` desta pasta.

A resposta sai pela saída padrão, em JSON, só quando há o que dizer: o bloqueio ou a trava
do fim. No fim de uma resposta, o erro sai como erro, sem travar: a configuração ou a da
leitura do terminal fora do molde, o texto do fim que falta, a sessão sem id. O mesmo vale,
em qualquer momento, para o protocolo que não se lê, a entrada que não é JSON e o evento
desconhecido.

## A anotação

Cada arquivo lido em parte tem a sua anotação, um arquivo na pasta da sessão, dentro da
pasta `estado` da configuração; os nomes da pasta e do arquivo vêm do id da sessão e do
caminho, pelo [protocolo](../protocolo/README.md#o-que-dá). A anotação é um objeto JSON com o
caminho inteiro do arquivo, sem atalhos nem `..`, e três números: a linha em que começou o
último pedaço, as linhas lidas e as que o arquivo tem, contadas a partir de 0.

- O caminho de uma leitura parte da pasta de onde a ferramenta roda, que o evento traz.
- As linhas são as separadas pela quebra de linha; a quebra no fim do arquivo não abre outra
  linha.
- O começo da leitura antes da primeira linha conta como a primeira linha. O começo e as
  quantas são números inteiros; o começo abaixo de 0 e as quantas abaixo de 1 são erro.

A anotação se grava de uma vez: o texto vai para um arquivo novo, na pasta `estado`, que
toma o lugar dela. Assim, a leitura de outra chamada, ao mesmo tempo, vê a anotação de antes
ou a de depois, nunca metade; e as leituras de dois arquivos não mexem uma na anotação da
outra.

## A configuração

O molde está em `esquemas/leitura-completa.schema.json`, com a regra de linha do
[molde comum](../../extrator/README.md#o-molde-comum) do extrator. O caminho da pasta parte
da pasta da configuração. A `configuracao.json` desta pasta é a de uso geral: os comandos
que cortam, que valem para qualquer programa. Os prefixos do shell ficam na configuração da
leitura do terminal.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `estado` | a pasta das anotações, uma pasta por sessão |
| `comandos` | os comandos que cortam um documento, cada um de uma ou mais palavras, numa linha só |

## Os textos

- `motivo.md`: o motivo do bloqueio.
- `fim.md`: a trava do fim.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
