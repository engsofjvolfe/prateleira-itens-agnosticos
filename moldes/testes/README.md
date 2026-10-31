# testes de moldes

    python3 -I <prateleira>/moldes/testes/teste_moldes.py <prateleira>/moldes <pasta de trabalho nova> [--semente N]
    python3 -I <prateleira>/moldes/testes/teste_contar_e_separar.py <prateleira>/moldes <pasta de trabalho nova> [--semente N]

A pasta de trabalho precisa ser nova ou vazia; o teste escreve nela.

São dois testes. O `teste_moldes.py` testa as partes que outros programas importam: a
leitura das análises, as regras de lugar, as tabelas, a leitura de tabelas em texto, a
tabela dos destinos, o limite e o molde da forma das análises. O
`teste_contar_e_separar.py` testa os dois scripts da peça, a contagem e as listas, com as
entradas comuns deles. O projeto que leva só as partes leva só o primeiro.

Os dois sorteiam tudo o que testam, sempre igual, porque a semente é fixa (outra semente
vem com `--semente`). O sorteio e o que se espera de cada caso estão no
`mundo_inventado.py`, que não se roda: uma forma de análise com nomes, separadores, marcas
e papéis que não são os de nenhuma análise real, e um campo com a fonte que ele cita;
regras com tipos de fora, marcas, grupos e documentos, e com coisas a mais que elas não
usam; aulas com slides, trechos, notas, títulos e texto solto; e a forma, as regras e as
análises erradas, cada uma com o que o erro dela tem de dizer. Em toda semente aparecem
todos os casos: trecho de estudo pelo grupo, pelo caminho ou com marca; à espera do
assunto; marcado, com uma ou duas marcas; com a marca só onde ela não se procura; de fora;
com tipo de fora junto de outro; sem documento; com grupo desconhecido. O destino vem em
pedaços, com separador dentro dos parênteses, parêntese dentro de outro, pedaço em NFD,
valor vazio e pedaço repetido. O `teste_moldes.py` sorteia também tabelas em texto, a
tabela dos destinos dos pedaços lidos e lugares para o limite, com todos os casos das
regras dele.

Eles conferem regras que valem para qualquer forma, nunca uma lista pronta. O
`teste_moldes.py`:

- os moldes declaram as formas de campo e os papéis que o código conhece; a forma com a
  fonte que um campo cita passa pelo molde;
- cada trecho é lido de volta, na ordem, com o texto, cada campo e cada papel; as notas são
  contadas, e o que vem depois de um título não se lê; os pedaços são os escritos, inteiros,
  sem o vazio e sem repetir;
- o id é aula/slide/posição/hash, único; o mesmo texto em NFD e em NFC dá o mesmo id, e
  outro texto dá outro; o `le_codigo` lê de volta cada id, e cada começo dele, nas partes
  dele, e não lê o que não é id nem começo de um: o vazio, o sem aula, o com uma parte a
  mais ou vazia, o com espaço na aula, o com zero ou com algo que não é número no slide ou
  na posição, e o com o hash curto, em maiúsculas ou que não é hexadecimal;
- a classe, as marcas, os documentos e os grupos que as regras não têm, de cada trecho, são
  os do caso dele; um mesmo problema sai sempre com a mesma frase, e problemas diferentes
  com frases diferentes;
- a tabela tem o cabeçalho, o alinhamento e uma linha por item; a das classes, uma linha
  por regra de fora e por marca, as outras classes com trecho e o total, e cada classe com
  um rótulo só dela;
- a tabela em texto dá cada linha com o número dela e os valores sem os espaços das pontas,
  sem as linhas em branco, com qualquer fim de linha; a linha com menos colunas tem vazias
  as que faltam no fim; cabeçalho errado e linha com mais colunas são erro que diz o nome e
  a linha;
- a tabela dos destinos dá a cada trecho os ids dos pedaços dele, na ordem e sem repetir,
  comparando em NFC, e lista uma vez cada pedaço sem linha, com os trechos dele; a linha com
  a unidade vazia, com a tabulação do fim ou sem ela, não falta; linha repetida, sem destino
  ou que contradiz outra é erro que diz a linha; destino que não está em pedaços é erro;
  cada id que o programa que usa a tabela não conhece sai com o pedaço dele;
- o limite: trata a aula que diz pelo menos as partes pedidas, só pelos lugares diretos; a
  decisão vale no lugar da conta; a unidade com itens tem material quando algum item é
  tratado; o lugar até a última aula fica em unidade com material, mesmo em item só
  mencionado; depois da última, só fica o que cai em entrada tratada; cada trecho sem lugar
  sai na lista certa; as perguntas de cada trecho de depois vão só para aulas até a última;
  a ordem dos lugares não muda o que fica; entradas que se contradizem são erro que diz
  cada uma;
- na forma, nas regras e nas análises erradas no que o molde não vê, a conferência da parte
  errada (a forma, as regras ou a leitura) é a que pega o erro e diz o que está errado, e a
  leitura das análises pelas regras para com o erro dessa parte;
- duas rodadas dão a mesma saída.

O `teste_contar_e_separar.py`:

- a contagem de cada documento e de cada classe bate com o que foi sorteado, com um
  problema por trecho com problema; o do grupo desconhecido diz o grupo;
- a lista do `separar.py` traz exatamente os trechos do documento, ou os que esperam o
  assunto; a lista de um documento que não é de conteúdo é `ERRO` e não é gravada;
- sem erro, a saída é gravada, numa pasta que o script cria quando ela ainda não existe, e
  a contagem traz a tabela das classes;
- forma, regras e análises erradas dão `ERRO`, que diz o que está errado (no que o molde
  pega, o caminho do valor), e nada é gravado;
- duas rodadas dão a mesma saída, e a ordem em que os arquivos foram criados não muda nada;
  com problema nas análises, a contagem sai com código 1, e sem problema, com 0.

Precisam do `extrator_comum.py` e do `texto_comum.py`, do extrator, na pasta irmã
`extrator/` da peça ou na própria pasta da peça. Cada um diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para
cada conferência que não passou, e sai com código 1.

As cópias estragadas da peça estão em duas listas, nesta pasta, para o
[`estraga.py`](../../copias-estragadas/README.md), rodado desta pasta: `estragos.json`, das
partes comuns, para o `teste_moldes.py`, e `estragos-contar-e-separar.json`, da contagem,
das listas e das entradas, para o `teste_contar_e_separar.py`:

    python3 -I ../../copias-estragadas/estraga.py .. teste_moldes.py estragos.json <pasta de trabalho nova> --irma ../../extrator
    python3 -I ../../copias-estragadas/estraga.py .. teste_contar_e_separar.py estragos-contar-e-separar.json <pasta de trabalho nova> --irma ../../extrator
