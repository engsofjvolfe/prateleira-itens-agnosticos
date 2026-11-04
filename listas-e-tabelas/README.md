# listas-e-tabelas

Serve para mudar os dados que um projeto guarda em listas dentro de arquivos JSON e em tabelas
CSV sem que o resto do arquivo mude: a peça junta entradas novas ao fim de uma lista e troca
campos de linhas de uma tabela, e grava cada arquivo na forma que ele já tinha (o mesmo recuo, o
mesmo escape, as mesmas quebras de linha), de modo que a diferença no arquivo é só o que se
juntou ou se trocou. As mudanças vêm num arquivo de dados, conferido inteiro antes de qualquer
gravação: com qualquer problema, nada se grava. O campo de texto que se monta de dados, como uma
citação com a obra, as páginas e o trecho, vem nas mudanças só com os dados, e a peça o monta
por um modelo do projeto.

A peça serve quando:

- a lista está dentro de um objeto, num arquivo JSON gravado pelo `json.dumps` do Python, com
  recuo ou numa linha só;
- a lista cresce por entradas novas, no fim, e nenhuma pode se repetir: pelo valor de um campo,
  ou pela entrada inteira;
- a tabela é um CSV com cabeçalho, separado por vírgula, com aspas duplas só onde precisa (a
  forma do módulo `csv` do Python), e cada linha se acha pelo valor de uma coluna;
- a tabela muda campo a campo, nas linhas que ela já tem.

Não serve para apagar, reordenar ou mudar uma entrada que já está numa lista, nem para juntar ou
apagar linhas de uma tabela; nem para a lista que é o próprio arquivo, sem um objeto em volta;
nem para um JSON numa forma que o `json.dumps` não refaz, como objetos escritos numa linha só
dentro de um arquivo com recuo, ou um CSV de outro dialeto, como o separado por ponto e vírgula,
que a peça recusa sem gravar nada; nem para YAML, TOML ou outros formatos. O documento que um
projeto grava a partir de uma lista fica com a peça que o grava, como o
[glossario](../glossario/README.md) ou o [divergencias](../divergencias/README.md), e a forma de
cada entrada, campo por campo, com o molde do arquivo, que confere a peça que o lê.

Um exemplo. Com a configuração `dados/listas-e-tabelas.json`

```json
{
  "versao_schema": 1,
  "modelos": {"livro": {"item": "livro.md"}},
  "listas": {
    "receitas": {"arquivo": "receitas.json", "lista": "receitas", "unico": "nome", "montados": {"fonte": "livro"}}
  },
  "tabelas": {"precos": {"arquivo": "../planilhas/precos.csv", "chave": "codigo"}}
}
```

o modelo `dados/livro.md`

```text
{titulo}, p. {paginas}
```

e as mudanças

```json
{
  "versao_schema": 1,
  "listas": {"receitas": [{"nome": "Pão de queijo", "minutos": 40,
                           "fonte": [{"titulo": "Cozinha mineira", "paginas": "12-13"}]}]},
  "tabelas": {"precos": [{"codigo": "F-07", "preco": "12,50"}]}
}
```

a receita entra no fim da lista `receitas` de `dados/receitas.json`, com
`"fonte": "Cozinha mineira, p. 12-13"`, se nenhuma outra receita se chama "Pão de queijo"; e,
em `planilhas/precos.csv`, a linha de `codigo` F-07 passa a ter `"12,50"` no `preco`, entre
aspas por causa da vírgula. O resto dos dois arquivos fica como estava, letra por letra.

Usa só a biblioteca padrão do Python, o `extrator_comum.py` e o `texto_comum.py`, do
[extrator](../extrator/README.md#o-módulo-comum), e o `documento_gerado.py`, do
[grava-ou-confere](../grava-ou-confere/README.md#o-documento-gerado). Na prateleira, eles são
achados nas pastas irmãs; numa cópia fora da prateleira, na mesma pasta dos scripts.

## Como rodar

    python3 -I <prateleira>/listas-e-tabelas/listas_e_tabelas.py <configuração.json> <mudanças.json>

- `<configuração.json>`: as listas, os modelos e as tabelas do projeto (ver
  [A configuração](#a-configuração)).
- `<mudanças.json>`: as entradas e as trocas (ver [As mudanças](#as-mudanças)).

Mostra uma linha por lista e por tabela mudadas, com o arquivo e quantas entradas se juntaram ou
quantos campos se trocaram, e um resumo. Com problema, mostra uma linha `ERRO` por problema e um
resumo, e nada é gravado (ver [Os problemas](#os-problemas)).

## A configuração

O molde está em `esquemas/listas-e-tabelas.schema.json`, com a regra de linha do
[molde comum](../extrator/README.md#o-molde-comum) do extrator. Os arquivos valem a partir da
pasta da configuração.

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `listas` | opcional: cada lista, pelo nome, com o `arquivo` JSON, o caminho da `lista` dentro dele, com `/` entre as chaves (como `grupo/nomes`), e, opcionais, o campo `unico` das entradas e os campos `montados`, cada um com o nome do modelo que o monta |
| `modelos` | opcional: cada modelo, pelo nome, com o arquivo do `item` e, opcional, o do texto `entre` dois itens (ver [Os campos montados](#os-campos-montados)) |
| `tabelas` | opcional: cada tabela, pelo nome, com o `arquivo` CSV e a coluna `chave`, cujo valor acha a linha |

Cada grupo, quando vem, tem um nome ou mais. Um arquivo pode ter mais de uma lista, mas não pode
ser de lista e de tabela.

## As mudanças

O molde está em `esquemas/mudancas.schema.json`:

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `listas` | para cada lista, pelo nome da configuração, as entradas que se juntam ao fim dela, uma ou mais, na ordem, cada uma com as chaves na ordem em que vão para o arquivo |
| `tabelas` | para cada tabela, pelo nome da configuração, as trocas, uma ou mais, cada uma um objeto com a coluna `chave` da tabela, com o valor que acha a linha, e cada coluna que muda, com o valor novo, todos textos |

As mudanças têm ao menos uma lista ou uma tabela, e cada grupo, quando vem, um nome ou mais. Um
arquivo de mudanças se aplica uma vez: aplicado de novo, as entradas se repetiriam e as trocas
não mudariam nada, e os dois são problema.

## Os campos montados

O modelo é o texto do `item` e, opcional, o texto `entre` dois itens, cada um o texto de um
arquivo em UTF-8, com cada quebra de linha como `\n` e sem a quebra do fim. Os campos do modelo
são os `{campo}` do texto do item, de letras, números e `_`.

Na entrada das mudanças, em qualquer nível dela, também dentro de uma lista, o campo que a lista
monta vem como uma lista de itens, um ou mais, cada um um objeto com os campos do modelo, e só
eles, cada valor um texto ou um número inteiro. No arquivo, ele vira um texto: cada item é o
texto do item, com cada `{campo}` trocado pelo valor dele, e os itens vêm um na linha seguinte ao
outro, com as linhas do texto entre no meio, quando o modelo o tem. O texto entre vazio deixa uma
linha em branco entre os itens.

Com o modelo do item

```text
{obra}, p. {paginas}
"{trecho}"
```

e o texto entre vazio, os itens `{"obra": "Atlas", "paginas": 12, "trecho": "uma frase"}` e
`{"obra": "Guia", "paginas": "3-4", "trecho": "outra"}` dão

```text
Atlas, p. 12
"uma frase"

Guia, p. 3-4
"outra"
```

Com o texto entre `ou`, a linha em branco dá lugar a uma linha `ou`.

## A forma de cada arquivo

A forma sai do próprio arquivo, e cada arquivo tem de voltar igual, letra por letra, lido e
gravado de novo nela, antes de qualquer mudança:

- **JSON:** o texto que o `json.dumps` do Python grava, com o separador padrão: com o recuo da
  segunda linha (espaços ou tabulação), ou numa linha só; com o escape `\uXXXX` dos caracteres
  de fora do ASCII quando o arquivo só tem ASCII e os dados têm algum caractere de fora (sem
  nada de fora nos dados, as entradas novas vão como são, sem escape); e com o que vem depois do
  valor, como a quebra de linha do fim. As chaves de cada objeto ficam na ordem em que estão.
- **CSV:** o do módulo `csv` do Python, separado por vírgula, com aspas duplas só onde precisa,
  com o cabeçalho na primeira linha, sem coluna repetida, cada linha com os campos dele, e com a
  quebra de linha com que o arquivo termina (`\r\n`, `\n` ou `\r`).

Cada arquivo se lê e se grava em UTF-8, com as quebras de linha como estão.

## Os problemas

São problema, cada um numa linha `ERRO`, e nada é gravado:

| Problema | Onde sai o ERRO |
| --- | --- |
| o arquivo que não volta igual na forma que se tira dele | no arquivo, na primeira linha em que ele muda |
| a entrada sem o campo único, ou com o valor dele igual ao de outra entrada, da lista ou das mudanças; sem campo único, a entrada igual a outra; os textos, também as chaves, se comparam na forma Unicode NFC, e as maiúsculas contam | nas mudanças, no caminho do valor, com o lugar da outra |
| o campo montado que não é uma lista de itens; o item sem um campo do modelo, com um campo que o modelo não usa ou com um valor que não é texto nem número inteiro | nas mudanças, no caminho do valor |
| a troca sem a chave; a chave que nenhuma linha tem, ou que mais de uma tem, na forma Unicode NFC; a coluna que a tabela não tem; a troca que não muda nada; e a que troca de novo a mesma coluna da mesma linha | nas mudanças, no caminho do valor |

A linha sai como `ERRO <arquivo>:<linha>: <motivo>` ou `ERRO <mudanças>: <caminho>: <motivo>`,
com o caminho do valor nas mudanças, como `/listas/receitas/0/nome`, e o resumo diz quantas
mudanças e quantos erros.

## Os códigos de saída

| Caso | Código |
| --- | --- |
| os arquivos gravados | 0 |
| problema, e então nada é gravado | 1 |
| a entrada que não serve, e então nada é gravado | 2 |

A entrada que não serve, que sai como `ERRO: <motivo>`: a configuração ou as mudanças que faltam,
que não se leem em UTF-8, que não são JSON ou que saem do molde (campo que ele não conhece, campo
que falta, valor fora da forma, grupo vazio); o nome de lista ou de tabela das mudanças que a
configuração não tem; o campo montado por um modelo que a configuração não tem; o arquivo de
lista e de tabela; o arquivo de um modelo que falta ou que não se lê em UTF-8, e o item sem
texto; o arquivo de lista ou de tabela que falta, que não se lê em UTF-8, como JSON ou como CSV,
que é uma pasta ou uma das entradas (a configuração, as mudanças ou o arquivo de um modelo); o
caminho da lista que não leva a uma lista; a tabela sem cabeçalho, com uma coluna repetida, com
uma linha de outro tamanho ou sem a coluna da chave; e o texto mudado que não se escreve em
UTF-8.

## Os módulos

A peça tem três módulos, que não se rodam e que o `listas_e_tabelas.py` importa desta pasta:

| Módulo | O que faz |
| --- | --- |
| `configuracao.py` | lê a configuração pelo molde, com os arquivos a partir da pasta dela e os modelos já lidos, e confere o que o molde não vê: o campo montado por um modelo que ela não tem e o arquivo de lista e de tabela |
| `forma_do_arquivo.py` | lê um arquivo JSON ou CSV com a forma dele, refaz o texto dos dados nessa forma, diz a primeira linha em que o arquivo não volta igual e grava os textos, sem gravar nenhum quando um deles não se escreve em UTF-8 |
| `campos_montados.py` | lê os modelos, diz o que vai entre dois itens e monta, em qualquer nível de uma entrada, cada campo que tem um modelo, com o caminho de cada problema |

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../LICENSE-CONTENT.txt).*
