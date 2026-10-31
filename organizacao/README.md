# Organização da prateleira

A prateleira é uma pasta de peças que servem a qualquer projeto: cada peça faz uma coisa,
não sabe nada de projeto nenhum e recebe o que é de cada projeto por configuração ou por
argumento. Ela fica numa pasta própria, com todo o conteúdo: as peças, os módulos comuns,
os moldes, as configurações de exemplo, os testes e esta documentação.

## As regras

Toda peça segue estas regras; o [RELATORIO-AGNOSTICO.md](../RELATORIO-AGNOSTICO.md) diz onde
alguma ainda quebra.

- **Agnóstica:** nenhuma peça sabe de um projeto. O que é de um projeto (caminhos, nomes de
  arquivo e de campo, marcas, títulos, textos) fica nos dados dele, fora da prateleira, e
  chega à peça pela configuração ou pelo comando.
- **Nada fixo no código:** o que muda de um uso para outro vem de configuração ou de
  argumento. Fica no código só a forma que a peça trata, dita no README dela.
- **Nenhum programa de IA nas peças:** o que é do programa em que a IA trabalha — o
  protocolo dos ganchos, os nomes das ferramentas e dos campos, a forma das transcrições —
  fica nos dados do projeto, e os textos falam de "o programa", nunca do nome dele.
- **JSON só com dados**, nunca narração nem o caminho de um texto narrado, que vem no
  comando; toda configuração tem `versao_schema` e um molde (JSON Schema) em `esquemas/`, e
  campo que o molde não conhece é erro.
- **DRY:** a mesma lógica num lugar só. O que várias peças fazem do mesmo jeito fica num
  módulo comum documentado (ver o [README](../README.md#como-as-peças-se-ligam)).
- **Modular:** uma peça faz uma coisa e se liga às outras só por arquivos ou por módulos
  comuns documentados; script não serve de biblioteca.
- **Preparada para o novo:** o desconhecido dá erro claro, que diz o que e onde; entrada que
  não serve sai com código 2, sem fazer nada pela metade.
- **Determinista:** a mesma entrada dá a mesma saída; listagens ordenadas, sorteios com
  semente fixa.
- **Testes sem overfit:** dados inventados, sorteados, com letras de fora do ASCII; o teste
  confere o comportamento, nunca uma frase pronta; cada teste vem com a lista de estragos e
  pega todos.
- **Código só pelas ferramentas de escrever arquivo**, nunca por comando de terminal.

## A forma de uma peça

    <peca>/
      README.md            o que faz, como rodar, o que recebe e entrega, códigos de saída
      <script>.py          docstring e comentários sem acento; roda com python3 -I
      esquemas/            o molde de cada configuração (<peca>.schema.json)
      configuracao.json    só com o caso comum a qualquer projeto e programa, como os comandos do terminal
      testes/
        README.md          como rodar e o que se confere
        teste_<nome>.py    recebe a pasta da peça e uma pasta de trabalho nova
        estragos.json      as cópias estragadas que o teste tem de pegar

- O módulo comum de outra peça é achado na pasta irmã (na prateleira) ou na própria pasta
  (numa cópia fora da prateleira): `for pasta in (PASTA.parent / "<peca>", PASTA)`.
- Códigos de saída: 0 sem problema; 1 com problema achado; 2 quando a configuração ou um
  argumento não serve.
- Mensagens: `ERRO arquivo:linha: motivo` por problema, e um resumo no fim.

## A estrutura

    prateleira/
      README.md                    o índice das peças, como elas se ligam e as versões
      CHANGELOG.md                 o que mudou em cada versão
      TODO.md                      o que falta fazer
      RELATORIO-AGNOSTICO.md       cada peça contra as regras
      .gitignore                   o cache do Python e as anotações de sessão dos ganchos
      organizacao/                 esta documentação
      confere-citacoes/  confere-forma/  copia-para-projeto/  copias-estragadas/
      custo-de-agentes/  divergencias/  documentos/  extrator/  ganchos/
      grava-ou-confere/  historico-de-arquivo/  itens-numerados/  marcas/  moldes/
      texto-em-comum/

## Como um projeto usa uma peça

O projeto não copia nada da prateleira. Ele guarda só os dados dele (a configuração de cada
peça, só dados, e as entradas) e roda a peça direto da prateleira, dando a ela esses dados:

    python3 -I <prateleira>/<peca>/<script>.py <dados do projeto>...

O que é de um projeto nasce no projeto, nunca dentro de uma peça. A
[copia-para-projeto](../copia-para-projeto/README.md) só serve ao projeto que precisa
funcionar sem a prateleira por perto: ela leva cópias dos arquivos de uma peça e confere
depois se elas estão em dia.

## Como testar uma peça

    python3 -I <prateleira>/<peca>/testes/teste_<nome>.py <prateleira>/<peca> <pasta de trabalho nova>
    python3 -I <prateleira>/copias-estragadas/estraga.py <prateleira>/<peca> <prateleira>/<peca>/testes/teste_<nome>.py \
        <prateleira>/<peca>/testes/estragos.json <pasta de trabalho nova> --irma <prateleira>/<peca irmã>
