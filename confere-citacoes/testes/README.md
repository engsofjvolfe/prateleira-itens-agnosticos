# testes de confere-citacoes

    python3 -I teste_confere_citacoes.py <pasta do confere_citacoes.py> <pasta de trabalho nova>

Tudo é inventado: a configuração (as marcas da referência e do trecho, o modelo do título
de página, a marca de supressão, os grupos de equivalentes), as fontes e os textos, com
palavras sorteadas e letras de fora do ASCII. O teste confere o que a peça faz, nunca uma
frase pronta: em que arquivo e linha sai cada `ERRO`, o código de saída e o resumo que
conta os erros que saíram.

- Passam: trecho na página citada; trecho que cruza duas páginas, citado com o intervalo;
  trecho que aparece em duas páginas, citado com a segunda; equivalentes trocados; espaços,
  tabulações e quebras de linha diferentes; pedaços partidos na supressão, com pontas;
  página de rótulo que não é número; letra decomposta (NFD); páginas soltas separadas.
- Dão `ERRO` na linha certa: trecho com página errada; trecho que cruza duas páginas citado
  com uma só; trecho que só está num bloco ignorado ou antes da primeira página; trecho com
  outras maiúsculas; pedaço que falta junto de um que está; intervalo ao contrário; parte de
  página vazia; fonte que não existe; fonte com bloco ignorado que não fecha; referência sem
  trecho; trecho sem referência.
- Saem com 2, sem conferir: configuração com campo desconhecido, sem um campo, com
  expressão que não compila ou sem um grupo, com modelo de arquivo de outro campo, com grupo
  de equivalentes de um caractere, com supressão vazia, também num texto sem citação; pasta
  das fontes ou texto que não existe; texto que não se lê em UTF-8.
- Duas rodadas dão o mesmo.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), com o extrator como pasta irmã:

    python3 -I ../../copias-estragadas/estraga.py .. teste_confere_citacoes.py estragos.json <pasta de trabalho nova> --irma ../../extrator
