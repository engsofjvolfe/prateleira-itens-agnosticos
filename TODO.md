# TODO

O que falta fazer na prateleira, e só o que falta, em ordem. O que fica pronto sai daqui e
entra no [CHANGELOG.md](CHANGELOG.md), na seção `Não publicado`. O
[relatório](RELATORIO-AGNOSTICO.md) diz onde está cada problema e como corrigir.

1. **As peças das divergências, do dicionário das dúvidas e do glossário**, para qualquer
   projeto que ensina a partir de fontes, com o que é de cada projeto na configuração ou no
   comando:

   - **as divergências:** a lista dos fatos que as fontes dizem de formas diferentes, cada
     um com a forma que o material ensina e as outras, cada forma com a fonte; a peça
     confere o fato repetido e grava o documento delas, ou confere que ele está em dia, e a
     citação de cada fonte se confere no documento gravado, pela peça que confere citações;
   - **o dicionário das dúvidas:** as dúvidas que as fontes deixam, cada uma sob os códigos
     do que ela toca e com as respostas que teve, para a mesma informação não se repetir; a
     peça confere os códigos dos títulos (a forma de cada um, a ordem, o código que cobre
     outro e o repetido), com a forma dos códigos na configuração;
   - **o glossário:** os termos com a definição tirada da fonte e a citação dela, mais os
     termos que os documentos marcam com `<dfn>`; a peça grava o glossário em ordem
     alfabética, ou confere que ele está em dia, com a âncora de cada termo e o link para o
     lugar de cada marca.
2. O JSON de saída do `itens-numerados` só com dados (item 1 do relatório).
3. O `confere-forma` sem texto narrado no JSON (item 2 do relatório).
4. A lista de estragos do `copias-estragadas` conferida contra a peça antes da rodada (item
   3 do relatório).
5. **Os padrões proibidos do `confere-forma` em arquivos próprios**, só com dados e com o
   molde `esquemas/proibidos.schema.json`, dados pelo `--proibidos`, que pode se repetir: as
   regras de todos se somam, e duas com o mesmo nome são erro. A peça traz o
   `marcas-de-ia.json`, com as marcas que uma ferramenta de IA deixa num texto, para
   qualquer projeto. A opção, o molde e o nome do arquivo são esses porque os projetos já
   rodam o conferidor assim.
6. **Um gancho de leitura completa**, que serve a qualquer projeto e a qualquer programa:
   todo documento se lê inteiro e se analisa, e o gancho barra todo meio de ler um
   documento cortando partes (busca por palavra, recorte de linhas ou de trechos, leitura de
   uma parte só, resumo feito por outra ferramenta). O
   [busca-por-palavra](ganchos/busca-por-palavra/README.md) cobre só a busca por palavra,
   deixa passar os padrões livres e não vê a busca feita por outro programa.
7. **Um gancho do changelog**, para o `CHANGELOG.md` de cada repositório seguir, daqui a um
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
8. Quando houver um repositório remoto, pôr no fim do changelog o link de cada versão.
