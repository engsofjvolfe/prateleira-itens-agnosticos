# testes de confere-forma

    python3 -I teste_confere_forma.py <pasta do confere_forma.py> <pasta de trabalho nova>

Tudo é inventado: a configuração (as marcas da seção, do divisor e do fecho, os títulos com
caracteres que são especiais numa expressão regular, a abertura, os padrões proibidos, os
nomes e a segunda marca de itálico) e os documentos, com palavras sorteadas e letras de fora
do ASCII. O teste confere o que a peça faz, nunca uma frase pronta: em que arquivo e linha
sai cada `ERRO` (quantos em cada linha), se sai `AVISO`, o código de saída e o resumo que
conta os textos, os erros e os avisos.

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

O documento certo não dá erro nem aviso. O tamanho acima do máximo ou abaixo do mínimo dá
`AVISO` e sai com 0; igual aos limites, não dá aviso. Saem com 2, sem conferir:
configuração com campo desconhecido ou que falta, item da abertura com os dois campos ou sem
nenhum, seção sem o grupo do título, expressão que não compila, mínimo maior que o máximo ou
que não é número, marca vazia, proibido sem nome, título que não é texto; texto que não
existe ou que não se lê em UTF-8. Duas rodadas dão o mesmo.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), com o extrator como pasta irmã:

    python3 -I ../../copias-estragadas/estraga.py .. teste_confere_forma.py estragos.json <pasta de trabalho nova> --irma ../../extrator
