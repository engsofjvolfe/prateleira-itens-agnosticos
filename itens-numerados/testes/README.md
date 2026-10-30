# testes de itens-numerados

    python3 -I teste_itens.py <pasta de itens.py> <pasta de trabalho nova>

Sorteia um documento, sempre o mesmo, porque a semente é fixa: um manual numerado com
capa, sumário, corpo e anexos, num padrão de transcrição e com formas de linha que não são
os de nenhum documento real. Os títulos têm caracteres que o padrão escapa e trechos
destacados. Uns itens têm o título na linha seguinte, e umas entradas do sumário têm o
número sozinho numa linha. O título no sumário pode ser só o começo do título do item.
Entre os itens há texto e notas de rodapé numeradas, e na capa uma data que parece número
de item.

O teste confere regras que valem para qualquer documento, nunca uma lista pronta:

- os itens que saem são os do documento, na ordem, com a série, o número, o título sem as
  marcas, a página e a linha; nem a nota de rodapé nem a data da capa passam por item;
- sem erro no documento, nenhum problema. Com um erro posto no documento sorteado (um
  número que salta, um repetido, uma entrada do sumário sem item, um título diferente),
  sai o problema dele, só ele, na linha dele; com os quatro, saem os quatro;
- os grupos, com vários tamanhos e também com um sumário que começa depois dos primeiros
  itens: cada item fica num grupo só, na ordem, e cada grupo começa onde deve, com o
  número de entradas certo e as páginas do primeiro e do último item;
- todo erro para tudo, sem gravar nada, e duas rodadas dão a mesma saída.

Precisa do `extrator_comum.py`, do extrator, na pasta irmã `extrator/` ou na mesma pasta.
Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas de `itens.py` estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md):

    python3 -I ../../copias-estragadas/estraga.py .. teste_itens.py estragos.json <pasta de trabalho nova> --irma ../../extrator
