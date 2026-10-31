# TODO

O que falta fazer na prateleira, e só o que falta, em ordem. O que fica pronto sai daqui e
entra no [CHANGELOG.md](CHANGELOG.md), na seção `Não publicado`. O
[relatório](RELATORIO-AGNOSTICO.md) diz onde está cada problema e como corrigir.

1. A ferramenta repetida na configuração do `historico-de-arquivo` dando erro (item 7 do
   relatório).
2. Os prefixos do terminal num lugar só, na configuração do `leitura-do-terminal` (item 2
   do relatório).
3. Um módulo de texto comum (item 1 do relatório).
4. A leitura de texto e a conferência da codificação pelo módulo comum (item 3 do
   relatório).
5. O código de saída 2 para a entrada que não serve (item 6 do relatório).
6. O `documentos` na forma de uma peça (item 8 do relatório).
7. O JSON de saída do `itens-numerados` só com dados (item 4 do relatório).
8. O `confere-forma` sem texto narrado no JSON (item 5 do relatório).
9. **Os padrões proibidos do `confere-forma` em arquivos próprios**, só com dados e com o
   molde `esquemas/proibidos.schema.json`, dados pelo `--proibidos`, que pode se repetir: as
   regras de todos se somam, e duas com o mesmo nome são erro. A peça traz o
   `marcas-de-ia.json`, com as marcas que uma ferramenta de IA deixa num texto, para
   qualquer projeto. A opção, o molde e o nome do arquivo são esses porque os projetos já
   rodam o conferidor assim.
10. **Um gancho de leitura completa**, que serve a qualquer projeto e a qualquer programa:
    todo documento se lê inteiro e se analisa, e o gancho barra todo meio de ler um
    documento cortando partes (busca por palavra, recorte de linhas ou de trechos, leitura de
    uma parte só, resumo feito por outra ferramenta). O
    [busca-por-palavra](ganchos/busca-por-palavra/README.md) cobre só a busca por palavra,
    deixa passar os padrões livres e não vê a busca feita por outro programa.
11. **Um gancho do changelog**, para o `CHANGELOG.md` de cada repositório seguir, daqui a um
    ano como hoje, o [Keep a Changelog 1.1.0](https://keepachangelog.com/pt-BR/1.1.0/) e o
    [Versionamento Semântico 2.0.0](https://semver.org/lang/pt-BR/spec/v2.0.0.html). Uma
    peça que confere a forma, com a forma na configuração do projeto (só dados):

    - a seção `Não publicado` no topo;
    - cada versão como `## [X.Y.Z] - AAAA-MM-DD`, com `[REMOVIDO]` no fim quando retirada,
      da mais nova para a mais velha;
    - só os tipos `Adicionado`, `Modificado`, `Obsoleto`, `Removido`, `Corrigido` e
      `Segurança`, nessa ordem, nenhum vazio, cada item terminando em ponto;
    - o link de cada versão no fim, quando houver repositório remoto.

    Ligada como gancho do git, antes do commit, para valer em todo commit, qualquer que seja
    o programa que o faz; com molde, teste e estragos, como toda peça.
12. Quando houver um repositório remoto, pôr no fim do changelog o link de cada versão.
