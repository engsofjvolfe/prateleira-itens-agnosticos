# testes de regras-de-codigo

    python3 -I teste_regras_de_codigo.py <pasta de regras_de_codigo.py> <pasta de trabalho nova>

Tudo é inventado: os textos das regras, os formatos sem conferência, os comandos que
escrevem, os prefixos e os destinos livres; e o protocolo do programa que roda o gancho,
sorteado pelo [`protocolo_inventado.py`](../../protocolo/testes/protocolo_inventado.py) (os
eventos, as chaves e as respostas), com a ferramenta de terminal e os campos do caminho de
escrita. Nada é de um projeto real.

O teste confere o que o gancho faz, nunca uma frase pronta:

- antes da primeira escrita de uma tarefa, saem todos os textos de regras, na resposta de
  contexto do protocolo, para arquivo de qualquer formato fora da lista `sem_conferencia`,
  sem extensão ou de extensão desconhecida; nas escritas seguintes, nada;
- o arquivo de um formato da lista, em maiúsculas ou minúsculas, não recebe as regras, não
  conta como a primeira escrita e não vai para o fim;
- no fim, com arquivos escritos, a resposta trava e lista cada arquivo uma vez, com as
  regras e a ordem de conferir; na volta da conferência, libera e limpa; a tarefa seguinte
  recomeça;
- no terminal, o comando que escreve em arquivo, que roda código escrito nele ou que não
  se lê é bloqueado, na resposta que nega, com a parte que causou o bloqueio; o resto
  passa, inclusive o que está entre aspas ou fora do lugar de comando; o terminal não anota
  nada;
- configuração fora do molde, protocolo fora da forma, sessão com nome de caminho, evento
  desconhecido, ferramenta sem campo de caminho conhecido, entrada que não é JSON e a falta
  de um dos textos do comando dão erro.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas de `regras_de_codigo.py` estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../../copias-estragadas/README.md), com as pastas da leitura do terminal,
do protocolo e do extrator ao lado da cópia; as da leitura do terminal e as do protocolo
estão na pasta de testes de cada um:

    python3 -I ../../../copias-estragadas/estraga.py .. teste_regras_de_codigo.py estragos.json <pasta de trabalho nova> --irma ../../leitura-do-terminal --irma ../../protocolo --irma ../../../extrator
