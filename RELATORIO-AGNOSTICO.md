# Relatório das regras da prateleira

Cada peça desta prateleira conferida contra as regras dela (estão em
[organizacao/](organizacao/README.md#as-regras)): DRY (a mesma lógica num lugar só),
modular (uma coisa só, ligada às outras por arquivos ou por módulos comuns documentados),
nada fixo no código, JSON só com dados, determinismo, preparo para o novo (o desconhecido dá
erro claro) e testes sem overfit. Um item por problema que ainda existe; "arquivo:linha" diz
onde está; "Correção" diz como resolver.

## DRY

Sem problema conhecido: o que várias peças fazem do mesmo jeito fica nos módulos comuns,
documentados no [README](README.md#como-as-peças-se-ligam).

## Nada fixo no código

Nenhum caminho de máquina nos códigos e nos READMEs (os comandos usam `<prateleira>`). O
que fica no código das peças é a forma que a peça trata, documentada no README dela: a
sintaxe do Markdown em `confere-forma` (itálico entre marcas iguais, negrito com a marca
dobrada, palavra como `\w+`) e a tabela separada por tabulação em `custo-de-agentes`. O
que é do programa em que a IA trabalha — os eventos dos ganchos, as chaves do evento, a
forma das respostas, os nomes das ferramentas e dos campos — vem do protocolo, num arquivo
do projeto, lido pelo `ganchos/protocolo`, e o código que barra uma chamada vem no comando.

## JSON só com dados

1. **Narração no JSON de saída do `itens-numerados`.** Cada problema leva um `detalhe`, uma
   frase pronta, no JSON que outro programa lê. Correção: o que o problema diz em campos de
   dados, e a frase só na tela.
2. **Texto narrado na configuração do `confere-forma`.** O texto da abertura (`igual`) e os
   `titulos` das seções são texto do documento conferido, dentro do JSON. Correção: esse
   texto num arquivo dado no comando, e o JSON só com a forma.

## Determinismo

Sem problema conhecido: as listagens são ordenadas e o sorteio dos testes tem semente fixa.

## Preparo para o novo

Sem problema conhecido: o desconhecido dá erro claro, que diz o que e onde, e a entrada que
não serve sai com código 2.

## Testes

Toda peça com código tem teste com dados inventados e uma lista de estragos que o teste
pega inteira, menos esta:

3. **`documentos` fora da forma de uma peça.** Os testes ficam na pasta da peça, sem
   `testes/` nem o README deles; o teste dos links usa dados fixos, não sorteados, e confere
   as linhas de saída como frases prontas; e o `teste_linhas_longas.py` não tem teste nem
   estragos, nem quem confira os códigos de saída dele. Correção: a forma de uma peça, com o
   teste conferindo regras.
