# testes de custo-de-agentes

    python3 -I teste_custo.py <pasta do custo.py> <pasta de trabalho nova>

Tudo é inventado: os nomes de todos os campos, o padrão dos arquivos, o tamanho do começo,
os rótulos das colunas e os números de cada turno, sorteados, com letras de fora do ASCII.
O teste calcula de novo, por conta própria, o que cada linha da tabela tem de dizer, e
confere, nunca uma frase pronta:

- o cabeçalho com os rótulos, na ordem;
- uma linha por transcrição com alguma linha, na ordem do caminho e com o caminho a partir
  da pasta: a da subpasta entra; a de fora do padrão e a vazia, não;
- os turnos (só os eventos com o uso como objeto), o contexto máximo, o processado e a
  saída, com o campo que falta, o texto e o booleano valendo 0;
- o começo da primeira pergunta (não o de outro tipo de evento, nem o de pergunta sem
  texto), com os espaços, a quebra de linha e a tabulação juntados, e cortado no tamanho;
  vazio quando não há pergunta;
- a linha que não é objeto JSON e a mensagem que não é objeto ficam de fora.

Saem com 2: configuração com campo desconhecido, que falta (também um rótulo), tamanho
negativo ou que não é número, entrada vazia ou com nome que não é texto, codificação que não
existe; pasta que não existe. Duas rodadas dão o mesmo.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), com as duas peças de que ela precisa como
pastas irmãs:

    python3 -I ../../copias-estragadas/estraga.py .. teste_custo.py estragos.json <pasta de trabalho nova> --irma ../../extrator --irma ../../historico-de-arquivo

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
