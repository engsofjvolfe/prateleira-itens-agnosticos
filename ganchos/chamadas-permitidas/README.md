# chamadas-permitidas

Dois ganchos para as chamadas de ferramenta que uma IA faz num projeto:

- **a cancela** só deixa rodar a chamada que uma regra da lista do projeto permite. Cada
  regra diz a forma exata da chamada e o trecho da documentação do projeto que a dá. O resto
  é barrado na hora, também um programa que ainda não existe: o que a documentação não dá
  não roda. As ferramentas livres, que não buscam nada, passam sem regra;
- **o registro** grava cada chamada num arquivo antes de ela rodar, barrada ou não, menos as
  das ferramentas que a configuração deixa de fora. A chamada que ele não consegue gravar não
  roda.

Usa só a biblioteca padrão do Python, num sistema que tranca arquivos como o Linux, o
`extrator_comum.py`, do [extrator](../../extrator/README.md), que lê os arquivos pelos
moldes deles, e o [protocolo](../protocolo/README.md), da pasta irmã, que lê o evento pelo
protocolo do programa que roda os ganchos.

## Os arquivos

| Arquivo | O que faz |
| --- | --- |
| `cancela.py` | o gancho que barra a chamada que nenhuma regra da lista permite |
| `registra.py` | o gancho que põe a linha de cada chamada no fim do registro |
| `evento.py` | a configuração e o evento, os mesmos para os dois ganchos, e o jeito de barrar |
| `registro.py` | a forma do registro e a gravação de uma linha nele |
| `esquemas/` | os moldes da configuração, da lista das regras e das partes do evento que os ganchos usam |

## Como rodar

    python3 -I <pasta da peça>/cancela.py --protocolo <protocolo.json> --config <configuração.json> \
        --regras <lista.json> --raiz <pasta principal> --barra-com <código>
    python3 -I <pasta da peça>/registra.py --protocolo <protocolo.json> --config <configuração.json> \
        --registro <arquivo> --barra-com <código>

O programa que roda os ganchos chama os dois antes de cada chamada de ferramenta, qualquer
que seja ela, porque o que passa é dito pela configuração e pela lista, e manda o evento pela
entrada padrão, em JSON.

- `--protocolo`: o protocolo do programa, na forma do [protocolo](../protocolo/README.md):
  dele vêm o nome do evento de antes de uma chamada e as chaves da sessão, da ferramenta, da
  entrada e da pasta de onde ela roda.
- `--barra-com`: o código de saída com que o programa não roda a chamada e mostra o motivo.
  Ele vem no comando, e não num arquivo, para valer também quando um arquivo está quebrado.

O gancho que deixa a chamada rodar não diz nada. O que a barra, ou que não consegue fazer o
trabalho dele (o protocolo, a configuração, a lista ou o evento fora da forma, o registro
que não se grava), diz o motivo na saída de erro e sai com o código de `--barra-com`. Se o
programa sabe barrar a chamada também quando o gancho nem chega a rodar, essa opção dele
fecha o último buraco.

## A configuração

Fica fora da peça, porque nomeia as ferramentas do programa. O molde está em
`esquemas/chamadas-permitidas.schema.json`:

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `fora_do_registro` | a lista das ferramentas cujas chamadas não se gravam |
| `livres` | a lista das ferramentas que a cancela deixa passar sem regra |
| `campos` | para cada outra ferramenta, o campo da entrada, um texto, que a forma de uma regra tem de bater inteira |

Ficam fora do registro, em geral, as ferramentas que leem ou escrevem um arquivo pelo
caminho dele. São livres essas mesmas e as que não buscam nada num arquivo, como a que só faz
uma pergunta. A de terminal é conferida pelo comando. Toda outra ferramenta,
também a que ainda não existe, é barrada, porque a configuração não diz o campo dela.

A ferramenta livre passa antes de a lista ser lida: uma lista quebrada nunca barra a
ferramenta de escrever, com que ela se conserta.

## A lista das regras

É do projeto, porque diz o que a documentação dele dá. O molde está em
`esquemas/regras.schema.json`: o `versao_schema`, a versão do molde, as `partes` e as
`regras`.

As `partes` são pedaços de forma com nome, para que um pedaço repetido, como o que diz o que
é um argumento seguro, fique num lugar só: cada nome, de letras minúsculas e `_`, dá uma
expressão regular. A forma de uma regra usa a parte como `<<nome>>`, que vale a parte entre
parênteses que não guardam o que acham. O nome que não é de uma parte é erro.

As `regras` são uma lista. Cada regra tem:

| Chave | O que é |
| --- | --- |
| `nome` | o nome dela, um só na lista |
| `ferramenta` | a ferramenta a que ela vale |
| `forma` | a expressão regular que o campo da entrada tem de bater inteiro, do começo ao fim |
| `fonte` | o `arquivo` da documentação que dá a chamada e o `trecho` dele que a dá, letra por letra |
| `documentada` | opcional: o `arquivo` e o `texto` que nele tem de estar para a chamada passar, montados com as partes que a forma nomeia, como `(?P<script>...)`, cada uma escrita como `{script}` |

A chamada passa só quando roda da pasta principal e bate com a forma de uma regra que vale. A
regra vale quando o trecho da fonte está no arquivo dela; a que perdeu o trecho, porque a
documentação mudou, não deixa passar nada, e o motivo do bloqueio diz o nome dela. A
`documentada` serve à chamada que a documentação dá por um modelo, como "cada script roda
com o comando que a seção dele mostra": a chamada passa só quando o script tem a seção.
Os caminhos que não são absolutos partem da pasta principal.

Por isso um comando novo entra primeiro na documentação e depois na lista. Como a forma bate
com o comando inteiro, o comando que junta outro a ele só passa se a forma deixar: ela deixa
de fora os sinais com que o terminal junta comandos (`;`, `|`, `&`), roda um comando dentro
de outro (`$`, a crase) ou manda a saída para um arquivo (`>`), e nunca tem um trecho que
aceite qualquer coisa, como `.*`.

## O que a cancela ainda não cobre

A cancela olha só as ferramentas que a configuração confere, como a de terminal. As livres
passam sem regra, e entre elas estão as que leem e escrevem um arquivo pelo caminho. Por
isso estas ainda dependem de a documentação ser seguida:

- ler um arquivo que a documentação proíbe, como uma apresentação, o código de um script ou
  um documento de achados inteiro;
- ler só um pedaço de um arquivo que a documentação manda ler inteiro;
- escrever nos arquivos da própria cancela: a lista das regras, a configuração do programa e
  a cópia da peça.

O caminho para fechar: a busca vira a chave que abre a porta. A leitura passa pela cancela,
e um arquivo só se lê inteiro, quando a documentação manda, ou no lugar que uma busca
permitida abriu. Um gancho que roda depois de cada busca permitida lê o que ela devolveu e
abre, para a sessão, cada lugar achado até onde ele acaba: a seção, até o título seguinte do
mesmo nível ou de nível acima; a entrada de um documento de achados; a linha de uma figura.
A saída de um script que dá lugares, como uma lista de trabalho, abre os lugares que ela dá.
No fim de cada resposta, uma conferência vê se cada arquivo de leitura inteira que se abriu
foi lido até a última linha. Antes de construir, duas decisões do projeto: o que se lê
inteiro pode depender do tipo do trabalho de cada sessão, e a cancela precisa saber esse
tipo; e se os arquivos da própria cancela ficam fechados à escrita na sessão, de modo que só
mudem à mão, fora dela.

## O registro

Um arquivo de texto com uma linha por chamada gravada, na ordem das chamadas: um objeto JSON
com exatamente as chaves `sessao` (o id da sessão), `ferramenta` (o nome dela) e `entrada` (a
entrada inteira que ela recebeu, um objeto). A linha nunca se parte, porque o JSON escreve a
quebra de linha de um texto como escape, e cada linha termina com a quebra. Duas chamadas ao
mesmo tempo não misturam as linhas: cada gravação tranca o arquivo. O registro que não existe
nasce; a pasta dele tem de existir.

## Testes

Em [testes/](testes/README.md).
