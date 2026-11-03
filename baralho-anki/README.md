# baralho-anki

Serve para estudar no Anki uma tabela Markdown de palavras-chave feita a partir de textos: cada
linha da tabela é um assunto e nomeia, numa coluna, o arquivo do texto de onde saiu (a fonte),
e cada célula das colunas escolhidas vira um cartão. Na frente do cartão vai uma pergunta; no
verso, a resposta e o trecho da fonte que a sustenta. A pergunta, a resposta e o trecho se
escrevem à mão, num CSV, lendo inteira a fonte de cada linha; a peça monta o CSV a partir da
tabela, confere o que se escreveu contra a tabela e contra as fontes, grava o pacote do Anki
(`.apkg`) e guarda o registro da conferência de conteúdo. O mesmo CSV dá sempre o mesmo pacote,
e reimportar o pacote no Anki atualiza as notas em vez de duplicá-las.

A peça serve quando:

- as palavras-chave estão numa tabela Markdown, uma linha por assunto;
- cada linha nomeia, numa coluna, o arquivo de texto de onde saiu, que fica numa das pastas
  dadas no comando;
- cada cartão tem um trecho da fonte, copiado letra por letra, que sustenta a resposta e que a
  peça confere.

Não serve para escrever a pergunta e a resposta, que se escrevem à mão, nem para cartões sem
fonte ou de outro tipo do Anki, como o de lacunas: cada nota tem um cartão só, com a frente e o
verso que os modelos dão.

Um exemplo. Da tabela

    | Assunto | Onde | Quando | Fonte |
    | --- | --- | --- | --- |
    | Revolução Francesa | França | 1789 | revolucao-francesa.md |

com `Assunto` como a coluna do assunto, `Fonte` como a da fonte e `Onde` e `Quando` como as
colunas de cartão, saem dois cartões, `revolucao-francesa-onde` e `revolucao-francesa-quando`.
No segundo, as palavras-chave são `1789`, e a pergunta, a resposta e o trecho se escrevem lendo
o `revolucao-francesa.md`: "Em que ano começou a Revolução Francesa?", "Em **1789**." e a frase
do texto que dá o ano.

Usa só a biblioteca padrão do Python, o `extrator_comum.py` e o `texto_comum.py`, do
[extrator](../extrator/README.md), o `markdown_comum.py`, do
[documentos](../documentos/README.md#o-módulo-de-markdown), e o `proibidos_comum.py`, do
[confere-forma](../confere-forma/README.md#o-módulo-dos-padrões-proibidos). Na prateleira, eles
são achados nas pastas irmãs; numa cópia fora da prateleira, na mesma pasta dos scripts.

## O caminho

1. O CSV a partir da tabela, com a pergunta, a resposta e o trecho vazios (`gera_csv.py`).
2. A pergunta, a resposta e o trecho de cada linha se escrevem lendo inteira a fonte dela.
3. A conferência do CSV (`confere_baralho.py`).
4. O pacote (`gera_apkg.py`).
5. O registro da conferência de conteúdo (`conferido.py --gravar`). Depois, sem o `--gravar`,
   ele diz que fonte mudou desde o registro; só as linhas dela se conferem de novo, e o
   registro se grava outra vez.

## Como rodar

    python3 -I gera_csv.py <configuração.json> <tabela.md> <baralho.csv>
    python3 -I confere_baralho.py <configuração.json> <tabela.md> <baralho.csv> --pasta <pasta>... [--proibidos <arquivo.json>]...
    python3 -I gera_apkg.py <configuração.json> <baralho.csv> <baralho.apkg> --frente <arquivo> --verso <arquivo> --estilo <arquivo>
    python3 -I conferido.py <configuração.json> <tabela.md> <conferido.json> --pasta <pasta>... [--gravar]

- `--pasta`: uma pasta das fontes; pode se repetir, e vale a primeira que tem a fonte.
- `--proibidos`: um arquivo de [padrões proibidos](../confere-forma/README.md#os-padrões-proibidos),
  como o `marcas-de-ia.json` do confere-forma; pode se repetir, e as regras de todos se somam.
- `--frente`, `--verso` e `--estilo`: os modelos da frente e do verso do cartão, no formato de
  modelo do Anki (`{{Campo}}`, `{{FrontSide}}`), e o estilo (CSS), cada um com o texto do
  arquivo como está.

Os quatro saem com 0 sem problema e com 2, sem gravar nada, quando a configuração, a tabela, o
CSV, uma fonte, um modelo, um arquivo de padrões proibidos, o registro ou um argumento não
servem, com uma linha `ERRO: motivo`. A conferência do CSV e a do registro saem com 1 quando
acham problema, com uma linha `ERRO arquivo:linha: motivo` (no registro, `ERRO arquivo:
motivo`) para cada um, e um resumo.

## A tabela e o CSV

A tabela é a primeira tabela Markdown do arquivo, fora dos blocos de código: a primeira linha
que começa por `|` e as seguidas a ela que também começam por `|`. A primeira é o cabeçalho, a
segunda é o separador, e as outras são as linhas, cada uma com as células do cabeçalho; o que
vem depois, também outra tabela, fica de fora. A configuração diz a coluna do assunto de cada
linha, a da fonte (o nome do arquivo do texto de onde a linha saiu) e as colunas que viram
cartão; as outras ficam de fora.

O CSV é UTF-8, separado por vírgula, com as aspas do padrão do módulo `csv` do Python, uma
linha de cabeçalho e cada linha terminada em `\n`. As colunas são a forma do cartão que a peça
trata e ficam no código; o que é de cada projeto (as colunas da tabela, o baralho, o tipo de
nota e os campos dele) vem da configuração. As colunas, nessa ordem:

| Coluna | O que é | De onde vem |
| --- | --- | --- |
| `id` | o nome do arquivo da fonte sem a extensão, um hífen e o identificador da coluna (as letras e os números, em minúsculas e sem acento, ligados por hífen: `Onde / Status` dá `onde-status`) | a tabela |
| `assunto` | a célula do assunto | a tabela |
| `coluna` | o nome da coluna de cartão | a tabela |
| `pergunta` | a pergunta do cartão | a fonte, lida inteira |
| `resposta` | a resposta à pergunta, escrita pelo que a fonte diz; não se confere letra por letra | a fonte, lida inteira |
| `palavras_chave` | a célula da coluna, com as palavras-chave separadas pelo `separador` | a tabela |
| `trecho` | o trecho da fonte que sustenta a resposta, copiado letra por letra | a fonte, lida inteira |
| `fonte` | a célula da fonte | a tabela |

Que coluna vai em cada campo da nota, e que campo aparece na frente e no verso, dizem a
[configuração](#a-configuração) e os modelos do cartão: as palavras-chave, por exemplo, podem ir
num campo, uma por linha, ou ficar só no CSV.

O `gera_csv.py` grava uma linha por linha da tabela e por coluna de cartão, na ordem da tabela
e, dentro dela, na das colunas de cartão. Quando o CSV já existe, a pergunta, a resposta e o
trecho de cada id que continua na tabela ficam como estavam; o resto vem da tabela de agora, e
a linha que a tabela não dá mais sai.

## O que se confere

O `confere_baralho.py` dá um `ERRO` na linha do CSV, para cada problema:

| Problema | Onde sai o ERRO |
| --- | --- |
| campo vazio ou só com espaços, também a pergunta, a resposta e o trecho | na linha |
| o `id`, o `assunto`, a `coluna`, as `palavras_chave` ou a `fonte` diferentes do que a tabela dá para o id; o id que a tabela não dá | na linha |
| o trecho que não está na fonte, achada nas pastas, em ordem: os dois se comparam na forma Unicode NFC, com os espaços juntados e sem as marcas de ênfase da configuração | na linha |
| a fonte que nenhuma pasta tem | na linha |
| o campo que casa com o `padrao` de uma regra dos arquivos de padrões proibidos, e não com o `exceto` dela | na linha, com o nome da regra |
| o id repetido | na segunda linha |
| o cartão que falta | na última linha |
| a linha fora da ordem da tabela, quando os ids são os da tabela | na primeira linha fora do lugar |

## O pacote

O `pacote_anki.py` grava o esquema antigo da coleção do Anki, o 11, que o Anki ainda importa:
um zip com o banco (`collection.anki2`) e a lista das mídias, vazia. Além do baralho e do tipo
de nota da configuração, o banco traz o baralho e as opções padrão que toda coleção tem. Cada
linha do CSV vira uma nota, com um cartão novo, na ordem do CSV:

- os campos são os do tipo de nota da configuração, cada um com o texto da coluna dele, o HTML
  escapado e cada trecho entre duas marcas de ênfase dentro da etiqueta HTML dela (as marcas
  mais longas primeiro; a marca sem par é erro); no campo de palavras-chave, cada palavra-chave
  numa linha, com a `quebra` entre elas;
- as etiquetas da nota são o nome do arquivo da fonte, sem a extensão, e o identificador da
  coluna;
- o id do baralho e o do tipo de nota saem do hash do nome de cada um; o guid da nota, do hash
  do `id` do CSV; os ids das notas e dos cartões e todas as datas do banco e das entradas do
  zip, da `data` da configuração.

A `data` é a data de mudança de cada nota no pacote: a cada versão nova do CSV, ela muda. Essa
é a forma que fica no código; o resto vem da configuração e dos modelos.

## A configuração

O molde está em `esquemas/baralho-anki.schema.json`:

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `tabela` | a coluna do assunto (`assunto`) e a da fonte (`fonte`), as colunas que viram cartão, na ordem (`cartoes`), e o separador das palavras-chave de uma célula (`separador`) |
| `enfases` | as marcas de ênfase do Markdown, cada uma com a etiqueta HTML que ela vira no pacote; a conferência compara os trechos sem elas |
| `baralho` | o nome do baralho; `::` separa o baralho de dentro do de fora |
| `nota` | o tipo de nota: o nome, o do modelo de cartão (`cartao`), os campos (cada um com o `nome` e a `coluna` do CSV; o que tem `palavras_chave` leva uma palavra-chave por linha), a `quebra` entre as palavras-chave e a letra dos campos no editor do Anki (`editor`, com `tipo_de_letra` e `tamanho`) |
| `data` | a data da versão do baralho, com o fuso |

É `ERRO`, com código 2, que diz o arquivo: campo que o molde não conhece, campo que falta ou de
outro tipo, campo de nota com uma coluna que o CSV não tem, dois campos com o mesmo nome, duas
colunas de cartão com o mesmo identificador e duas ênfases com a mesma marca.

## O registro da conferência

O `conferido.py` guarda o sha256 do arquivo da tabela e o de cada fonte que ela nomeia, achada
nas pastas, com as fontes na ordem da tabela. O molde está em `esquemas/conferido.schema.json`:

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `tabela` | o sha256 do arquivo da tabela |
| `fontes` | o sha256 de cada fonte, pelo nome dela na tabela |

Sem o `--gravar`, ele dá um `ERRO` para a tabela que mudou, para a fonte que mudou, que o
registro não tem ou que nenhuma pasta tem, e para a fonte do registro que a tabela não nomeia
mais. Com o `--gravar`, grava o registro de agora, com a versão do molde; a fonte que nenhuma
pasta tem é `ERRO`, com código 2, e nada se grava.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../LICENSE-CONTENT.txt).*
