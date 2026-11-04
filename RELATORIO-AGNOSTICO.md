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
dobrada, palavra como `\w+`), a tabela separada por tabulação em `custo-de-agentes`, em
`baralho-anki`, a tabela Markdown, as colunas do CSV e o esquema antigo da coleção do Anki e,
em `rodape`, o link Markdown em linha e os padrões do git para os documentos. O
que é do programa em que a IA trabalha — os eventos dos ganchos, as chaves do evento, a
forma das respostas, os nomes das ferramentas e dos campos — vem do protocolo, num arquivo
do projeto, lido pelo `ganchos/protocolo`, e o código que barra uma chamada vem no comando.

## JSON só com dados

1. **Narração no JSON de saída do `itens-numerados`.** Cada problema leva um `detalhe`, uma
   frase pronta, no JSON que outro programa lê. Correção: o que o problema diz em campos de
   dados, e a frase só na tela.
2. **Texto corrido na lista do `glossario`.** Em `glossario/esquemas/glossario.schema.json:18`,
   a `definicao` e a `fonte` de cada termo são texto do documento dentro do JSON. Correção: o
   glossário só pelas marcas dos documentos, com o link para o lugar em que cada termo é
   explicado, sem a lista das definições.
3. **Texto corrido na lista do `divergencias`.** Em
   `divergencias/esquemas/divergencias.schema.json:17`, o que cada forma `diz` e a `fonte`
   dela, e o `fato`, na linha 26, são texto do documento dentro do JSON. Correção: cada forma
   pelo lugar dela na transcrição da fonte (o arquivo e as linhas), com o trecho copiado pela
   peça, e a forma ensinada como escolha, nos dados.

## Determinismo

Sem problema conhecido: as listagens são ordenadas e o sorteio dos testes tem semente fixa.

## Preparo para o novo

4. **A lista de estragos conferida só no meio da rodada.** Em
   `copias-estragadas/estraga.py:53`, o arquivo de cada estrago é lido com o `read_text`
   direto, quando a rodada já começou: o `arquivo` da lista que não existe na peça, ou que
   não se lê em UTF-8, só aparece depois dos estragos de antes dele, com o erro do Python; e
   o texto `de` que não aparece uma vez só no arquivo dá `ERRO` naquele estrago e código 1,
   embora a docstring diga que, com erro na lista, nada roda. Correção: antes da rodada, ler
   o arquivo de cada estrago escolhido pelo `le_texto` do módulo comum e contar nele o texto
   `de`, com o `ERRO` que diz o estrago e o arquivo e o código 2.
5. **O documento gravado lido sem conferir a codificação.** Em
   `grava-ou-confere/grava_ou_confere.py:34`, o `--conferir` lê o documento gravado com o
   `read_text` direto: o que não se lê em UTF-8 dá o erro do Python, e não a mensagem de
   falta. Correção: o documento gravado que não se lê em UTF-8 é diferente do texto e sai
   com a mensagem de falta e o código 1.
6. **O comando de busca só de espaços aceito pela configuração.** Em
   `ganchos/busca-por-palavra/esquemas/busca-por-palavra.schema.json:20`, o `comando` de uma
   busca só precisa ser um texto não vazio: o que só tem espaços passa pelo molde, vira uma
   lista sem palavras e, em todo comando de terminal, quebra o gancho com o erro do Python,
   em `ganchos/leitura-do-terminal/leitura_do_terminal.py:227`, e não com o `ERRO` da
   configuração. Correção: o `comando` pela regra de linha do molde comum, como os comandos
   do `leitura-completa`.

## Testes

Sem problema conhecido: toda peça com código tem, em `testes/`, teste com dados inventados e
sorteados, que confere regras, e uma lista de estragos que o teste pega inteira.

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](LICENSE-CONTENT.txt).*
