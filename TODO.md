# TODO

O que falta fazer na prateleira, e só o que falta, em ordem. O que fica pronto sai daqui e
entra no [CHANGELOG.md](CHANGELOG.md), na seção `Não publicado`. O
[relatório](RELATORIO-AGNOSTICO.md) diz onde está cada problema e como corrigir.

1. **Um gancho de leitura completa**, que serve a qualquer projeto e a qualquer programa:
   todo documento se lê inteiro e se analisa, e o gancho barra todo meio de ler um documento
   cortando partes (busca por palavra, recorte de linhas ou de trechos, leitura de uma parte
   só, resumo feito por outra ferramenta). O
   [busca-por-palavra](ganchos/busca-por-palavra/README.md) cobre só a busca por palavra,
   deixa passar os padrões livres e não vê a busca feita por outro programa.
2. **Um gancho do changelog**, para o `CHANGELOG.md` de cada repositório seguir, daqui a um
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
3. Um leitor de molde só, completo (item 1 do relatório).
4. Um módulo de texto comum (item 2 do relatório).
5. `moldes/entrada.py` lendo os campos com `campo` (item 3 do relatório).
6. Quando houver um repositório remoto, pôr no fim do changelog o link de cada versão.
