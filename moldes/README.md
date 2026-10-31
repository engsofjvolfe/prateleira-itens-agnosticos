# moldes

Lê análises de aulas escritas linha a linha, numa forma dada num arquivo de dados, e diz
em que documento de um material de estudo cada trecho delas cai, por regras dadas em outro
arquivo. Um trecho é uma linha da análise: um fato tirado de um pedaço de slide, com os
campos que dizem o tipo dele, o grupo, o caminho e para onde ele vai. Serve para:

- contar quantos trechos cada documento recebe, e de que tipo, grupo, marca e aula;
- listar os trechos de um documento, para a leitura deles;
- dar a outros programas a leitura das análises e o lugar de cada trecho, sem repetir essa
  lógica;
- dar a cada trecho o que o destino dele nomeia, por uma tabela que junta os jeitos de
  escrever o mesmo nome;
- aplicar um limite por aula a um material que cobre só as aulas até uma última: de que
  cada aula trata, o que ela só menciona e que lugares ficam.

Usa só a biblioteca padrão do Python e dois módulos do [extrator](../extrator/README.md): o
`extrator_comum.py`, pelo qual os scripts leem a forma e as regras pelos moldes delas e as
peças comuns leem as análises e acham os valores repetidos de uma lista, e o
`texto_comum.py`, que passa os
textos para a forma NFC. Eles são achados na pasta irmã `extrator/` ou na mesma pasta.

## Como rodar

    python3 -I <prateleira>/moldes/contar.py <pasta das análises> <forma.json> <regras.json> <saída.md>
    python3 -I <prateleira>/moldes/separar.py <pasta das análises> <forma.json> <regras.json> <saída.md> --documento <id>
    python3 -I <prateleira>/moldes/separar.py <pasta das análises> <forma.json> <regras.json> <saída.md> --assunto

**contar.py** grava a contagem: a tabela das classes (abaixo), com o total; para cada
documento, quantos trechos ele recebe e quantos de cada tipo, grupo, marca (quando há
trecho marcado nele) e aula; no fim, os problemas. Sai com código 1 quando há problema; a
contagem é gravada assim mesmo.

**separar.py** grava a lista dos trechos que caem num documento de conteúdo, ou dos que
esperam o assunto, aula por aula. Cada trecho ocupa duas linhas: a primeira com o id, os
tipos, os grupos (depois de `g`), os caminhos, as marcas (depois de `m`) e o destino
(depois de `→`); a segunda com o texto.

Na leitura pelos moldes, o campo que o molde não conhece, o que falta e o valor de outro
tipo ou fora da forma são erro, que diz o caminho do valor. Cada erro que o script acha na
entrada dá uma linha `ERRO`, que diz o que está errado; ele sai com código 1 e nada é
gravado.

## A forma das análises

O molde está em `esquemas/forma-analise.schema.json`.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `arquivos` | o padrão dos nomes dos arquivos de análise (ex.: `aula-*.md`) |
| `prefixo_arquivo` | o que vem antes da chave da aula no nome do arquivo |
| `prefixo_titulo` | o começo de uma linha de título; o título fecha o slide, e o que vem depois dele não se lê até o próximo slide |
| `prefixo_slide` | o começo de uma linha que abre um slide; o resto da linha é o número dele |
| `marca_item` | o começo de cada item |
| `separador_texto` | o que separa o texto do trecho do primeiro campo |
| `separador_campos` | o que separa um campo do seguinte |
| `vazio` | o valor que quer dizer "nenhum" num campo em lista |
| `nota_sem_campos` | o começo de um item sem campos, que é uma nota e não um trecho |
| `campos` | os campos, em ordem, cada um com o `nome`, a `forma` e, se tiver, o `papel` e a `fonte` (a chave da fonte cujas páginas o campo cita) |

Uma linha de trecho fica assim:
`<marca_item><texto><separador_texto><campo 1>: <valor><separador_campos><campo 2>: <valor>…`

Formas de campo: `lista` (os itens entre os `separadores`; o que está entre parênteses não
conta), `pedacos` (os pedaços entre os `separadores` que ficam fora dos parênteses, cada um
inteiro, com o que está entre parênteses), `presenca` (quais dos `valores` aparecem no
campo) e `texto` (o campo inteiro). Nas formas em lista, o valor `vazio` fica fora e nada
se repete. Em `pedacos`, o parêntese que não fecha, ou que fecha sem abrir, é erro, que diz
o arquivo, a linha e o campo.

Papéis: `tipo`, `grupo` e `caminho` dizem onde o trecho cai e pedem uma forma em lista;
`destino` é o texto que diz para onde ele vai. Cada papel está em um campo, e só em um.

Cada trecho tem um id: `aula/slide/posição/hash`. A posição conta os trechos do slide, a
partir de 1; o hash são os quatro primeiros dígitos do SHA-1 do texto do trecho em NFC.
Quando o texto muda, o id muda, e a mudança aparece em toda decisão guardada pelo id. Um id,
ou o começo dele (a aula; a aula e o slide; a aula, o slide e a posição), se lê pelo
`le_codigo` do `analises.py`, que lê as partes como o `id_do_trecho` as escreve e não lê o
que não é id nem começo de um.

## As regras

O molde está em `esquemas/regras.schema.json`. As regras podem estar dentro de um arquivo
maior, como o formato de um material: o molde fecha só o que elas usam.

| Chave | O que é |
| --- | --- |
| `fora` | cada regra (`id`, `nome`, `tipos`) tira do material o trecho cujos tipos são todos dela |
| `marcas` | cada marca (`id`, `nome`, `texto`, `papeis`) acompanha o trecho que tem o `texto` no campo de um dos `papeis`; o trecho fica no material, com a marca |
| `grupos` | cada grupo (`id`, `nome`); `pelo_assunto: true` quando o documento do trecho do grupo vem do assunto dele, decidido numa leitura |
| `documentos` | cada documento (`id`, `nome`) recebe os trechos de um dos `grupos` dele, ou de um dos `caminhos`, ou todos (`todos: true`); os que não recebem todos são os documentos de conteúdo |

As regras se conferem contra a forma: todo papel de cada marca está na forma; todo caminho
de um documento é um dos valores do campo do caminho, quando o campo diz os valores.

## As classes dos trechos

Cada trecho fica numa classe só:

- **de estudo, com lugar nos documentos**: cai num documento de conteúdo;
- **de estudo, à espera do assunto**: só tem grupo cujo documento vem do assunto;
- **fora**, por uma regra de fora;
- **marcado, à espera de lugar**: tem marca e não cai em documento de conteúdo; conta na
  primeira marca dele, na ordem das regras;
- **com problema**: tipo de fora junto de outro tipo; sem grupo e sem marca; ou sem
  documento de conteúdo.

O trecho de fora, ou com problema por causa dos tipos ou da falta de grupo e de marca, não
cai em documento nenhum; os outros caem também nos documentos que recebem todos. Um grupo
que as regras não têm é problema também.

A aplicação da tabela dos destinos e do limite dá mais três classes, que a tabela das
classes mostra quando há trecho nelas: **de estudo, à espera de unidade** (o trecho que
espera a coisa que ganha material, dentro do documento dele); **até a última aula, sem
lugar depois do limite**; e **depois da última aula, sem lugar**.

## A tabela dos destinos

Um texto em colunas separadas por tabulação, com o cabeçalho `destino`, `unidade` e uma
linha por id nomeado. O `destino` é um pedaço do campo do papel `destino`, como as análises
o escrevem; a `unidade` é o id que ele nomeia (uma coisa que ganha material, um item dela
ou um conjunto delas, como o projeto as chama). O pedaço que nomeia mais de um id
tem uma linha para cada; o que não nomeia nenhum tem uma linha com a unidade vazia, que
pode vir sem a tabulação do fim. Os textos se comparam em NFC.

Cada trecho recebe os ids dos pedaços do destino dele, na ordem dos pedaços e sem repetir;
os pedaços que a tabela não tem saem numa lista, cada um uma vez, com os trechos dele. A
linha repetida, a linha sem destino e o pedaço com a unidade vazia numa linha e uma unidade
noutra são erro, que diz a linha. O destino precisa estar numa forma que dê lista, como
`pedacos`. O programa que usa a tabela dá os ids que tem, e cada id da tabela que não está
entre eles sai com o pedaço dele.

## O limite

Para um material que cobre só as aulas até uma última. Uma entrada é o que recebe trechos
dentro de um documento: uma unidade sem itens, um item, ou a unidade com itens, que é a
entrada da abertura dela. Cada lugar é um trecho de uma aula numa entrada, numa parte do
molde dela, direto (o destino nomeia a entrada) ou não (nomeia um conjunto de que ela é
membro).

- Uma aula trata de uma unidade sem itens, ou de um item, quando os lugares diretos dos
  trechos dela ali têm pelo menos o número dado de partes distintas; a decisão de quem
  trata, quando há, vale no lugar dessa conta. Da unidade com itens tratam as aulas que
  tratam de algum item dela. As outras aulas com lugar ali só a mencionam.
- A entrada tratada é a de que trata alguma aula até a última; a unidade tratada, com
  itens ou sem, tem material.
- Fica o lugar de uma aula até a última numa entrada cuja unidade tem material (o item só
  mencionado fica, na unidade dele), e o de uma aula depois da última numa entrada tratada.
  O resto sai.
- O trecho que perdeu todos os lugares sai numa lista: uma para os das aulas até a última,
  outra para os de depois.
- O trecho de depois da última aula que fica vai para as perguntas das aulas até a última
  que tratam das entradas em que ele ficou.

É erro, e cada problema sai na mensagem: o número de partes que não é um inteiro de 1 para
cima; a aula repetida, ou a última aula que não está entre as aulas; o trecho com lugares
de mais de uma aula, ou de uma aula que não está entre elas; o id que é item e unidade com
itens; e a decisão para uma unidade com itens, para uma entrada sem lugar, ou com uma aula
que não está entre as aulas, que vem depois da última ou que não tem trecho na entrada.

## Peças comuns

Não rodam sozinhas: os scripts desta pasta, e os de um projeto que as copie (com o
`extrator_comum.py` e o `texto_comum.py` ao lado), as importam.

- `analises.py` — lê as análises da pasta pela forma, já conferida pelo molde dela, depois
  de conferir o que o molde não vê (o nome de campo repetido e o papel em mais de um campo,
  em nenhum ou num campo que não dá lista); monta o id de um trecho e lê um id, ou o começo
  dele, em partes; e dá a chave que põe textos em ordem comparando pelo valor os números de
  dentro deles, com o próprio texto para desempatar.
- `lugares.py` — a classe, as marcas e os documentos de cada trecho, pelas regras; confere
  as regras contra a forma.
- `relatorio.py` — a tabela em markdown, as ordenações e a tabela das classes.
- `entrada.py` — o que os scripts fazem do mesmo jeito: as quatro entradas do comando, a
  leitura da forma e das regras pelos moldes delas, o aviso de erro e a gravação da saída.
- `tabela.py` — as linhas de um texto em colunas separadas por tabulação, com o cabeçalho
  dado: sem as linhas em branco e sem os espaços das pontas; a linha com menos colunas tem
  vazias as que faltam no fim, porque o editor que tira os espaços do fim da linha tira
  também as tabulações das colunas vazias do fim; cabeçalho diferente ou linha com mais
  colunas é erro que diz a linha. Recebe o texto: a leitura do arquivo fica com o programa
  que o importa.
- `destinos.py` — lê a tabela dos destinos (do texto dela) e dá os ids de cada trecho, os
  pedaços sem linha e os ids que o programa que usa a tabela não tem.
- `limite.py` — aplica o limite aos lugares que recebe.

## Testes

Em [testes/](testes/README.md).
