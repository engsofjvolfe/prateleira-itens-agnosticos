# Relatório das regras da prateleira

Cada peça desta prateleira conferida contra as regras dela (estão em
[organizacao/](organizacao/README.md#as-regras)): DRY (a mesma lógica num lugar só),
modular (uma coisa só, ligada às outras por arquivos ou por módulos comuns documentados),
nada fixo no código, JSON só com dados, determinismo, preparo para o novo (o desconhecido dá
erro claro) e testes sem overfit. Um item por problema que ainda existe; "arquivo:linha" diz
onde está; "Correção" diz como resolver.

## DRY

1. **Outro jeito de ler a forma dos dados.** O leitor de molde do
   `extrator/extrator_comum.py` (`le_conferido`) confere o molde inteiro, mas
   `ganchos/chamadas-permitidas/dados.py` confere a configuração e a lista das regras valor
   por valor, sem molde e sem `versao_schema`; e o `extrator/extrator.py` e o
   `itens-numerados/itens.py` ainda tratam o `KeyError` e o `TypeError` de um dado que falta
   ou é de outro tipo, que o molde não deixa mais chegar. Correção: o `chamadas-permitidas`
   lendo pelo leitor do módulo comum, pela pasta irmã, como o `busca-por-palavra` já faz,
   com um molde para cada arquivo de dados, e sem o tratamento que sobrou.
2. **Funções de texto repetidas.** Passar a forma Unicode para NFC e juntar os espaços
   aparece em `moldes/analises.py` (`nfc`) e em `confere-citacoes/confere_citacoes.py`
   (`letras`, `comparavel`). Correção: um módulo de texto comum, documentado, usado pelas
   duas.

## Nada fixo no código

Nenhum caminho de máquina nos códigos e nos READMEs (os comandos usam `<prateleira>`). O
que fica no código das peças é a forma que a peça trata, documentada no README dela: a
sintaxe do Markdown em `confere-forma` (itálico entre marcas iguais, negrito com a marca
dobrada, palavra como `\w+`) e a tabela separada por tabulação em `custo-de-agentes`. O
que é do programa em que a IA trabalha — os eventos dos ganchos, as chaves do evento, a
forma das respostas, os nomes das ferramentas e dos campos — vem do protocolo, num arquivo
do projeto, lido pelo `ganchos/protocolo`, e o código que barra uma chamada vem no comando.

## Determinismo

Sem problema conhecido: as listagens são ordenadas e o sorteio dos testes tem semente fixa.

## Preparo para o novo

Sem problema conhecido: o leitor de molde diz o caminho do campo que falta ou é de outro
tipo, e o molde que usa o que ele não entende é erro.

## Testes

Toda peça com código tem teste com dados inventados e uma lista de estragos que o teste
pega inteira. `documentos/teste_linhas_longas.py` é ele mesmo uma conferência, sem teste
próprio.
