# historico-de-arquivo

Tira das transcrições das sessões de um programa de IA cada leitura e cada gravação de um
arquivo, na ordem do tempo. Serve para recuperar o texto que um arquivo teve um dia e que
não está mais em lugar nenhum: o que uma edição tirou dele, o que uma leitura mostrou.

A transcrição de uma sessão é o arquivo JSONL que o programa grava com cada evento da
conversa, um por linha. Uma ferramenta que lê ou grava arquivos aparece nela como um uso,
com o nome da ferramenta e a entrada, onde está o caminho do arquivo, e, num evento
seguinte, como o resultado desse uso, ligado a ele pelo id.

O script acha o arquivo pelo caminho inteiro, como a sessão o escreveu, ou só pelo nome,
em qualquer pasta. A busca é pelo arquivo, nunca por palavra do texto: acha todo uso que
leu ou gravou nele, sempre os mesmos.

| Arquivo | O que faz |
| --- | --- |
| `historico_de_arquivo.py` | acha os usos no arquivo pedido e grava o que achou |
| `transcricoes.py` | lê as transcrições de uma pasta e das subpastas dela, um evento JSON por linha, e entrega os blocos da mensagem de cada evento, para qualquer script que filtre transcrições |
| `esquemas/historico-de-arquivo.schema.json` | o molde da configuração |

Usa só a biblioteca padrão do Python e o `extrator_comum.py`, do
[extrator](../extrator/README.md), que lê a configuração pelo molde dela e confere que as
codificações dela existem; na prateleira, ele é achado na pasta irmã `extrator/`.

## Como rodar

    python3 -I <prateleira>/historico-de-arquivo/historico_de_arquivo.py --config <configuração.json> --transcricoes <pasta> --arquivo <caminho> --saida <pasta nova>

- `--transcricoes`: a pasta das transcrições; entram todos os arquivos dela e das
  subpastas cujo nome segue o padrão da configuração, como os das sessões de agentes.
- `--arquivo`: o caminho do arquivo, como as sessões o escreveram; com `--pelo-nome`, só o
  nome dele.
- `--saida`: uma pasta nova. Ela só é criada depois que tudo foi lido e montado: com erro,
  não fica pasta nenhuma.

## O que grava

Na pasta de saída, com os nomes, os rótulos, as marcas e a codificação da configuração:

- um arquivo por achado, numerado na ordem do tempo, com a extensão da configuração e
  zeros na frente quando o número de achados tem mais algarismos: a sessão, a hora, a
  ferramenta, o caminho, a transcrição, a partir da pasta dada, e a linha dela, cada um
  depois do rótulo e do separador; depois, cada campo da entrada que a configuração diz
  para a ferramenta, sob o nome dele entre as marcas da seção, com o que não é texto
  escrito em JSON; e, quando a configuração pede, o resultado, sob o rótulo dele: o texto,
  os textos dos blocos de uma lista, um por linha, ou a marca de sem resultado, quando ele
  não veio;
- a lista dos achados: uma linha por achado, na ordem do tempo, com o número, o arquivo e
  os mesmos dados, separados por tabulação;
- a lista das linhas que não se leram: a transcrição e a linha de cada uma, fora da
  codificação ou que não é um objeto JSON. A linha em branco não conta.

Na tela, quantos achados e quantas linhas que não se leram. Dão erro: a pasta das
transcrições que não existe, a pasta de saída que já existe, a configuração com campo que
o molde não conhece ou sem um campo que o script lê, a codificação que não existe, dois
arquivos da saída com o mesmo nome e duas ferramentas com o mesmo nome, com o erro dizendo
o nome.

## A configuração

O molde está em `esquemas/historico-de-arquivo.schema.json`. A configuração é do projeto:
os nomes dos campos são os das transcrições do programa que as grava.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `transcricoes` | o `padrao` do nome dos arquivos das transcrições e a `codificacao` delas |
| `eventos` | os nomes dos campos: `hora` e `sessao`, do evento; `mensagem`, do evento, e `conteudo`, dela, com a lista dos blocos; `tipo`, de cada bloco; `texto`, do bloco de texto de um resultado em lista |
| `uso` | o bloco do uso de uma ferramenta: o `tipo` dele e os nomes dos campos `id`, `nome` (o da ferramenta), `entrada` e `caminho` (o do arquivo, dentro da entrada) |
| `resultado` | o bloco do resultado: o `tipo` dele e os nomes dos campos `id` (o do uso) e `conteudo` |
| `ferramentas` | cada ferramenta que lê ou grava arquivos: o `nome`, os `campos` da entrada que vão para o achado e se o `resultado` vai também |
| `saida` | a `codificacao` dos arquivos gravados; a `extensao` dos arquivos dos achados; o nome da `lista` dos achados e o da das linhas que não se leram (`ilegiveis`); os `rotulos` de cada dado, das colunas `numero` e `arquivo` e do `resultado`; o `separador` entre o rótulo e o dado; as marcas `antes` e `depois` do título de cada `secao`; e a marca de `sem_resultado` |

## Testes

Em [testes/](testes/README.md).
