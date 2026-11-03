# testes de divergencias

    python3 -I teste_divergencias.py <pasta do divergencias.py> <pasta de trabalho nova>

Tudo é inventado: as listas, os cabeçalhos e os rótulos, sorteados e com letras de fora do
ASCII, e as fontes, blocos de uma a três linhas. O teste confere regras, nunca uma frase
pronta:

- o documento é o cabeçalho, sem os espaços e as quebras do fim, e, para cada divergência,
  na ordem da lista, o título de segundo nível com o fato e, para cada forma, a ensinada
  primeiro e as outras na ordem delas, o rótulo com o que ela diz e a fonte, sem os espaços
  e as quebras das pontas, com uma linha em branco entre os blocos e uma quebra de linha no
  fim; ele é gravado com as pastas que faltam;
- sem divergência, o documento é só o cabeçalho;
- com `--conferir`, nada é gravado: o documento em dia sai com 0, e o mudado ou o que falta,
  com 1, sem nada criado;
- com o modelo do rodapé, numa pasta mais funda que a do documento, o documento termina no
  rodapé, com o link a partir da pasta dele, e está em dia com o modelo, e não sem ele;
- o fato repetido, com outras maiúsculas, outra forma Unicode ou outros espaços, e a forma
  que diz o mesmo que outra do mesmo fato, com outra forma Unicode ou outros espaços, saem
  com 1, com o caminho dos dois no `ERRO`, e nada é gravado; o que a forma diz com outras
  maiúsculas, e o que fatos diferentes dizem igual, passam;
- a lista fora do molde (campo que ele não conhece, campo que falta, outras formas vazias,
  fato com quebra de linha, o que a forma diz ou a fonte só com espaços, outra versão), que
  não é JSON ou que não se lê em UTF-8, o cabeçalho que falta, que não se lê em UTF-8 ou que
  está vazio, o rótulo que falta ou que não é uma linha só com alguma letra, o modelo do
  rodapé que falta e o documento que é a lista, o cabeçalho, o modelo ou uma pasta saem com
  2, sem nada gravado;
- duas rodadas dão o mesmo.

Precisa do `extrator_comum.py`, do `texto_comum.py`, do `grava_ou_confere.py`, do
`documento_gerado.py`, do `rodape_comum.py` e do `markdown_comum.py`, nas pastas irmãs da
peça. Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), com as pastas do grava-ou-confere, do
extrator, do rodape e do documentos ao lado da cópia:

    python3 -I ../../copias-estragadas/estraga.py .. teste_divergencias.py estragos.json <pasta de trabalho nova> --irma ../../grava-ou-confere --irma ../../extrator --irma ../../rodape --irma ../../documentos

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
