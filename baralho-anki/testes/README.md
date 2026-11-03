# testes de baralho-anki

    python3 -I teste_baralho_anki.py <pasta do baralho-anki> <pasta de trabalho nova>

Tudo é inventado e sorteado, com letras de fora do ASCII: a configuração (as colunas, os
campos, que são todas as colunas do CSV em ordem sorteada, com a pergunta no primeiro, a data
com fuso e as marcas de ênfase, com a curta antes da longa), a tabela, depois
de um bloco de código com linhas de tabela e antes de uma segunda tabela, as fontes em duas
pastas (uma delas com a cópia de uma fonte da outra, com uma frase a mais), os
modelos do cartão, com um campo com filtro, e dois arquivos de padrões proibidos, um deles com
exceção. O teste confere regras, nunca uma frase pronta:

- `gera_csv.py`: uma linha por linha da tabela e por coluna de cartão, em ordem, com o id (o
  nome da fonte sem a extensão e o identificador da coluna), o assunto, a coluna, as
  palavras-chave e a fonte da tabela, e a pergunta, a resposta e o trecho vazios; a tabela é a
  primeira do arquivo, fora dos blocos de código, e a segunda fica de fora; de novo, a
  pergunta, a resposta e o trecho de cada id que continua ficam, as palavras-chave vêm da
  tabela de agora, e a linha que a tabela não dá mais sai;
- `confere_baralho.py`: o CSV certo sai com 0, com o trecho achado na fonte em NFD, com outros
  espaços e com as marcas de ênfase no texto ou no trecho; cada defeito sai com 1 e o `ERRO`
  na linha dele: o campo diferente do da tabela, o id que a tabela não dá, o cartão que falta,
  o id repetido, o campo vazio ou só com espaços, como a pergunta, a resposta e o trecho, o
  trecho que não está na fonte, a fonte que nenhuma pasta tem, a linha fora da ordem e o
  padrão proibido de cada arquivo, na pergunta e na resposta, que o exceto deixa passar; a
  primeira pasta que tem a fonte vale; sem arquivo de padrões proibidos, nenhum padrão é
  proibido;
- `gera_apkg.py`: o pacote é um zip com o banco e a lista vazia das mídias, com a data da
  configuração; o banco tem o baralho e o tipo de nota com os ids do hash do nome (também com
  outros nomes sorteados), os campos
  com a letra do editor, os modelos e o estilo como estão nos arquivos, os campos de que a
  frente precisa (um de dois, um deles com filtro, ou o único), e uma nota e um cartão por
  linha, em ordem, com o
  guid do hash do id, o HTML escapado, as ênfases nas etiquetas, as palavras-chave em linhas e
  as etiquetas da fonte e da coluna; duas rodadas dão os mesmos bytes, e outra data, outros
  bytes com os mesmos guids;
- `conferido.py`: com `--gravar`, o sha256 da tabela e o de cada fonte, da primeira pasta que
  a tem, na ordem da tabela; sem ele, o registro em dia sai com 0, e a fonte ou a tabela que
  mudaram, a fonte sem registro, a do registro que a tabela não nomeia e a que nenhuma pasta
  tem saem com 1, com um `ERRO` para cada uma.

Saem com 2, sem gravar nada: a configuração com campo que o molde não conhece, de outra versão,
com a coluna de um campo que o CSV não tem, com nome de campo repetido, com duas colunas de
cartão de mesmo identificador ou com marca de ênfase repetida; a tabela sem a coluna da fonte,
sem tabela, sem linhas ou com uma linha de outro número de células; o CSV com outro cabeçalho
ou com uma linha de outro número de campos; o arquivo de padrões proibidos fora do molde, com
padrão que não compila ou com o nome de uma regra de outro arquivo; a fonte que não se lê em
UTF-8; no pacote, a marca de ênfase sem par, a etiqueta com espaço, o id repetido, o modelo
que falta ou fora do UTF-8 e a data que não se lê; com `--gravar`, a fonte que falta; e o
registro fora do molde.

Precisa do `extrator_comum.py` e do `texto_comum.py`, da peça extrator, do `markdown_comum.py`,
da peça documentos, e do `proibidos_comum.py`, da peça confere-forma, nas pastas irmãs da peça.
Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não passou, e
sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), com o extrator, o documentos e o
confere-forma como pastas irmãs:

    python3 -I ../../copias-estragadas/estraga.py .. teste_baralho_anki.py estragos.json <pasta de trabalho nova> --irma ../../extrator --irma ../../documentos --irma ../../confere-forma
