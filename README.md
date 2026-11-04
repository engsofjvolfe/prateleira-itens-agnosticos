# prateleira

![Licenca codigo](https://img.shields.io/badge/C%C3%B3digo-GPL--3.0-blue)
![Licenca conteudo](https://img.shields.io/badge/Conte%C3%BAdo-CC_BY--NC--SA_4.0-blue)

Prateleira de peças: scripts e arquivos de dados que servem a qualquer projeto. Cada peça é
uma pasta com um README (o que faz, o que recebe, o que entrega e como rodar) e, quando tem
código, uma pasta `testes/` com o teste dela e as cópias estragadas que provam que o teste
pega os defeitos. Nos comandos dos READMEs, `<prateleira>` é a pasta onde a prateleira está.

- A organização (as regras, a forma de uma peça, a estrutura, como um projeto usa uma peça
  e como testar): [organizacao/](organizacao/README.md).
- Cada peça conferida contra as regras: [RELATORIO-AGNOSTICO.md](RELATORIO-AGNOSTICO.md).
- O que falta fazer: [TODO.md](TODO.md); o que mudou em cada versão:
  [CHANGELOG.md](CHANGELOG.md).
- As licenças, uma para os programas e outra para o conteúdo: [Licença](#licença).

## As peças

| Peça | O que faz |
| --- | --- |
| [baralho-anki/](baralho-anki/README.md) | gerar, de uma tabela Markdown de palavras-chave feita a partir de textos, um baralho do Anki com um cartão por célula: o CSV com a pergunta, a resposta e o trecho do texto que a sustenta, escritos à mão, a conferência dele contra a tabela e os textos, o pacote determinístico e o registro da conferência de conteúdo (com testes) |
| [confere-changelog/](confere-changelog/README.md) | conferir a forma de um changelog, a do Keep a Changelog, com as versões do Versionamento Semântico inteiro, também a do índice do git, como gancho antes do commit (com testes) |
| [confere-citacoes/](confere-citacoes/README.md) | conferir que cada trecho citado num texto Markdown está, letra por letra, na transcrição da fonte e nas páginas citadas, com os pedaços na ordem da fonte e cada supressão no lugar de alguma coisa (com testes) |
| [confere-commit/](confere-commit/README.md) | conferir um commit antes de ele se fazer, como gancho do git: rodar as conferências de uma lista sobre os arquivos do commit, como estão no índice, e barrar o commit quando alguma falha (com testes) |
| [confere-forma/](confere-forma/README.md) | conferir a forma de documentos Markdown contra o esqueleto deles, com o texto que todos têm igual, e uma descrição só com a forma: abertura, seções, divisores, começo das seções, fecho, siglas, padrões proibidos, nomes em itálico e tamanho; as marcas que uma ferramenta de IA deixa num texto, para qualquer projeto; e o módulo comum que lê os padrões proibidos (com testes) |
| [copia-para-projeto/](copia-para-projeto/README.md) | levar os arquivos de uma peça para um projeto, com o cabeçalho dos scripts dele, e conferir que as cópias estão em dia (com testes) |
| [copias-estragadas/](copias-estragadas/README.md) | provar que o teste de uma peça pega os defeitos dela, rodando-o contra cópias estragadas (com testes) |
| [custo-de-agentes/](custo-de-agentes/README.md) | mostrar o uso de tokens de cada transcrição de sessão, como as dos agentes de um programa de IA (com testes) |
| [dicionario-das-duvidas/](dicionario-das-duvidas/README.md) | conferir os códigos dos títulos de um dicionário das dúvidas, com a forma dos códigos na configuração (com testes) |
| [divergencias/](divergencias/README.md) | conferir a lista dos fatos que as fontes dizem de formas diferentes, com a forma que o material ensina e as outras, e gravar o documento deles, ou conferir que o gravado está em dia (com testes) |
| [documentos/](documentos/README.md) | conferir os links internos dos documentos de um repositório git e as linhas que passam de um limite de caracteres; e o módulo comum que lê um texto Markdown como o GitHub o lê (com testes) |
| [extrator/](extrator/README.md) | tirar por programa o texto de documentos (PDF, HTML, XML, JSON) e gravar a transcrição de cada um, página por página; o módulo comum que lê dados JSON pelo molde; e o módulo de texto comum, que passa um texto para a forma NFC e junta os espaços (com testes) |
| [ganchos/](ganchos/README.md) | ganchos para o programa em que a IA trabalha: as regras de código no começo e no fim de cada tarefa que escreve código ou dados; a barreira à busca por palavra; a leitura completa de todo documento; o arquivo que só cresce para onde a limpeza leva o que tira; a cancela e o registro das chamadas de ferramenta; a leitura do comando de terminal que três deles usam; e a leitura do protocolo de cada programa, que todos usam (com testes) |
| [glossario/](glossario/README.md) | gravar o glossário de um projeto, ou conferir que o gravado está em dia: os termos de uma lista, com a definição e a fonte, e os que os documentos marcam com `<dfn>`, com o link para o lugar da marca, em ordem alfabética (com testes) |
| [grava-ou-confere/](grava-ou-confere/README.md) | gravar um documento que um script gera a partir de dados, ou conferir que o gravado está em dia; e o módulo que lê o cabeçalho, confere o arquivo e monta o texto desse documento (com testes) |
| [historico-de-arquivo/](historico-de-arquivo/README.md) | tirar das transcrições das sessões cada leitura e cada gravação de um arquivo, na ordem do tempo; e ler as transcrições, um evento por linha, para qualquer peça que as filtre (com testes) |
| [itens-numerados/](itens-numerados/README.md) | listar os itens numerados de uma transcrição, conferir a numeração e dividir o sumário em grupos de tópicos (com testes) |
| [listas-e-tabelas/](listas-e-tabelas/README.md) | juntar entradas ao fim de listas de arquivos JSON e trocar campos de linhas de tabelas CSV, pelas mudanças de um arquivo de dados, com cada arquivo gravado na forma que já tem, o campo de texto que se monta de dados feito por um modelo do projeto e nada gravado com problema (com testes) |
| [marcas/](marcas/README.md) | ler os códigos escondidos em comentários de um texto Markdown e conferir se cada um está no lugar em que deveria estar (com testes) |
| [moldes/](moldes/README.md) | dizer em que documento cada trecho das análises cai, contar e listar os trechos de cada documento, dar a cada trecho o que o destino dele nomeia e aplicar um limite por aula (com testes) |
| [rodape/](rodape/README.md) | pôr o mesmo rodapé, feito de um modelo, no fim de cada documento Markdown de um repositório git, como o aviso da licença, com cada link a partir da pasta do documento, ou conferir que todos o têm; e o módulo comum que lê o modelo, põe o rodapé no fim de um texto e o separa dele (com testes) |
| [texto-em-comum/](texto-em-comum/README.md) | dizer quais arquivos de uma pasta têm texto igual ao de arquivos de outras pastas (com testes) |

Os arquivos soltos:

| Arquivo | O que é |
| --- | --- |
| `README.md` | este arquivo |
| `CHANGELOG.md` | o que mudou em cada versão |
| `links-do-changelog.json` | os modelos do link de cada versão no fim do changelog, que o gancho do git dá ao [confere-changelog](confere-changelog/README.md#os-links) |
| `TODO.md` | o que falta fazer |
| `RELATORIO-AGNOSTICO.md` | cada peça conferida contra as regras da prateleira |
| `LICENSE` | a licença dos programas, a GPL-3.0 |
| `LICENSE-CONTENT.txt` | a licença do conteúdo, a CC BY-NC-SA 4.0 |
| `rodape.md` | o modelo do rodapé da licença, que a peça [rodape](rodape/README.md) põe no fim de cada documento e o gancho do git dá ao confere-changelog |
| `rodape.json` | os documentos que levam o rodapé e os que ficam sem ele, os textos que os ganchos mostram |
| `.gitignore` | o que a prateleira não guarda: o cache do Python e as anotações de sessão dos ganchos |

## Como as peças se ligam

Só por arquivos e pelos módulos comuns documentados, que a peça acha na pasta irmã (na
prateleira) ou na própria pasta (numa cópia fora da prateleira).

| Módulo comum | Da peça | Peças que o usam |
| --- | --- | --- |
| `extrator_comum.py`: ler um texto em UTF-8, também com as quebras de linha como estão, ler JSON de um arquivo ou de um texto e pelo molde, pegar um campo com o tipo pedido, comparar dois valores JSON e dizer se um é de um tipo, achar os valores repetidos de uma lista, compilar uma expressão, conferir que uma codificação existe, preencher um modelo, dividir uma transcrição em páginas | [extrator](extrator/README.md#o-módulo-comum) | baralho-anki, confere-changelog, confere-citacoes, confere-commit, confere-forma, copia-para-projeto, copias-estragadas, custo-de-agentes, dicionario-das-duvidas, divergencias, documentos, glossario, historico-de-arquivo, itens-numerados, listas-e-tabelas, marcas, moldes, rodape, ganchos/busca-por-palavra, ganchos/chamadas-permitidas, ganchos/destino-da-limpeza, ganchos/leitura-completa, ganchos/leitura-do-terminal, ganchos/protocolo, ganchos/regras-de-codigo |
| `texto_comum.py`: passar um texto para a forma Unicode NFC e juntar os espaços | [extrator](extrator/README.md#o-módulo-de-texto) | baralho-anki, confere-citacoes, custo-de-agentes, divergencias, extrator, glossario, itens-numerados, listas-e-tabelas, marcas, moldes, texto-em-comum |
| `proibidos_comum.py`: ler os arquivos de padrões proibidos, cada um pelo molde dele, e dizer as regras em que um texto cai | [confere-forma](confere-forma/README.md#o-módulo-dos-padrões-proibidos) | baralho-anki, confere-forma |
| `markdown_comum.py`: ler um texto Markdown como o GitHub o lê: as linhas fora dos blocos de código, o texto sem o código, a âncora de um título, os títulos com a linha, o nível e a âncora de cada um, os marcadores e os links; dar o caminho de um arquivo a partir de uma pasta, o alvo e o link como vão num documento; dar os padrões do git de uma lista com os de fora, o que o git mostra de um comando e os caminhos que ele dá com `-z`; e dar os documentos de um repositório git pelos padrões do git | [documentos](documentos/README.md#o-módulo-de-markdown) | baralho-anki, confere-commit, dicionario-das-duvidas, documentos, glossario, rodape |
| `rodape_comum.py`: ler o modelo de um rodapé, dar o rodapé de um documento, com cada link a partir da pasta dele, pôr o rodapé no fim de um texto e separar de um texto o rodapé do fim; e pôr no leitor de argumentos a opção `--rodape` | [rodape](rodape/README.md#o-módulo-do-rodapé) | confere-changelog, confere-forma, divergencias, glossario, rodape |
| `transcricoes.py`: ler as transcrições de sessão, um evento por linha | [historico-de-arquivo](historico-de-arquivo/README.md) | historico-de-arquivo, custo-de-agentes |
| `grava_ou_confere.py`: gravar um documento gerado ou conferir que está em dia | [grava-ou-confere](grava-ou-confere/README.md) | copia-para-projeto, divergencias, glossario, rodape |
| `documento_gerado.py`: ler o cabeçalho de um documento gerado, conferir que o arquivo dele não é uma entrada nem uma pasta e montar o texto, com o cabeçalho e os blocos | [grava-ou-confere](grava-ou-confere/README.md#o-documento-gerado) | divergencias, glossario, listas-e-tabelas |
| `leitura_do_terminal.py`: ler um comando de terminal como o shell lê, com os prefixos do shell da configuração dela | [ganchos/leitura-do-terminal](ganchos/leitura-do-terminal/README.md) | ganchos/regras-de-codigo, ganchos/busca-por-palavra, ganchos/leitura-completa |
| `protocolo.py`: ler o protocolo dos ganchos de um programa, ler o evento, montar a resposta e dar o arquivo da anotação de cada sessão, ou de cada chave dela | [ganchos/protocolo](ganchos/protocolo/README.md) | ganchos/busca-por-palavra, ganchos/chamadas-permitidas, ganchos/destino-da-limpeza, ganchos/leitura-completa, ganchos/regras-de-codigo |

E os encadeamentos, em que uma peça grava o arquivo que a próxima lê:

- Documentos + configuração do extrator → `extrator/extrator.py` → transcrições, página por
  página → `confere-citacoes` (como fontes) e `itens-numerados/itens.py`.
- Textos Markdown → `confere-forma` (a forma, com o esqueleto deles) e `confere-citacoes` (as
  citações).
- O `CHANGELOG.md` de um repositório, o do índice do git → `confere-changelog`, antes de
  cada commit, pelo gancho do git.
- Os arquivos de um commit, como estão no índice do git, + a lista das conferências →
  `confere-commit/confere_commit.py`, antes do commit, pelo gancho do git → cada conferência,
  rodada numa cópia do índice com os arquivos do commit que são dela, e o commit barrado
  quando alguma falha.
- Os documentos de um repositório + o modelo do rodapé + os padrões dos documentos →
  `rodape/rodape.py` → cada documento com o rodapé dele no fim, ou os que não o têm; e o
  modelo → `confere-forma` e `confere-changelog` (o rodapé do fim, fora da conferência) e
  `divergencias` e `glossario` (o rodapé no fim do documento que gravam).
- A lista das divergências + o cabeçalho → `divergencias/divergencias.py` → o documento das
  divergências → `confere-citacoes` (a citação da fonte de cada forma).
- Um dicionário das dúvidas + a forma dos códigos → `dicionario-das-duvidas/confere_dicionario.py`
  → os títulos fora da regra.
- A lista das definições + o cabeçalho + os documentos com as marcas → `glossario/glossario.py`
  → o glossário → `confere-citacoes` (a citação da fonte de cada definição).
- Um arquivo de mudanças + a configuração das listas e das tabelas + os modelos dos campos
  montados → `listas-e-tabelas/listas_e_tabelas.py` → as entradas no fim das listas JSON e os
  campos trocados nas tabelas CSV, cada arquivo na forma que tinha → as peças que leem as listas
  e as tabelas, como o `divergencias`, o `glossario` e o `baralho-anki`.
- Uma tabela Markdown de palavras-chave + a configuração do baralho → `baralho-anki/gera_csv.py`
  → o CSV, com a pergunta, a resposta e o trecho escritos pelas fontes →
  `baralho-anki/confere_baralho.py` (contra a tabela, as fontes e os padrões proibidos) →
  `baralho-anki/gera_apkg.py` → o pacote do Anki; e a tabela + as fontes →
  `baralho-anki/conferido.py` → o registro da conferência de conteúdo.
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

## Licença

Uma licença diz o que cada pessoa pode fazer com um trabalho: usar, mudar, repassar. A
prateleira usa duas, para duas partes diferentes:

| Parte | Licença | Significa que... |
| --- | --- | --- |
| Programas (os scripts Python das peças e dos testes) | [GPL-3.0](LICENSE) | Pode usar, mudar e repassar, mas as versões mudadas também precisam ficar abertas para todo mundo, com o código dos programas disponível |
| Conteúdo (tudo o que não é programa: os documentos e os dados, como os moldes, as configurações e as listas de estragos) | [CC BY-NC-SA 4.0](LICENSE-CONTENT.txt) | Pode usar e adaptar dando o crédito, sem fins comerciais, mantendo a mesma licença |

A divisão vale por tipo de arquivo, não por uma lista fechada: um arquivo novo do mesmo tipo
já nasce coberto. Cada documento termina no aviso da licença do conteúdo, que a peça
[rodape](rodape/README.md) põe e confere, com o modelo em `rodape.md`.

Ao reusar o conteúdo, o crédito é: "prateleira, licenciado sob CC BY-NC-SA 4.0", com o link
para este repositório.

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](LICENSE-CONTENT.txt).*
