# testes de glossario

    python3 -I teste_glossario.py <pasta do glossario.py> <pasta de trabalho nova>

Tudo é inventado e sorteado, com letras de fora do ASCII: a lista, com termos que começam
por letras com e sem acento, maiúsculas ou não; o cabeçalho; e os documentos, um deles numa
pasta com espaço no nome. O teste confere regras, nunca uma frase pronta:

- o glossário é o cabeçalho, sem os espaços e as quebras do fim, e, em ordem alfabética sem
  contar acentos nem maiúsculas, o título de segundo nível de cada termo e, do termo da
  lista, a definição e a fonte, sem os espaços e as quebras das pontas, e, do termo de uma
  marca, o link para o lugar dela, a partir da pasta do glossário, entre `<` e `>` quando o
  caminho tem espaço;
- o lugar é a seção, o título mais perto acima, de nível 2 em diante, também o da própria
  linha, ou o documento, sob o título de nível 1 ou antes de qualquer título, com o título
  do documento, ou o caminho, e o da seção no texto do link;
- a marca com atributos, em maiúsculas, em duas linhas, com tags dentro ou em NFD conta, e a
  que está num bloco de código ou no código na linha não; o termo da lista e de uma marca
  sai só com a definição;
- o glossário dado entre os documentos fica de fora; sem termo, o glossário é só o
  cabeçalho;
- com `--conferir`, nada é gravado: o glossário em dia sai com 0, e o mudado ou o que falta,
  com 1;
- com o modelo do rodapé, numa pasta mais funda que a do glossário, o glossário termina no
  rodapé, com o link a partir da pasta dele, e está em dia com o modelo, e não sem ele;
- o termo repetido na lista (com outras maiúsculas, outra forma Unicode ou outros espaços),
  a marca vazia, a só com tags e espaços, o termo marcado em dois lugares e dois títulos com
  a mesma âncora (dois termos, ou um termo e o título do cabeçalho) saem com 1, com o `ERRO`
  no lugar de cada um, e nada é gravado;
- a lista fora do molde, que não é JSON ou que não se lê em UTF-8, o cabeçalho que falta,
  vazio ou fora do UTF-8, o documento que falta ou fora do UTF-8, o modelo do rodapé que
  falta e o glossário que é uma entrada (também o modelo) ou uma pasta saem com 2, sem nada
  gravado;
- duas rodadas dão o mesmo.

Precisa do `extrator_comum.py`, do `texto_comum.py`, do `markdown_comum.py`, do
`grava_ou_confere.py`, do `documento_gerado.py` e do `rodape_comum.py`, nas pastas irmãs da
peça. Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), com as pastas do grava-ou-confere, do
documentos, do extrator e do rodape ao lado da cópia:

    python3 -I ../../copias-estragadas/estraga.py .. teste_glossario.py estragos.json <pasta de trabalho nova> --irma ../../grava-ou-confere --irma ../../documentos --irma ../../extrator --irma ../../rodape

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
