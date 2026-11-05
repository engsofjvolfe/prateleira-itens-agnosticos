# TODO

O que falta fazer na prateleira, e só o que falta, em ordem. O que fica pronto sai daqui e
entra no [CHANGELOG.md](CHANGELOG.md), na seção `Não publicado`. O
[relatório](RELATORIO-AGNOSTICO.md) diz onde está cada problema e como corrigir.

1. O JSON de saída do `itens-numerados` só com dados (item 3 do relatório).
2. A lista de estragos do `copias-estragadas` conferida contra a peça antes da rodada (item
   6 do relatório).
3. O documento gravado que não se lê em UTF-8 como falta no `grava-ou-confere` (item 7 do
   relatório).
4. O comando de busca só de espaços como erro da configuração no `busca-por-palavra` (item 8
   do relatório).
5. O `glossario` só pelas marcas dos documentos, sem a lista das definições em JSON (item 4
   do relatório). Por rebase, no commit em que a peça entrou, e não num commit novo.
6. O `divergencias` com cada forma pelo lugar dela na transcrição da fonte (o arquivo e as
   linhas), com o trecho copiado pela peça, e a forma ensinada como escolha, nos dados (item
   5 do relatório). Por rebase, no commit em que a peça entrou, e não num commit novo.
7. O `dicionario-das-duvidas` grava o dicionário: cada dúvida pelos lugares dela na
   transcrição da fonte, com o trecho copiado pela peça, e a resposta como escolha, nos
   dados. Por rebase, no commit em que a peça entrou, e não num commit novo.
8. No leitor de molde do módulo comum do `extrator`, o JSON só com dados: como erro, todo
   texto que não é dado (texto corrido, narração, quebra de linha, marcação Markdown, como a
   citação em bloco, o negrito e o itálico) e o vínculo a um texto que precise ser lido para
   o JSON funcionar. Por rebase, no commit em que o leitor passou a conferir o molde inteiro,
   e não num commit novo.
9. A peça dos trechos escritos por IA: a lista sai das marcas dos documentos, com a abertura
   e o fechamento na configuração, o título de cada documento e o link para a linha de cada
   trecho, sem texto no JSON; o caminho do link e o título do documento pelas funções do
   módulo de Markdown que o `glossario` também usa. O começo dela está no ramo
   `trechos-de-ia`, fora do `main`.
10. O erro do git num lugar só, no módulo de Markdown, para o `confere-commit`, o `rodape` e
    o `confere-changelog` (item 1 do relatório).
11. O CSV do `baralho-anki` lido pelo `forma_do_arquivo.py`, do `listas-e-tabelas`, que passa
    a módulo comum (item 2 do relatório).
12. A peça que lista os caracteres de fora do ASCII que não são letra e que entraram nos
    arquivos mudados de um repositório git desde uma revisão de base, com o nome Unicode de
    cada um, para o gancho do commit poder rodá-la.
13. Rodar o teste e as cópias estragadas de uma peça de uma vez, como opção do
    `copias-estragadas`, e o teste de todas as peças de uma prateleira, numa peça; na
    organização, que o teste de todas roda quando muda um módulo comum.
14. Na organização, a regra do JSON só com dados inteira: nenhum texto que não seja dado e
    nenhum vínculo a um texto que precise ser lido para o JSON funcionar; no relatório, o que
    ela acusa em cada peça.
15. O `listas-e-tabelas` com os modelos dos campos montados dados no comando, e não
    apontados na configuração. Por rebase, no commit em que a peça entrou, e não num commit
    novo.
16. Na organização, as regras que faltam: a peça só fica na prateleira se serve a qualquer
    projeto; a peça pronta e oficial pode entrar no lugar de uma escrita do zero, adaptada
    para ficar agnóstica; nada depende de uma lista feita à mão, e a norma oficial e a
    solução pronta vêm antes de uma regra nova; e, no DRY, a repetição entre ferramentas
    diferentes, com dados de forma diferente, pode ficar, e o que pode seguir DRY e não é a
    hora fica anotado no relatório e no TODO.
17. O README de cada peça abrindo pelo uso: a que serve, quando serve, o que ela não faz e um
    exemplo inventado; essa forma escrita na organização e no README, e os READMEs das peças
    que ainda não abrem assim.
18. No README, o gancho do git da prateleira: o que ele confere antes de cada commit e como se
    põe num clone.
19. A peça do índice: grava o índice de um repositório, com cada peça, módulo comum ou
    documento e o que ele é, tirado dele mesmo, ou confere que o gravado está em dia, para o
    gancho do commit rodá-la. Com ela, o README e a organização deixam de listar as peças, os
    módulos e os arquivos comuns, os encadeamentos e a estrutura, e apontam para o índice.

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](LICENSE-CONTENT.txt).*
