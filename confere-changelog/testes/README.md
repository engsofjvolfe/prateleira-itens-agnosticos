# testes de confere-changelog

    python3 -I teste_confere_changelog.py <pasta de confere_changelog.py> <pasta de trabalho nova> [--semente N]

Tudo é inventado e sorteado, sempre igual, porque a semente é fixa (outra semente vem com
`--semente`): os nomes da configuração (a seção do que não foi publicado, a marca da versão
retirada, os tipos de mudança e o fim do item), com letras de fora do ASCII; os modelos dos
links; e os changelogs, com as versões, as datas, os tipos e os itens sorteados, e os
identificadores de pré-lançamento e de construção, de letras do ASCII, maiúsculas e
minúsculas, e hífen. Nada é de um projeto real.

O teste confere o que a peça faz, nunca uma frase pronta:

- o changelog na forma passa: com versão retirada ou sem, com a seção do que não foi
  publicado com tipos ou vazia, sem versão nenhuma, com item de várias linhas e com o começo
  de vários parágrafos; com os pré-lançamentos na ordem da precedência, como no exemplo da
  especificação, com identificadores na ordem do ASCII que não é a das letras sem contar
  maiúsculas, e com metadados de construção; e, com os modelos dos links, com os links de
  cada seção, também com uma versão só, e sem link nenhum quando não há versão;
- cada defeito dá `ERRO` na linha dele, e só nela:
  - no começo, o título que falta e o título antes da primeira seção;
  - nas seções, a do que não foi publicado que falta, repetida ou depois de uma versão;
  - nas versões, a com zero na frente, sem a data, com a data que não existe, com outra
    marca de retirada, fora da ordem ou repetida, e a data fora da ordem;
  - na forma do Versionamento Semântico, o pré-lançamento ou o identificador vazio, o
    identificador só de algarismos com zero na frente ou com outro sinal, o algarismo de
    fora do ASCII e os metadados vazios;
  - na precedência, o pré-lançamento fora da ordem, a versão normal depois do pré-lançamento
    dela e as versões que só mudam nos metadados de construção;
  - nos tipos, o desconhecido, fora da ordem, repetido ou sem item, e a versão sem tipo;
  - nos itens, o sem o fim, também o de várias linhas com o fim só na primeira, o item fora
    de um tipo e a continuação fora de um item;
  - a linha com um espaço no começo, a solta e o título de nível 4;
  - a linha em branco que falta antes ou depois de um título, a dobrada e a que fica entre
    itens; o arquivo sem a quebra no fim ou com linha em branco no fim;
  - os links sem os modelos deles; e, com os modelos, o link errado, a mais, que falta, fora
    da ordem ou sem a linha em branco antes;
- com `--indice`, o conferido é o changelog do índice do git, e não o da pasta, rodado de
  qualquer pasta; as quebras de linha do Windows se leem como as de um arquivo, com e sem
  `--indice`;
- saem com 2 a configuração fora do molde (também com os links dentro dela), de outra
  versão, sem tipo, com tipo vazio ou repetido, com o fim vazio ou com um nome de duas
  linhas; o arquivo dos links que não existe, fora do molde, de outra versão, sem um modelo,
  com um modelo de duas linhas, sem o lugar de um campo dele ou com o de outro, com o erro
  que diz o arquivo; o changelog que não existe e o que não é UTF-8; e, com `--indice`, o
  arquivo fora do índice, o do índice que não é UTF-8 e o de fora de um repositório;
- os erros saem em ordem de linha, e a mesma entrada dá a mesma saída.

O teste precisa do git, que ele roda sem a configuração do sistema e da conta e sem subir da
pasta de trabalho, que poderia estar dentro de outro repositório. Diz `0 falha(s)` quando
passa; senão, uma linha `FALHA` para cada conferência que não passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), com o extrator ao lado da cópia:

    python3 -I ../../copias-estragadas/estraga.py .. teste_confere_changelog.py estragos.json <pasta de trabalho nova> --irma ../../extrator
