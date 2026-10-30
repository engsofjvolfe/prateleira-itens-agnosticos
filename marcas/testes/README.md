# testes de marcas

    python3 -I <prateleira>/marcas/testes/teste_marcas.py <prateleira>/marcas <pasta de trabalho nova> [--semente N]

A pasta de trabalho precisa ser nova ou vazia: o teste grava nela as linhas de cada arquivo
inventado, com o número de cada uma, como a peça as recebe, para mostrar o que falhou.

O teste sorteia tudo o que testa, sempre igual, porque a semente é fixa (outra semente vem
com `--semente`): os níveis, com acento; as unidades e as regiões de cada uma, numa ordem
que se escreve, com níveis pulados, regiões que não recebem códigos, regiões do meio do
caminho no esperado e fora dele, e regiões irmãs; os códigos de cada região, um deles
esperado em duas, e os que valem em qualquer região; e o texto certo, em arquivos cujos
nomes vêm na ordem contrária à de leitura, com comentários que não são marca, comentários
vazios, marcas no meio da linha, duas na mesma linha, marca em três linhas, marcas em NFD e
com outros espaços, e números de linha com buracos. Uma unidade tem sempre todos esses
casos.

Ele confere regras, nunca uma frase pronta:

- as marcas saem na ordem, com o arquivo, o número dado, o nível e o código em NFC;
  comentário que não começa por um nível não é marca; um comentário vai até o primeiro fim;
  o que não fecha sai sem nível, e nada depois dele sai;
- o caminho de cada marca é o do lugar dela: abrir um nível fecha os de dentro, e cada
  arquivo começa sem nada aberto;
- o texto certo não dá aviso;
- cada estrago do texto dá exatamente os avisos do caso dele, com o caso, o arquivo, a
  linha, a unidade e o código; FALTA só no caso da falta; o texto do aviso diz o código e,
  quando há, o lugar de antes; todos os casos aparecem;
- vários estragos juntos saem em ordem de arquivo e linha; duas rodadas, e o esperado e os
  códigos que existem em outra ordem, dão os mesmos avisos;
- com um nível só, a unidade é a região;
- níveis e esperado que não servem dão `ErroDeMarcas`, que diz o que está errado.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), rodado desta pasta:

    python3 -I ../../copias-estragadas/estraga.py .. teste_marcas.py estragos.json <pasta de trabalho nova>
