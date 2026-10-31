# Relatório das regras da prateleira

Cada peça desta prateleira conferida contra as regras dela (estão em
[organizacao/](organizacao/README.md#as-regras)): DRY (a mesma lógica num lugar só),
modular (uma coisa só, ligada às outras por arquivos ou por módulos comuns documentados),
nada fixo no código, JSON só com dados, determinismo, preparo para o novo (o desconhecido dá
erro claro) e testes sem overfit. Um item por problema que ainda existe; "arquivo:linha" diz
onde está; "Correção" diz como resolver.

## DRY

1. **A leitura de um texto e a conferência da codificação repetidas.** O módulo comum dá o
   `le_texto`, mas `confere-citacoes`, `confere-forma`, `ganchos/busca-por-palavra`,
   `ganchos/destino-da-limpeza`, `ganchos/regras-de-codigo` e `itens-numerados` ainda leem
   os textos por conta própria; e `custo-de-agentes` e `historico-de-arquivo` conferem, cada
   um, se a codificação da configuração existe. Correção: as duas coisas pelo módulo comum.

## Nada fixo no código

Nenhum caminho de máquina nos códigos e nos READMEs (os comandos usam `<prateleira>`). O
que fica no código das peças é a forma que a peça trata, documentada no README dela: a
sintaxe do Markdown em `confere-forma` (itálico entre marcas iguais, negrito com a marca
dobrada, palavra como `\w+`) e a tabela separada por tabulação em `custo-de-agentes`. O
que é do programa em que a IA trabalha — os eventos dos ganchos, as chaves do evento, a
forma das respostas, os nomes das ferramentas e dos campos — vem do protocolo, num arquivo
do projeto, lido pelo `ganchos/protocolo`, e o código que barra uma chamada vem no comando.

## JSON só com dados

2. **Narração no JSON de saída do `itens-numerados`.** Cada problema leva um `detalhe`, uma
   frase pronta, no JSON que outro programa lê. Correção: o que o problema diz em campos de
   dados, e a frase só na tela.
3. **Texto narrado na configuração do `confere-forma`.** O texto da abertura (`igual`) e os
   `titulos` das seções são texto do documento conferido, dentro do JSON. Correção: esse
   texto num arquivo dado no comando, e o JSON só com a forma.

## Determinismo

Sem problema conhecido: as listagens são ordenadas e o sorteio dos testes tem semente fixa.

## Preparo para o novo

4. **Código de saída da entrada que não serve.** A regra é sair com 2 quando a
   configuração ou um argumento não serve, mas `copia-para-projeto/copia.py`,
   `copias-estragadas/estraga.py`, `documentos/teste_linhas_longas.py`,
   `extrator/extrator.py`, `historico-de-arquivo/historico_de_arquivo.py`,
   `itens-numerados/itens.py` e `moldes/entrada.py` saem com 1. Correção: 2 nesses casos,
   com o teste de cada um conferindo.

## Testes

Toda peça com código tem teste com dados inventados e uma lista de estragos que o teste
pega inteira, menos esta:

5. **`documentos` fora da forma de uma peça.** Os testes ficam na pasta da peça, sem
   `testes/` nem o README deles; o teste dos links usa dados fixos, não sorteados, e confere
   as linhas de saída como frases prontas; e o `teste_linhas_longas.py` não tem teste nem
   estragos. Correção: a forma de uma peça, com o teste conferindo regras.
