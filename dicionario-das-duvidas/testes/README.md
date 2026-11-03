# testes de dicionario-das-duvidas

    python3 -I teste_confere_dicionario.py <pasta do confere_dicionario.py> <pasta de trabalho nova>

Tudo é inventado e sorteado, com letras de fora do ASCII: o começo do título, as marcas do
código, a marca entre dois códigos, o separador das partes, as formas e os tamanhos da
configuração, e os dicionários. A primeira forma é larga, e aceita até o vazio e as marcas,
para que só a regra das marcas barre o código vazio ou com uma marca dentro; as outras são
estreitas. O teste confere regras, nunca uma frase pronta:

- o dicionário certo, com títulos de um a três códigos em ordem natural (9 antes de 10), um
  bloco de código com títulos fora da regra e linhas que não começam pelo título, passa com
  0;
- cada título fora da regra sai com 1 e um `ERRO` na linha dele: texto que não é código,
  código sem uma das marcas, vazio ou com uma marca dentro, título vazio, códigos separados
  por outra coisa, código com partes demais ou com um tamanho que não vale, parte que só tem
  a forma no começo, código que é o começo de outro, código repetido e códigos fora da ordem
  natural; o código mais longo antes do começo dele dá dois `ERRO`, um de cada problema;
- o resumo diz, nessa ordem, os dicionários, os títulos e os erros;
- com mais de um dicionário, o `ERRO` diz o de cada problema;
- a configuração fora do molde (campo que ele não conhece ou que falta, marca vazia ou com
  quebra de linha, nenhuma forma ou forma vazia, nenhum tamanho, tamanho zero ou repetido,
  outra versão), a forma que não compila, o tamanho que passa do número de formas, a
  configuração que não é JSON e o dicionário que falta ou que não se lê em UTF-8 saem com 2,
  sem nada conferido;
- duas rodadas dão o mesmo.

Precisa do `extrator_comum.py` e do `markdown_comum.py`, nas pastas irmãs da peça. Diz
`0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não passou, e
sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), com as pastas do documentos e do extrator
ao lado da cópia:

    python3 -I ../../copias-estragadas/estraga.py .. teste_confere_dicionario.py estragos.json <pasta de trabalho nova> --irma ../../documentos --irma ../../extrator

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
