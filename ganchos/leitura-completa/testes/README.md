# testes de leitura-completa

    python3 -I teste_leitura_completa.py <pasta de leitura_completa.py> <pasta de trabalho nova> [--semente N]

Tudo é inventado e sorteado, sempre igual, porque a semente é fixa (outra semente vem com
`--semente`): os comandos que cortam, o prefixo, na configuração da leitura do terminal, os
textos do motivo e do fim, a pasta das anotações e os arquivos lidos, com o número de linhas
sorteado e letras de fora do ASCII. O protocolo do programa que roda o gancho também é
sorteado, pelo [`protocolo_inventado.py`](../../protocolo/testes/protocolo_inventado.py): os
eventos, as chaves e as respostas. Ele traz a ferramenta de terminal, uma de busca, uma que
resume e uma de leitura, que dá à primeira linha um número sorteado e lê, sem o campo das
quantas, um número sorteado de linhas. Nada é de um projeto real nem de um programa de
verdade.

O teste confere o que o gancho faz, nunca uma frase pronta:

- no terminal, é barrado o comando que corta, de uma ou de duas palavras, também com outras
  no meio, depois de um operador, de um prefixo e de uma atribuição, com o caminho e dentro
  de `$( )` ou de crases; o comando que não se lê também; o resto passa, também o nome do
  comando como argumento, entre aspas, num comentário ou como parte de outro nome;
- a ferramenta de busca e a que resume são barradas sempre;
- na leitura, passam três:
  - a que começa na primeira linha, sem o campo do começo ou com ele até a primeira linha;
  - a que continua na linha seguinte à última lida, em pedaços de tamanhos sorteados, até
    o fim;
  - a que repete o último pedaço;
- é barrada, com o arquivo, as linhas lidas e as que ele tem, a leitura que começa em outra
  linha, também a que pula uma linha ou volta menos que o último pedaço; a leitura sem o
  campo das quantas lê as linhas sem limite;
- as linhas do arquivo são as separadas pela quebra de linha, com ou sem ela no fim; o que
  não é texto UTF-8, o que não existe e a pasta ficam de fora;
- o caminho parte da pasta da chamada, e o caminho por atalho ou com `..` é o mesmo arquivo;
- no fim, com arquivo lido em parte, a resposta trava, com o texto do fim e cada arquivo
  uma vez, na ordem dos caminhos, com as linhas lidas e as que ele tem; a leitura continua
  depois da trava, e o arquivo lido até o fim não entra; na volta da trava, o fim libera e
  apaga as anotações; sem nada lido em parte, não diz nada;
- cada sessão tem a sua pasta, e cada arquivo lido em parte, a sua anotação nela, na pasta
  da configuração, com os nomes tirados do id da sessão e do caminho, e nada mais fica ali;
  o id da sessão nunca vira caminho; a anotação nova é um arquivo novo, que toma o lugar da
  de antes;
- o bloqueio é a resposta que nega do protocolo, com o texto do motivo e a parte que
  bloqueou;
- antes de uma chamada, o erro a barra: a configuração fora do molde ou de outra versão, o
  comando sem palavra, a configuração da leitura do terminal fora do molde, o texto do
  motivo que falta, a ferramenta desconhecida, a leitura sem o caminho ou sem o id da sessão
  e o número que não é inteiro ou fica abaixo do menor;
- no fim, a configuração fora do molde, o texto do fim que falta e a sessão sem id saem com
  erro; o protocolo fora da forma, a entrada que não é JSON, o evento desconhecido e a falta
  de uma opção do comando também;
- o gancho nunca escreve nos arquivos lidos, e a mesma entrada dá a mesma saída.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../../copias-estragadas/README.md), com as pastas da leitura do terminal,
do extrator e do protocolo ao lado da cópia:

    python3 -I ../../../copias-estragadas/estraga.py .. teste_leitura_completa.py estragos.json <pasta de trabalho nova> --irma ../../leitura-do-terminal --irma ../../../extrator --irma ../../protocolo

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../../LICENSE-CONTENT.txt).*
