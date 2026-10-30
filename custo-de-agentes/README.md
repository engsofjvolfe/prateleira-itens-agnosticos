# custo-de-agentes

Mostra o uso de tokens de cada transcrição de sessão:
quantos turnos trazem o uso, o maior contexto de um turno, o total processado, o total de
saída e o começo da primeira pergunta. Serve para ver quanto custou cada agente de um
trabalho e qual deles encheu o contexto.

Usa só a biblioteca padrão do Python, o `transcricoes.py`, do
[historico-de-arquivo](../historico-de-arquivo/README.md), que lê as transcrições (um evento
JSON por linha, pulando a linha que não é um objeto JSON), e o `extrator_comum.py`, do
[extrator](../extrator/README.md), que lê a configuração pelo molde dela. Na prateleira,
eles são achados nas pastas irmãs; numa cópia fora da prateleira, na mesma pasta do script.

## Como rodar

    python3 -I custo.py <configuração.json> <pasta das transcrições>

A configuração é do projeto: ela dá o padrão do nome dos arquivos das transcrições e os
nomes dos campos delas, que são os do programa que as grava.

## O que sai

Uma tabela na tela, separada por tabulação: o cabeçalho, com os rótulos da configuração, e
uma linha por transcrição que tem alguma linha, na ordem do caminho. Sai com código 0, ou
com 2 quando a configuração ou a pasta não serve.

| Coluna | O que é |
| --- | --- |
| transcrição | o caminho, a partir da pasta (as transcrições das subpastas entram) |
| turnos | quantos eventos trazem, na mensagem, o uso como objeto |
| contexto máximo | o maior contexto de um turno: a soma dos campos de entrada do uso |
| processado | a soma, em todos os turnos, do contexto mais a saída |
| saída | a soma da saída de todos os turnos |
| começo | o começo do texto da primeira pergunta (evento do tipo dado, com o conteúdo em texto), com cada trecho de espaços virando um espaço; vazio quando não há pergunta |

Campo do uso que falta, ou que não é número inteiro (um booleano também não é), vale 0.

## A configuração

O molde está em `esquemas/custo-de-agentes.schema.json`:

| Campo | O que é |
| --- | --- |
| `versao_schema` | 1 |
| `transcricoes` | o `padrao` dos arquivos (como `agent-*.jsonl`) e a `codificacao` |
| `eventos` | os nomes dos campos do evento: o `tipo`, o valor do tipo que é uma `pergunta`, a `mensagem`, o `conteudo` dela e o `uso` dela |
| `uso` | os nomes dos campos de `entrada` do uso, que somados dão o contexto, e o da `saida` |
| `comeco` | quantas `letras` do começo da pergunta aparecem |
| `colunas` | o rótulo de cada coluna da tabela |

É `ERRO`, com código 2: campo que o molde não conhece, campo que falta ou de outro tipo,
lista de entrada vazia ou com nome que não é texto, número de letras negativo e codificação
que não existe.

## Testes

Em [testes/](testes/README.md).
