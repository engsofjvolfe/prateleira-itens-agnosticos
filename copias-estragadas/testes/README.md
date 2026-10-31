# testes de copias-estragadas

    python3 -I teste_estraga.py <pasta do estraga.py> <pasta de trabalho nova>

Monta uma peça inventada, com uma função que soma e um texto, testes inventados dela e
listas de estragos inventadas. O teste confere regras, nunca uma frase pronta:

- o estrago que quebra o que o teste da peça confere é pego, o que não quebra não é, e o
  que não se aplica é erro;
- a contagem do fim é a das linhas, e o código de saída diz se todos foram pegos;
- a peça original não muda;
- com `--so`, só rodam os estragos que batem com algum filtro, na ordem da lista, e o
  filtro sem o `=`, ou que não bate com nenhum estrago, é erro;
- os argumentos de `--antes` chegam ao teste, e cada pasta de `--irma` fica ao lado da
  cópia, sem a pasta `testes/`; duas com o mesmo nome são erro;
- lista com campo desconhecido ou que falta e pasta de trabalho que não está vazia são
  erro;
- com erro, que sai com código 2, nada roda;
- duas rodadas dão a mesma saída.

Precisa do `extrator_comum.py`, do extrator, na pasta irmã `extrator/`. Diz `0 falha(s)`
quando passa; senão, uma linha `FALHA` para cada conferência que não passou, e sai com
código 1.

As cópias estragadas da própria peça estão em `estragos.json`, nesta pasta:

    python3 -I ../estraga.py .. teste_estraga.py estragos.json <pasta de trabalho nova> --irma ../../extrator
