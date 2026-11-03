# testes de rodape

    python3 -I teste_rodape.py <pasta do rodape.py> <pasta de trabalho nova>
    python3 -I teste_rodape_comum.py <pasta do rodape_comum.py> <pasta de trabalho nova>

A pasta de trabalho precisa ser nova; o teste escreve nela. Tudo é inventado e sorteado,
sempre igual, porque a semente é fixa, com letras de fora do ASCII: os repositórios git, os
nomes das pastas e dos documentos, os modelos, os textos e os padrões. Os dois conferem
regras, nunca uma frase pronta, e precisam das pastas irmãs `extrator/` e `documentos/` da
peça; o do script, também da `grava-ou-confere/` e do git, que ele roda sem a configuração do
sistema e da conta e sem subir da pasta de trabalho. Cada um diz `0 falha(s)` quando passa;
senão, uma linha `FALHA` para cada conferência que não passou, e sai com código 1.

## O script

O `teste_rodape.py` monta um repositório com documentos sem rodapé, com o rodapé certo, com o
rodapé de outra pasta, com o rodapé de outros espaços e linhas em branco, vazios e novos, fora
do git; e, que ficam como estão, um que o `.gitignore` deixa de fora, um que segue um padrão de
fora, um de outra extensão e o próprio modelo. A extensão dos documentos e a quebra da
primeira linha do rodapé são sorteadas, e a pasta do arquivo para onde o rodapé leva tem
espaço no nome. Confere:

- com `--conferir`, cada documento que não termina no rodapé dele, e só ele, sai numa linha
  `ERRO` com o caminho e a linha (a do rodapé que ele tem no fim ou, sem nenhum, a última com
  texto), em ordem; o mesmo problema sai com o mesmo motivo, e o que falta e o que está fora
  da forma, com motivos diferentes; o resumo diz quantos documentos e quantos fora do dia; o
  código é 1; nada é gravado;
- sem `--conferir`, cada documento fora do dia, e só ele, ganha o rodapé dele e perde o velho,
  com uma linha por documento e o resumo; o vazio fica só com o rodapé; depois, o `--conferir`
  sai só com o resumo e com 0, e outra rodada não muda nada;
- saem com 2, só com uma linha `ERRO` que diz a pasta ou o arquivo, e sem nada gravado: a
  pasta sem git; a configuração que não é JSON, de outra versão, sem um campo, com campo que o
  molde não conhece, sem documentos, com padrão repetido ou de mais de uma linha; o modelo que
  falta, vazio, com código ou com link para um arquivo que não existe; e o documento que não
  se lê em UTF-8, também com outro documento para gravar antes dele;
- duas rodadas dão a mesma saída.

## O módulo do rodapé

O `teste_rodape_comum.py` monta um modelo com as pontas em branco e links para arquivos (o de
uma imagem, o com âncora e o de uma pasta com espaço no nome, escrito entre `<` e `>` ou
codificado), um link externo e um só de âncora, e documentos em pastas de profundidades
diferentes. Confere:

- sem arquivo, não há modelo;
- no rodapé de cada documento, o alvo de cada link para um arquivo é o caminho a partir da
  pasta do documento, entre `<` e `>` quando tem espaço ou parênteses, com a âncora; o resto
  do modelo, o link externo e o só de âncora ficam como estão;
- o texto com o rodapé é o texto sem os espaços e as quebras do fim, uma linha em branco, o
  rodapé e uma quebra; sem texto, só o rodapé; sem modelo, o texto como vem;
- o rodapé no fim de um texto se acha também com outros alvos, com outros espaços e quebras
  onde o modelo tem um e com espaços e quebras depois dele; o corpo é o texto de antes dele,
  com uma quebra, e a linha é a do começo dele; com dois rodapés, só o do fim sai; não se acha
  o rodapé que não está no fim, o de outro texto, o colado a uma linha, o de outro modelo nem
  num texto sem ele; o texto com o rodapé volta a ele mesmo;
- o modelo que falta, que não se lê em UTF-8, vazio, com código na linha ou em bloco, ou com
  link para um arquivo que não existe é erro que diz o arquivo;
- a opção `--rodape` dá o caminho do modelo, nenhum sem ela, e a ajuda dada aparece na ajuda;
- duas leituras dão o mesmo.

## As cópias estragadas

Estão em duas listas, nesta pasta, para o [`estraga.py`](../../copias-estragadas/README.md),
rodado desta pasta: `estragos.json`, para o `teste_rodape.py`, e `estragos-rodape-comum.json`,
para o `teste_rodape_comum.py`:

    python3 -I ../../copias-estragadas/estraga.py .. teste_rodape.py estragos.json <pasta de trabalho nova> --irma ../../documentos --irma ../../extrator --irma ../../grava-ou-confere
    python3 -I ../../copias-estragadas/estraga.py .. teste_rodape_comum.py estragos-rodape-comum.json <pasta de trabalho nova> --irma ../../documentos --irma ../../extrator

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
