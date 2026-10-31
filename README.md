# prateleira

Prateleira de peças: scripts e arquivos de dados que servem a qualquer projeto. Cada peça é
uma pasta com um README (o que faz, o que recebe, o que entrega e como rodar) e, quando tem
código, uma pasta `testes/` com o teste dela e as cópias estragadas que provam que o teste
pega os defeitos. Nos comandos dos READMEs, `<prateleira>` é a pasta onde a prateleira está.

- A organização (as regras, a forma de uma peça, a estrutura, como um projeto usa uma peça
  e como testar): [organizacao/](organizacao/README.md).
- Cada peça conferida contra as regras: [RELATORIO-AGNOSTICO.md](RELATORIO-AGNOSTICO.md).
- O que falta fazer: [TODO.md](TODO.md); o que mudou em cada versão:
  [CHANGELOG.md](CHANGELOG.md).

## As peças

| Peça | O que faz |
| --- | --- |
| [confere-citacoes/](confere-citacoes/README.md) | conferir que cada trecho citado num texto Markdown está, letra por letra, na transcrição da fonte e nas páginas citadas, com os pedaços na ordem da fonte e cada supressão no lugar de alguma coisa (com testes) |
| [confere-forma/](confere-forma/README.md) | conferir a forma de documentos Markdown contra uma descrição dela: abertura, seções, divisores, fecho, padrões proibidos, nomes em itálico e tamanho (com testes) |
| [copia-para-projeto/](copia-para-projeto/README.md) | levar os arquivos de uma peça para um projeto, com o cabeçalho dos scripts dele, e conferir que as cópias estão em dia (com testes) |
| [copias-estragadas/](copias-estragadas/README.md) | provar que o teste de uma peça pega os defeitos dela, rodando-o contra cópias estragadas (com testes) |
| [custo-de-agentes/](custo-de-agentes/README.md) | mostrar o uso de tokens de cada transcrição de sessão, como as dos agentes de um programa de IA (com testes) |
| [dicionario-das-duvidas/](dicionario-das-duvidas/README.md) | conferir os códigos dos títulos de um dicionário das dúvidas, com a forma dos códigos na configuração (com testes) |
| [divergencias/](divergencias/README.md) | conferir a lista dos fatos que as fontes dizem de formas diferentes, com a forma que o material ensina e as outras, e gravar o documento deles, ou conferir que o gravado está em dia (com testes) |
| [documentos/](documentos/README.md) | conferir os links internos dos documentos de um repositório git e as linhas que passam de um limite de caracteres; e o módulo comum que lê um texto Markdown como o GitHub o lê (com testes) |
| [extrator/](extrator/README.md) | tirar por programa o texto de documentos (PDF, HTML, XML, JSON) e gravar a transcrição de cada um, página por página; o módulo comum que lê dados JSON pelo molde; e o módulo de texto comum, que passa um texto para a forma NFC e junta os espaços (com testes) |
| [ganchos/](ganchos/README.md) | ganchos para o programa em que a IA trabalha: as regras de código no começo e no fim de cada tarefa que escreve código ou dados; a barreira à busca por palavra; o arquivo que só cresce para onde a limpeza leva o que tira; a cancela e o registro das chamadas de ferramenta; a leitura do comando de terminal que dois deles usam; e a leitura do protocolo de cada programa, que todos usam (com testes) |
| [grava-ou-confere/](grava-ou-confere/README.md) | gravar um documento que um script gera a partir de dados, ou conferir que o gravado está em dia (com testes) |
| [historico-de-arquivo/](historico-de-arquivo/README.md) | tirar das transcrições das sessões cada leitura e cada gravação de um arquivo, na ordem do tempo; e ler as transcrições, um evento por linha, para qualquer peça que as filtre (com testes) |
| [itens-numerados/](itens-numerados/README.md) | listar os itens numerados de uma transcrição, conferir a numeração e dividir o sumário em grupos de tópicos (com testes) |
| [marcas/](marcas/README.md) | ler os códigos escondidos em comentários de um texto Markdown e conferir se cada um está no lugar em que deveria estar (com testes) |
| [moldes/](moldes/README.md) | dizer em que documento cada trecho das análises cai, contar e listar os trechos de cada documento, dar a cada trecho o que o destino dele nomeia e aplicar um limite por aula (com testes) |
| [texto-em-comum/](texto-em-comum/README.md) | dizer quais arquivos de uma pasta têm texto igual ao de arquivos de outras pastas (com testes) |

Os arquivos soltos:

| Arquivo | O que é |
| --- | --- |
| `README.md` | este arquivo |
| `CHANGELOG.md` | o que mudou em cada versão |
| `TODO.md` | o que falta fazer |
| `RELATORIO-AGNOSTICO.md` | cada peça conferida contra as regras da prateleira |
| `.gitignore` | o que a prateleira não guarda: o cache do Python e as anotações de sessão dos ganchos |

## Como as peças se ligam

Só por arquivos e pelos módulos comuns documentados, que a peça acha na pasta irmã (na
prateleira) ou na própria pasta (numa cópia fora da prateleira).

| Módulo comum | Da peça | Peças que o usam |
| --- | --- | --- |
| `extrator_comum.py`: ler um texto em UTF-8, ler JSON pelo molde, pegar um campo com o tipo pedido, achar os valores repetidos de uma lista, compilar uma expressão, conferir que uma codificação existe, dividir uma transcrição em páginas | [extrator](extrator/README.md#o-módulo-comum) | confere-citacoes, confere-forma, copia-para-projeto, copias-estragadas, custo-de-agentes, dicionario-das-duvidas, divergencias, documentos, historico-de-arquivo, itens-numerados, marcas, moldes, ganchos/busca-por-palavra, ganchos/chamadas-permitidas, ganchos/destino-da-limpeza, ganchos/leitura-do-terminal, ganchos/protocolo, ganchos/regras-de-codigo |
| `texto_comum.py`: passar um texto para a forma Unicode NFC e juntar os espaços | [extrator](extrator/README.md#o-módulo-de-texto) | confere-citacoes, custo-de-agentes, divergencias, extrator, itens-numerados, marcas, moldes, texto-em-comum |
| `markdown_comum.py`: ler um texto Markdown como o GitHub o lê: as linhas fora dos blocos de código, o texto sem o código, a âncora de um título, os títulos com a linha, o nível e a âncora de cada um, e os marcadores | [documentos](documentos/README.md#o-módulo-de-markdown) | dicionario-das-duvidas, documentos |
| `transcricoes.py`: ler as transcrições de sessão, um evento por linha | [historico-de-arquivo](historico-de-arquivo/README.md) | historico-de-arquivo, custo-de-agentes |
| `grava_ou_confere.py`: gravar um documento gerado ou conferir que está em dia | [grava-ou-confere](grava-ou-confere/README.md) | copia-para-projeto, divergencias |
| `leitura_do_terminal.py`: ler um comando de terminal como o shell lê, com os prefixos do shell da configuração dela | [ganchos/leitura-do-terminal](ganchos/leitura-do-terminal/README.md) | ganchos/regras-de-codigo, ganchos/busca-por-palavra |
| `protocolo.py`: ler o protocolo dos ganchos de um programa, ler o evento, montar a resposta e dar o arquivo da anotação de cada sessão | [ganchos/protocolo](ganchos/protocolo/README.md) | ganchos/busca-por-palavra, ganchos/chamadas-permitidas, ganchos/destino-da-limpeza, ganchos/regras-de-codigo |

E os encadeamentos, em que uma peça grava o arquivo que a próxima lê:

- Documentos + configuração do extrator → `extrator/extrator.py` → transcrições, página por
  página → `confere-citacoes` (como fontes) e `itens-numerados/itens.py`.
- Textos Markdown → `confere-forma` (a forma) e `confere-citacoes` (as citações).
- A lista das divergências + o cabeçalho → `divergencias/divergencias.py` → o documento das
  divergências → `confere-citacoes` (a citação da fonte de cada forma).
- Um dicionário das dúvidas + a forma dos códigos → `dicionario-das-duvidas/confere_dicionario.py`
  → os títulos fora da regra.
- Análises + a forma delas + as regras de lugar → `moldes/contar.py` e `moldes/separar.py`.
- Transcrições de sessão → `historico-de-arquivo` (o histórico de um arquivo) e
  `custo-de-agentes` (o custo de cada uma).
- Uma peça, o teste dela e a lista de estragos → `copias-estragadas/estraga.py` → quantos
  estragos o teste pega.
- Os dados de um projeto → a peça, rodada direto da prateleira (ver
  [organizacao/](organizacao/README.md#como-um-projeto-usa-uma-peça)).
- Uma peça e um projeto que precisa funcionar sem a prateleira →
  `copia-para-projeto/copia.py` → as cópias no projeto, ou a conferência delas.
- Uma pasta e as pastas com que ela se compara → `texto-em-comum/texto_em_comum.py`.

## As versões

As versões seguem o [Versionamento Semântico](https://semver.org/lang/pt-BR/spec/v2.0.0.html).
A parte pública de cada peça é o que um projeto usa dela: como se roda, o que recebe (os
argumentos e a configuração, pelo molde em `esquemas/`), o que entrega (a saída e os códigos
de saída) e os módulos comuns da tabela acima. Enquanto o primeiro número for 0, qualquer
coisa pode mudar, e cada publicação sobe o segundo número. Da 1.0.0 em diante, sobe:

- **o primeiro número** quando uma peça muda de um jeito que obriga o projeto que a usa a
  mudar também, ou sai da prateleira;
- **o segundo** quando entra uma peça, ou algo novo que não obriga nenhum projeto a mudar,
  ou quando uma peça fica obsoleta;
- **o terceiro** quando se corrige uma falha sem mudar o uso.
