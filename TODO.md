# TODO

O que falta fazer na prateleira, e só o que falta, em ordem. O que fica pronto sai daqui e
entra no [CHANGELOG.md](CHANGELOG.md), na seção `Não publicado`. O
[relatório](RELATORIO-AGNOSTICO.md) diz onde está cada problema e como corrigir.

1. **Um gancho do changelog**, para o `CHANGELOG.md` de cada repositório seguir, daqui a um
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
2. O JSON de saída do `itens-numerados` só com dados (item 1 do relatório).
3. O `confere-forma` sem texto narrado no JSON (item 2 do relatório).
4. A lista de estragos do `copias-estragadas` conferida contra a peça antes da rodada (item
   3 do relatório).
5. O documento gravado que não se lê em UTF-8 como falta no `grava-ou-confere` (item 4 do
   relatório).
6. Quando houver um repositório remoto, pôr no fim do changelog o link de cada versão.
