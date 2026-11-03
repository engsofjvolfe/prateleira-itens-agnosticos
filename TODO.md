# TODO

O que falta fazer na prateleira, e só o que falta, em ordem. O que fica pronto sai daqui e
entra no [CHANGELOG.md](CHANGELOG.md), na seção `Não publicado`. O
[relatório](RELATORIO-AGNOSTICO.md) diz onde está cada problema e como corrigir.

1. O JSON de saída do `itens-numerados` só com dados (item 1 do relatório).
2. O `confere-forma` sem texto narrado no JSON (item 2 do relatório).
3. A lista de estragos do `copias-estragadas` conferida contra a peça antes da rodada (item
   5 do relatório).
4. O documento gravado que não se lê em UTF-8 como falta no `grava-ou-confere` (item 6 do
   relatório).
5. O comando de busca só de espaços como erro da configuração no `busca-por-palavra` (item 7
   do relatório).
6. O `glossario` só pelas marcas dos documentos, sem a lista das definições em JSON (item 3
   do relatório). Por rebase, no commit em que a peça entrou, e não num commit novo.
7. O `divergencias` com cada forma pelo lugar dela na transcrição da fonte (o arquivo e as
   linhas), com o trecho copiado pela peça, e a forma ensinada como escolha, nos dados (item
   4 do relatório). Por rebase, no commit em que a peça entrou, e não num commit novo.
8. O `dicionario-das-duvidas` grava o dicionário: cada dúvida pelos lugares dela na
   transcrição da fonte, com o trecho copiado pela peça, e a resposta como escolha, nos
   dados. Por rebase, no commit em que a peça entrou, e não num commit novo.
9. No leitor de molde do módulo comum do `extrator`, o JSON só com dados: como erro, todo
   texto que não é dado (texto corrido, narração, quebra de linha, marcação Markdown, como a
   citação em bloco, o negrito e o itálico) e o vínculo a um texto que precise ser lido para
   o JSON funcionar. Por rebase, no commit em que o leitor passou a conferir o molde inteiro,
   e não num commit novo.
10. A peça dos trechos escritos por IA: a lista sai das marcas dos documentos, com a abertura
    e o fechamento na configuração, o título de cada documento e o link para a linha de cada
    trecho, sem texto no JSON; o caminho do link e o título do documento pelas funções do
    módulo de Markdown que o `glossario` também usa. O começo dela está no ramo
    `trechos-de-ia`, fora do `main`.
11. As licenças da prateleira: o código sob GPL-3.0 (`LICENSE`) e os documentos e os dados sob
    CC BY-NC-SA 4.0 (`LICENSE-CONTENT.txt`), com os badges e a seção da licença no README; e
    uma peça que grava e confere o rodapé da licença no fim de cada documento de um
    repositório, com o modelo do rodapé dado no comando e o link para o arquivo da licença a
    partir da pasta de cada documento. O `confere-forma` (o rodapé depois da última seção) e
    as peças que gravam documentos (`glossario` e `divergencias`, pelo `documento_gerado.py`)
    passam a aceitar o rodapé.
