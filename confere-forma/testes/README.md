# testes de confere-forma

    python3 -I teste_confere_forma.py <pasta do confere_forma.py> <pasta de trabalho nova>

Tudo é inventado: a configuração (as marcas da seção, do divisor e do fecho, os títulos com
caracteres que são especiais numa expressão regular, a abertura, os nomes e a segunda marca
de itálico), os dois arquivos de padrões proibidos (uma regra em cada um, uma delas com
exceção) e os documentos, com palavras sorteadas e letras de fora do ASCII. O teste confere
o que a peça faz, nunca uma frase pronta: em que arquivo e linha sai cada `ERRO` (quantos em
cada linha), se sai `AVISO`, o código de saída e o resumo que conta os textos, os erros e os
avisos.

Cada defeito vai num documento próprio, que anota a linha em que o erro tem de sair:

- abertura com a primeira linha fora do modelo, com o texto igual diferente, com linha a
  mais e com linha que falta;
- seções fora de ordem, seção a mais e seção que falta;
- seção sem divisor e divisor fora do lugar;
- seção sem fecho, com dois, com texto depois dele e linha de bloco fora dele;
- padrão proibido, e o mesmo padrão dentro do bloco, onde a exceção vale;
- nome fora do itálico: o longo (o curto dentro dele não conta de novo), o curto sozinho, o
  nome só em negrito; e não são erro o nome em itálico com cada uma das duas marcas, em
  negrito e itálico, colado a outras letras, ou numa linha que não se confere.

O documento certo não dá erro nem aviso. Sem arquivo de padrões proibidos, nenhum padrão é
proibido, e as duas regras num arquivo só dão os mesmos erros que em dois. O
`marcas-de-ia.json` da peça deixa passar o documento certo e uma linha com a tipografia
comum (travessões, aspas curvas, reticências, grau e micro) e pega, cada um na linha dele,
os exemplos do README: o espaço sem quebra, o de largura zero, a marca de direção do texto,
`oaicite`, `contentReference` e `utm_source=`. O tamanho acima do máximo ou abaixo do mínimo
dá `AVISO` e sai com 0; igual aos limites, não dá aviso.

Saem com 2, sem conferir: configuração com campo desconhecido ou que falta, item da
abertura com os dois campos ou sem nenhum, seção sem o grupo do título, expressão que não
compila, mínimo maior que o máximo ou que não é número, marca vazia, padrões proibidos
dentro dela, título que não é texto; arquivo de padrões proibidos com campo desconhecido, de
outra versão, com regra de campo desconhecido, sem nome, com nome sem letra, sem padrão, com
padrão vazio ou que não compila ou com exceção que não compila, com o mesmo nome em dois
arquivos ou duas vezes num, dado duas vezes, que não existe ou que não é JSON, com o erro
que diz o arquivo; texto que não existe ou que não se lê em UTF-8. Duas rodadas dão o mesmo.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), com o extrator como pasta irmã:

    python3 -I ../../copias-estragadas/estraga.py .. teste_confere_forma.py estragos.json <pasta de trabalho nova> --irma ../../extrator
