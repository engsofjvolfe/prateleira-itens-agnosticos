# rodape

Serve para pôr o mesmo rodapé no fim de cada documento Markdown de um repositório git e para
conferir, antes de cada versão, que todos o têm, como o aviso da licença com o link para o
arquivo dela. O rodapé se escreve uma vez, num modelo, e os links do modelo valem a partir da
pasta dele, como em qualquer documento; em cada documento, a peça refaz cada link para um
arquivo a partir da pasta do documento, e o rodapé velho que um documento tem no fim, também
com o link de outra pasta, dá lugar ao dele. Os documentos são os arquivos do repositório que
seguem os padrões da configuração, e o documento novo que segue um padrão já nasce coberto.

A peça serve quando:

- os documentos são Markdown e ficam num repositório git;
- o rodapé é o mesmo texto em todos, e só o alvo dos links muda de uma pasta para a outra;
- o rodapé vem no fim de cada documento, depois de uma linha em branco.

Não serve para um cabeçalho, para um texto que muda de um documento para outro (como o título
dele), para arquivos que não são Markdown, como o código, nem para conferir que um documento
sem rodapé deve ficar sem ele: o que fica de fora se diz nos padrões de fora.

Um exemplo. Com o modelo `dados/rodape.md`, numa pasta ao lado do `LICENSE.txt` da raiz,

```markdown
---

*Texto sob a [licença do projeto](../LICENSE.txt).*
```

o documento `receitas/doces/bolo.md` termina, depois de uma linha em branco, em

```markdown
---

*Texto sob a [licença do projeto](../../LICENSE.txt).*
```

e o `LEIAME.md`, na raiz, em `*Texto sob a [licença do projeto](LICENSE.txt).*`.

O módulo comum, o [`rodape_comum.py`](#o-módulo-do-rodapé), serve também às peças que gravam
um documento (que o põem no fim dele) e às que conferem a forma de um documento (que o deixam
fora da conferência). Usa só a biblioteca padrão do Python, o git, o `extrator_comum.py`, do
[extrator](../extrator/README.md), o `markdown_comum.py`, do
[documentos](../documentos/README.md#o-módulo-de-markdown), e o `grava_ou_confere.py`, do
[grava-ou-confere](../grava-ou-confere/README.md). Na prateleira, eles são achados nas pastas
irmãs; numa cópia fora da prateleira, na mesma pasta dos scripts.

## Como rodar

    python3 -I <prateleira>/rodape/rodape.py <raiz do repositório> <configuração.json> <modelo.md> [--conferir]

- `<configuração.json>`: os padrões dos documentos, só com dados (ver
  [A configuração](#a-configuração)).
- `<modelo.md>`: o modelo do rodapé (ver [O modelo](#o-modelo)); se ele for um dos
  documentos, fica de fora deles.
- `--conferir`: nada é gravado; cada documento tem de terminar no rodapé dele.

Sem `--conferir`, o documento que não termina no rodapé dele passa a terminar: o rodapé do
modelo que ele tem no fim sai, e o dele entra; o que já termina nele não se grava. Mostra uma
linha por documento gravado, ou, com `--conferir`, uma linha `ERRO documento:linha: motivo`
por documento que não termina no rodapé dele, com a linha do rodapé que ele tem no fim ou, sem
nenhum, a última linha com texto; e um resumo, com quantos documentos e quantos gravados ou
fora do dia.

## A configuração

O molde está em `esquemas/rodape.schema.json`, com a regra de linha do
[molde comum](../extrator/README.md#o-molde-comum) do extrator:

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `documentos` | os padrões do git (pathspec) dos documentos, um ou mais, como `*.md`, que acha os `.md` de todas as pastas |
| `fora` | os padrões dos que ficam sem rodapé, que podem não ser nenhum, como os pedaços de documento que outra peça junta |

Cada padrão tem uma linha só, com alguma letra, sem repetir. Os documentos são os arquivos do
repositório, os versionados e os novos que o `.gitignore` não deixa de fora, que seguem um
padrão de `documentos` e nenhum de `fora`, em ordem.

## O modelo

O modelo é um texto Markdown, sem código, lido sem os espaços e as quebras das pontas. Cada
link dele para um arquivo, `[texto](alvo)` ou `![texto](alvo)`, vale a partir da pasta do
modelo e tem de levar a um arquivo que existe. No rodapé de um documento:

- o alvo de cada link para um arquivo é o caminho do arquivo a partir da pasta do documento,
  com `/` entre as partes, entre `<` e `>` quando tem espaço ou parênteses, e com a âncora que
  tinha;
- o link com esquema, como `https:` ou `mailto:`, e o que é só âncora, como `#fim`, ficam como
  estão, e o resto do texto também.

O documento termina no rodapé dele quando é o texto, sem os espaços e as quebras do fim, uma
linha em branco, o rodapé e uma quebra de linha; o documento vazio fica só com o rodapé. O
rodapé que um documento tem no fim é o do modelo, a partir do começo de uma linha, com
qualquer alvo nos links para arquivos e com qualquer espaço ou quebra de linha onde o modelo
tem um, seguido só de espaços e quebras.

## O módulo do rodapé

O `rodape_comum.py` guarda o que as peças fazem do mesmo jeito com o rodapé. Não se roda: as
peças o importam da pasta irmã `rodape/` ou da própria pasta.

| Função | O que faz |
| --- | --- |
| `le_modelo(caminho)` | o modelo do arquivo, ou nenhum sem o arquivo; `ErroDeDados`, que diz o arquivo, quando ele não se lê em UTF-8, está vazio, tem código ou tem um link para um arquivo que não existe |
| `rodape(modelo, documento)` | o rodapé do documento, com cada link para um arquivo a partir da pasta dele |
| `com_rodape(texto, modelo, documento)` | o texto com o rodapé do documento no fim; sem modelo, o texto como vem |
| `separa(texto, modelo)` | o texto sem o rodapé do modelo que ele tem no fim, sem os espaços e as quebras de antes dele e com uma quebra de linha no fim, e a linha em que o rodapé começa; sem rodapé no fim, ou sem modelo, o texto como vem e nenhuma linha |
| `opcao_rodape(leitor, ajuda)` | põe no leitor de argumentos (`argparse`) a opção `--rodape <modelo.md>`, com a ajuda dada; nos argumentos lidos, ela dá o caminho em `rodape`, ou nenhum |

As peças que o usam pelo `--rodape`: o [confere-forma](../confere-forma/README.md) e o
[confere-changelog](../confere-changelog/README.md), que deixam o rodapé do fim fora da
conferência, e o [divergencias](../divergencias/README.md) e o
[glossario](../glossario/README.md), que o põem no fim do documento que gravam.

## Os códigos de saída

| Caso | Código |
| --- | --- |
| os documentos gravados, ou em dia com `--conferir` | 0 |
| com `--conferir`, algum documento que não termina no rodapé dele | 1 |
| a entrada que não serve, e então nada é gravado | 2 |

A entrada que não serve, que sai como `ERRO: <motivo>`: a pasta cujos arquivos o git não
lista, como a que não é um repositório; a configuração que não é JSON ou que sai do molde; o
modelo que não serve; e o documento que não se lê em UTF-8.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../LICENSE-CONTENT.txt).*
