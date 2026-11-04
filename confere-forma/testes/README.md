# testes de confere-forma

    python3 -I teste_confere_forma.py <pasta do confere_forma.py> <pasta de trabalho nova>

Tudo é inventado: o esqueleto (a abertura e os títulos, estes com caracteres que são especiais
numa expressão regular, e três lacunas, uma delas com uma marca que tem outra dentro e outra
com uma alternativa no topo da expressão), a configuração (as marcas da seção, do divisor e do
fecho, a forma do começo das seções, a das siglas, a da primeira vez delas, com o que vem logo
antes e logo depois, o trecho de fora, uma marcação com uma sigla dentro, os nomes e a segunda
marca de itálico), os dois arquivos de padrões proibidos
(uma regra em cada um, uma delas com exceção) e os documentos, com palavras e siglas sorteadas
e letras de fora do ASCII. O teste confere o que a peça faz, nunca uma frase pronta: em que
arquivo e linha sai cada `ERRO` (quantos em cada linha), se sai `AVISO`, o código de saída e o
resumo que conta os textos, os erros e os avisos.

Cada defeito vai num documento próprio, que anota a linha em que o erro tem de sair:

- abertura com a primeira linha fora do esqueleto, com o texto fixo diferente, com linha a
  mais e com linha que falta;
- seções fora de ordem, seção a mais, seção que falta e título com texto a mais; o título com
  outra palavra no lugar da lacuna, que não é erro, e com o que a lacuna não aceita;
- seção sem divisor e divisor fora do lugar;
- seção que começa por uma linha fora da forma (só a primeira linha conta), seção só com o
  fecho, que então é o começo dela, e seção sem nada no fim, com o erro no título;
- seção sem fecho, com dois, com texto depois dele e linha de bloco fora dele;
- siglas fora da forma na primeira vez: a de uma linha, as duas de uma linha só, a do fim da
  linha, a com a explicação longe, a com o antes longe, a com o depois longe, a só com o
  antes, a só com o depois, a que antes só apareceu numa linha que não se confere e a que só
  apareceu dentro do trecho de fora; e não são erro a da forma na primeira vez, também logo
  depois do trecho de fora, a de dentro do trecho de fora e as vezes seguintes, na forma ou
  fora dela; noutro texto, cada sigla conta de novo;
- padrão proibido, e o mesmo padrão dentro do bloco, onde a exceção vale;
- nome fora do itálico: o longo (o curto dentro dele não conta de novo), o curto sozinho, o
  nome só em negrito; e não são erro o nome em itálico com cada uma das duas marcas, em
  negrito e itálico, colado a outras letras, ou numa linha que não se confere.

O documento certo não dá erro nem aviso. Sem os divisores, o esqueleto dá os mesmos erros;
sem lacunas, ele vale letra por letra; e, sem o começo das seções e sem as siglas, nada deles
se confere. Sem o `antes` das siglas, só o `depois` vale, e, sem o `depois`, só o `antes`; a
forma da sigla se confere na linha inteira, também no que é trecho de fora. Sem arquivo de
padrões proibidos, nenhum padrão é proibido, e as duas regras num
arquivo só dão os mesmos erros que em dois. O `marcas-de-ia.json` da peça deixa passar o
documento certo e uma linha com a tipografia comum (travessões, aspas curvas, reticências,
grau e micro) e pega, cada um na linha dele, os exemplos do README: o espaço sem quebra, o de
largura zero, a marca de direção do texto, `oaicite`, `contentReference` e `utm_source=`. O
tamanho acima do máximo ou abaixo do mínimo dá `AVISO` e sai com 0; igual aos limites, não dá
aviso.

Com o modelo do rodapé (o divisor, um padrão proibido e um nome fora do itálico, com um link
para um arquivo), o rodapé no fim do documento certo fica fora da conferência e das palavras;
no documento com defeito, os `ERRO` de antes do rodapé saem nas mesmas linhas; o rodapé que não
está no fim se confere; e, nos documentos sem rodapé, o modelo não muda nenhum `ERRO`. Sem o
modelo, o rodapé se confere como o resto do texto.

Saem com 2, sem conferir: o modelo do rodapé que falta, com o erro que diz o arquivo; a
configuração com campo desconhecido, com a abertura ou os títulos, que vêm do esqueleto, de
outra versão, com campo que falta, seção sem o grupo do título, expressão ou começo das seções
que não compila, mínimo maior que o máximo ou que não é número, marca de itálico vazia,
padrões proibidos dentro dela, lacuna sem marca, com marca sem letra, repetida ou que não
compila, siglas sem um campo, sem o antes nem o depois, com campo desconhecido e com o padrão,
o antes, o depois ou o trecho de fora que não compila ou que casa com o vazio; o esqueleto
que não existe, que não se lê em UTF-8, com uma linha que não é da abertura, de seção nem
divisor, sem uma lacuna da configuração ou com uma linha que, com as lacunas, não compila, com
o erro que diz o arquivo; o arquivo de padrões proibidos com campo desconhecido, de outra
versão, com regra de campo desconhecido, sem nome, com nome sem letra, sem padrão, com padrão
vazio ou que não compila ou com exceção que não compila, com o mesmo nome em dois arquivos ou
duas vezes num, dado duas vezes, que não existe ou que não é JSON, com o erro que diz o
arquivo; o texto que não existe ou que não se lê em UTF-8. Duas rodadas dão o mesmo.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

O teste precisa das pastas irmãs `extrator/`, `rodape/` e `documentos/` da peça. As cópias
estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), com essas três como pastas irmãs:

    python3 -I ../../copias-estragadas/estraga.py .. teste_confere_forma.py estragos.json <pasta de trabalho nova> --irma ../../extrator --irma ../../rodape --irma ../../documentos

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
