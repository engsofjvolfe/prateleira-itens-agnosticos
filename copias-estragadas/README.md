# copias-estragadas

Prova que o teste de uma peça pega os defeitos dela. Para cada estrago de uma lista, o
`estraga.py` copia a peça para uma pasta nova, troca nela um texto de um arquivo por um
texto estragado e roda o teste da peça contra a cópia. O estrago é pego quando o teste
falha. A peça original nunca muda.

Usa só a biblioteca padrão do Python e o `extrator_comum.py`, do
[extrator](../extrator/README.md), que lê a lista pelo molde dela. Na prateleira, ele é
achado na pasta irmã `extrator/`.

## Como rodar

    python3 -I <prateleira>/copias-estragadas/estraga.py <peça> <teste.py> <estragos.json> <pasta de trabalho nova>

- `--so <campo>=<valor>`: roda só os estragos que têm esse valor nesse campo, como
  `nome=sem-irma` ou `arquivo=calculo.py`, para conferir uma mudança só contra os estragos
  que ela toca; pode repetir, e rodam os que batem com qualquer um, na ordem da lista.
- `--irma <pasta>`: copia essa pasta ao lado da cópia da peça, com o mesmo nome e sem a
  pasta `testes/` dela, para a peça que acha outra na pasta irmã; pode repetir, para a peça
  que acha mais de uma.
- `--antes <argumento>`: um argumento do teste, que vai depois da pasta da cópia e antes
  da pasta de trabalho; pode repetir.

O teste recebe a pasta da cópia, os argumentos de `--antes` e uma pasta de trabalho nova,
nessa ordem.

No fim, uma linha por estrago, que diz se ele foi pego e a última linha do teste, e quantos
foram pegos. Sai com código 0 só quando todos são pegos. O estrago cujo texto não aparece
uma vez só no arquivo é `ERRO`. São `ERRO`, e nada roda: a lista com campo desconhecido, ou
sem um campo; o `--so` sem o `=`, ou que não bate com nenhum estrago; e duas pastas de
`--irma` com o mesmo nome.

## A lista (`estragos.json`)

O molde está em `esquemas/estragos.schema.json`: o `versao_schema` e a lista `estragos`,
cada um com o `nome` (letras minúsculas, números e hífen), o `arquivo` (o caminho dentro
da peça), o texto `de` e o texto `para`. Cada peça guarda a lista dela na pasta de testes
dela.

## Testes

Em [testes/](testes/README.md).
