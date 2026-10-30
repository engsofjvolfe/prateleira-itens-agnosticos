# O que um projeto ensinou ao modelo

Conhecimento geral tirado de um projeto de material de estudo feito a partir do modelo de
projetos, para o modelo aproveitar. Não descreve o projeto: diz o que vale para qualquer
disciplina, agrupado pelo lugar do modelo que cada coisa toca.

## 1. O modelo vira o projeto

- O projeto nasce de uma cópia do modelo, no mesmo lugar, e cada documento que vem do
  modelo vira documento do projeto: diz como aquele projeto é, no presente, sem ordens e
  sem os caminhos que ele não usa. Acrescentar linhas "neste projeto…" a um texto de
  instruções não basta; o que o texto é, e para que ele serve, muda.
- O que só serve ao começo de um projeto — como descobrir o formato, como montar as
  pastas, como pedir cada etapa a uma IA — não fica no projeto. O modelo precisa separar o
  que vai para o projeto (o motor, os moldes de dados, o esqueleto dos documentos do
  projeto) do que é guia do começo e fica só no modelo.
- O conhecimento que um projeto descobre volta ao modelo como guia genérico, nunca como
  cópia do que o projeto fez.

## 2. Os documentos de um projeto

Cada documento serve a um uso e tem um papel só:

| Documento | Para quê | O que tem |
| --- | --- | --- |
| README | a chegada ao projeto | o que é o projeto e o público dele, o que ele tem, o aviso dos limites do material, a licença de cada parte e um só apontador, para o índice |
| Índice | a leitura do projeto inteiro | a ordem de leitura que melhor o explica, uma linha por documento dizendo o que ele é; é ele que ensina a navegar |
| Glossário | a consulta de um termo | cada termo que o projeto define, com a definição e a citação das fontes ou com o link para o lugar onde é definido; montado por script |
| Manual | o estudo | o programa de revisão, os tipos de documento de estudo e para que serve cada um, como achar um item, como mudar um cartão de vez, como pôr uma imagem num cartão e como relatar um erro |
| NOTICE | o uso permitido | o material de terceiros: a autoria dele, que ele nunca se publica, que nenhuma figura dele vai no que se publica |
| Metodologia | a manutenção do projeto e a confiança nele | como o conteúdo é feito e conferido; os resultados ficam no documento de análise, que ela aponta |
| Diário do trabalho com IA | a história do projeto | os passos gerais percorridos, como diário, não como regra; é o único documento que conta história |
| Regras de citação | a escrita e a conferência de uma referência | as regras da norma para os tipos de fonte que o projeto cita, e o que vai em cada campo do arquivo de fontes |
| README dos scripts | a manutenção do projeto | o que precisa estar instalado e para quê, quando cada script entra, o mapa do projeto e o arquivo de formato, e uma seção por script (o que faz, como rodar, o que mostra), com os caminhos e as fontes do projeto |
| README dos ganchos | a gravação de versões | o que é conferido em cada commit e na mensagem, como se escreve a mensagem, por que a IA não é coautora e como os ganchos se ligam num clone |
| README da pasta protegida | o trabalho com as fontes | uma linha por pasta e por tipo de arquivo, dizendo o que é; o resto aponta para o NOTICE e para a metodologia |

O que vale para todo documento:

- **Atemporal.** Nenhuma frase de estado ("ainda não", "por enquanto") nem lista de
  pendências: o texto é verdadeiro antes e depois de cada passo.
- **Sem repetição.** O que outro documento diz é apontado, não repetido. O comportamento
  de um script é descrito uma vez, na seção dele no README dos scripts, dizendo o que vale
  para todo caso, e os outros documentos apontam para lá; assim uma mudança em outro lugar
  nunca torna um documento falso.
- **Claro no primeiro contato.** O documento aberto daqui a um ano, sem o trabalho
  acompanhado, se entende: cada parte diz o que é dentro do todo, e as palavras se
  explicam.
- **Descreve, não manda.** E não traz nota sobre o que ficou de fora.
- **Termo definido num lugar só, o glossário.** A definição de um termo que um texto do
  material usa mora num arquivo de dados, com a citação das fontes que a dão, e o texto
  que explica o termo põe nele o link para a definição, num marcador do glossário; o
  glossário nunca aponta para um texto. Os outros documentos marcam o termo com `<dfn>` no
  lugar da definição, e o glossário aponta para lá. Um script monta o glossário das duas
  entradas, confere a citação de cada definição e barra o termo definido duas vezes e o
  marcador de dois termos.
- **Depois de qualquer mudança, todos os documentos são lidos inteiros contra ela.** Uma
  busca só acha o que se pensou em procurar. Um verificador de links que calcula a âncora
  de cada título como o GitHub calcula pega o link que uma renomeação quebrou, inclusive
  o de texto quebrado em duas linhas.
- **Um relato de erro serve a qualquer documento** quando pede o título do documento e o
  título mais próximo acima do erro (num cartão, a pergunta), a frase copiada como está e
  o que há de errado nela, com um exemplo.

O documento dos ganchos diz também como se escreve a mensagem de commit, porque o gancho
confere só a forma dela. O título diz o que o commit faz, pelo objetivo do trabalho, com o
commit como sujeito; a explicação segue no mesmo tom, do objetivo para o que veio dele,
cobre tudo o que o commit muda sem percorrer o que cada documento diz nem dizer onde cada
coisa fica, não compara com o antes e se entende sem contexto; nenhuma mensagem leva marca
de coautoria; e uma mensagem aprovada do histórico serve de exemplo. Um
padrão que não está escrito se perde a cada commit, e cada mensagem pede várias voltas até
sair certa.

## 3. Descobrir o formato

O formato de uma disciplina não cabe num molde pronto. O guia de descoberta conduz uma
investigação, e o que ela decide fica gravado como dado (o arquivo de formato) e, com o
porquê, num documento de análise.

- **Duas bases que não se substituem:** a análise do material, que mostra o que ele traz
  e garante que nada fica de fora, e a pesquisa, que mostra o que a matéria precisa cobrir
  nos cursos a que serve e com que profundidade. Uma divisão feita só com a lista de tipos
  de conhecimento é inventário, não formato.
- **O nível de cobrança é resultado de pesquisa**, nunca de opinião.
- **A pesquisa é sobre a forma, não sobre o conteúdo.** Cada curso recebe as mesmas
  perguntas. Ela é mecânica onde dá: a busca fica registrada, o texto de cada fonte é
  tirado por programa do arquivo oficial e lido inteiro, e cada ponto tem o trecho
  literal que o diz. O plano de ensino de uma oferta e os exercícios do livro não são base
  do formato.
- **Cada parte do material se analisa por si, com as mesmas perguntas:** que tipos de
  conhecimento traz e onde, quanto de cada, que forma de estudo serve a cada um, o que a
  liga às outras partes e por que caminhos se estuda. Só com todas lidas a matéria se
  divide em grupos, cada grupo com uma abordagem.
- **Uma matéria pode se estudar por mais de um caminho** — do agente aos efeitos e dos
  efeitos aos agentes possíveis, por exemplo —, e cada caminho é parte estrutural do
  formato, não só um tipo de fato.
- **A lista de tipos de conhecimento cresce com o material:** o trecho que não cabe em
  nenhum ganha tipo novo, com nome e definição (o recurso de memorização que a própria
  fonte dá e o marco histórico são dois que já apareceram).
- **O texto de uma figura entra na análise** com as palavras lidas, marcado como vindo
  da figura; o ilegível vira dúvida anotada.
- **Todo documento tem um molde** — as mesmas partes, na mesma ordem —, não só os que
  têm grade. Os moldes saem de contar, por script, o que as análises põem em cada
  documento, e um script confere que todo trecho tem lugar e nenhuma parte fica vazia. A
  mesma consistência em todo o material é a razão de existir do projeto.
- **O arquivo de formato guarda os documentos e o molde de cada um**, como dado, ao lado
  do resto da forma: para quem é o material e até onde ele vai, os grupos, a sequência das
  partes de um texto por tipo de conhecimento, onde cada tipo se ensina, o que fica fora e
  as marcas. O molde de um documento é de um tipo — partes por tipo de conhecimento, uma
  grade de eixos (com os elos do dicionário), formas de pergunta ou colunas do cartão —, e
  cada coisa que ganha material, a unidade, é um dado do documento dela, com a grade
  própria ou a do documento. A ordem dos documentos no arquivo é a ordem em que eles se
  escrevem em cada aula. Todo script lê o formato do mesmo jeito, conferindo o molde
  dele e as ligações de dentro dele, e a conferência dos moldes usa o formato e as
  análises para dizer onde cada trecho cai.
- **O nome escrito à mão ganha um id por uma tabela.** A análise diz para onde vai cada
  trecho com as palavras dela, e a mesma coisa sai escrita de vários jeitos.
  Uma tabela dá a cada jeito o id do que ele nomeia — a coisa que ganha material, um item
  dela ou um conjunto delas —, e as análises não mudam. O jeito que a tabela ainda não tem
  aparece numa lista, com os trechos dele, até ganhar a linha dele, e o id da tabela que o
  formato não tem é erro.
- **Ensinar primeiro, treinar depois.** Os documentos ensinam; os cartões e as perguntas
  de prova treinam. Cartões e documentos tratam do mesmo conteúdo, mas não se estudam lado
  a lado: o programa de revisão decide quando cada cartão volta.
- **Quando a avaliação é escrita,** um documento de perguntas de prova, com
  resposta-modelo, treina a resposta inteira.

## 4. As fontes e a transcrição

- **Quando a fonte tem texto de verdade** — uma apresentação, um livro digital em HTML
  com as páginas impressas marcadas —, a transcrição sai do próprio arquivo, por script,
  e é o script que a confere contra a fonte. À mão, confere-se só o texto de dentro das
  figuras, lido por OCR.
- **Um livro que só se lê num site** se transcreve da captura que o navegador salva
  durante a leitura: o script guarda uma cópia do documento na pasta protegida, nunca lê
  os dados de sessão, e a captura não fica no projeto.
- **O texto das figuras se confere olhando a imagem, no próprio arquivo de
  conferência,** e a correção volta para a transcrição por script, com o tique da
  correção. O formatador do editor pode reescrever o Markdown ao salvar; o leitor do
  arquivo de conferência, um script, precisa aguentar isso (cercas de qualquer tamanho), ou
  apaga texto sem avisar.
- **Três tipos de figura não valem a correção e nunca são fonte de conteúdo:** desenhos
  com muitos elementos, como um mecanismo, tabelas e gráficos de dados, e imagens cujo
  texto não entra no estudo. O conteúdo de um ponto que vem delas sai da legenda e do
  livro.
- **O texto de dentro de uma figura se escreve por regras fixas** — só o que está
  escrito, um rótulo por linha, na ordem de leitura da figura inteira, símbolos e índices
  como impressos, o ilegível marcado e nunca adivinhado —, para que duas leituras da mesma
  figura deem o mesmo texto e a conferência compare letra por letra.
- **O OCR ilegível se relê** com a imagem ampliada e na posição certa, e a leitura nova
  só fica quando lê mais sem perder palavra que a primeira lia com confiança.
- **A imagem que o editor não mostra** (EMF, WMF, TIFF) aparece numa cópia em PNG, com
  link para o original, e todo caminho com espaço vai entre `<>` no link, ou o link não
  aparece.
- **O texto sai primeiro por programa, e só depois se lê.** A tentativa é sempre o texto
  mecânico do próprio arquivo; a imagem de uma página só se olha onde há dúvida, porque
  ler tudo pela imagem é gasto à toa em documento que tem texto de verdade.
- **Um documento que não traz ano**, como uma apresentação de slides, tem por ano o da
  versão que o projeto usa: o ano em que o autor gravou o arquivo pela última vez, que o
  próprio arquivo registra, como o ano de uma impressão. O documento não traz esse ano
  escrito, e por isso ele vai entre colchetes, como ano certo (NBR 6023:2025, 8.6.1.1 e
  8.6.1.3); o ano não muda com o ano em que o material é repassado. O ano de criação que o
  arquivo registra muitas vezes é o de um modelo antigo e não serve.
- **Um extrator só, com um leitor pequeno para cada tipo de arquivo** (PDF, HTML, XML,
  JSON), e a forma da transcrição como dado: um tipo novo é um leitor novo, sem mexer nos
  outros. Os transcritores que um projeto já tem podem virar leitores dele, só se for
  preciso e sem mudar nada do que já foi gerado.

## 5. O conteúdo

- **Aula em slides dá os pontos e a estrutura; o livro completa cada ponto** com tudo o
  que diz sobre ele. O que o livro diz de um assunto que nenhum slide traz fica fora, salvo
  exceção decidida e escrita.
- **Duas etapas, cada uma com o seu jeito de ler.** A base que arquiteta o material — as
  transcrições, a pesquisa, a análise de cada parte, a análise da matéria, os moldes e a
  lista de trabalho — se faz com a leitura inteira das fontes, nunca por busca de palavras,
  e dá a cada ponto o lugar dele no livro. A escrita do material começa com a base pronta e
  não a repete: nela se leem inteiros a lista de trabalho, que é a lista de checagem do
  texto, conferida por script trecho por trecho, e os lugares do livro que ela dá; o resto
  — as regras da documentação, uma dúvida, o tipo de uma figura, um termo do glossário —
  se acha pela busca do endereço que já se tem, e o que a busca acha se lê inteiro, a seção
  do título até o seguinte do mesmo nível ou de nível acima, sem escolher o que ler dela.
- **Cada texto se entende sozinho.** Ele explica o que é preciso ali, a categoria e o item
  que usa, com as fontes dele, mesmo que outro texto já os explique, e nunca manda a um
  texto de outro assunto só porque lá está a explicação. Por isso
  nenhum texto já escrito se lê para escrever outro: o que o novo precisa vem das fontes
  dele.
- **A grafia é a do livro;** quando aula e livro discordam, vale o livro, com a diferença
  anotada.
- **Um material que cobre só parte das aulas tem um limite por aula.** Uma aula trata de
  uma coisa quando diz dela pelo menos um número dado de partes distintas do molde (duas,
  por exemplo); com menos, só a menciona. O que as aulas cobertas tratam ganha material, e
  o que uma aula de depois diz disso entra junto, com as perguntas de prova nas aulas que
  tratam da coisa; o que elas só mencionam fica onde elas dizem, sem material próprio. O
  trecho das aulas cobertas que fica sem lugar — todos os lugares dele eram de coisas só
  mencionadas, ou nada o leva a um documento — ganha outro no material da própria aula,
  onde ela fala do fato, fora da conta; e qual aula trata de quê pode ser decidido à mão,
  no lugar da conta. A conta diz que a aula *trata de* algo, nunca que o *ensina*: ensinar é
  qualidade de um texto.
- **O que não é assunto do material entra como a fonte o usa:** como comparação, quando
  ela o compara com o assunto; pelo que diz, quando ela fala dele por outro motivo. Nunca
  sai por uma regra geral, e nunca ganha uma comparação que a fonte não faz.
- **Ensinar, não mostrar.** Cada fato se explica como num primeiro contato com a matéria:
  o básico antes do que depende dele, o nome técnico depois do que ele nomeia, o que uma
  figura mostra escrito em texto, sem "o livro diz" nem "veja o slide". E o texto é um
  gatilho rápido de estudo, não outro livro: o mais enxuto que dá sem perder o tom, a
  explicação e o conteúdo.
- **Cada unidade tem um texto só, escrito inteiro na primeira aula que trata dela**, e os
  textos se escrevem aula por aula: em cada aula, o básico antes do que depende dele, e as
  perguntas de prova da aula por último, porque a resposta-modelo usa só o que os textos
  ensinam. Antes de cada texto, um script grava a lista de trabalho dele: os trechos de
  cada parte do molde, cada um com o lugar dele no livro. A lista copia texto das fontes e
  fica na pasta protegida.
- **Cartões:** um fato por cartão, todo fato com pelo menos um; a associação pedida nos
  dois sentidos ganha um cartão em cada sentido, e a lista vira cartões menores; o porquê,
  curto, no verso; nenhum de múltipla escolha; os de fato entram no baralho antes dos de
  porquê. Cada cartão tem dois campos de imagem, um na frente e um no verso, escondidos
  quando vazios, para preencher depois pela planilha.
- **O baralho:** as colunas do cartão saem do molde dele no arquivo de formato, e cada
  campo vazio fica escondido. Cada texto tem a sua planilha, e o baralho se divide em
  baralhos menores, um por aula, para o primeiro contato com cada cartão vir depois da
  leitura do texto dele; os cartões novos entram na ordem das linhas da planilha. O código
  de cada cartão no programa de revisão sai da planilha e da pergunta: corrigir a resposta
  ou pôr uma imagem mantém o histórico de revisão, e só mudar a pergunta faz um cartão
  novo. A imagem vai no pacote como arquivo, e o campo a mostra como imagem do HTML,
  para a verificação de mídia do programa não apagá-la; o pacote que tem imagem fica na
  pasta protegida, porque a imagem de uma fonte nunca se publica, e o sem imagem vai com
  o projeto.

## 6. A conferência

- Primeiro o script, depois a leitura humana; o tique dela é sempre o último, e sai quando
  a parte muda.
- Uma conferência dá a mesma saída toda vez. A leitura de um agente de IA não dá, então
  não serve como conferência: no lugar dela, um script.
- Um "ok" dado à mão não confere conteúdo. Cada parte diz de onde veio, e um script prova
  que nada ficou sem lugar.
- Todo teste roda também contra uma cópia estragada do que ele testa, e precisa falhar.
- **O texto se liga às fontes por códigos escondidos.** Cada texto de estudo marca, em
  comentários que a visualização não mostra, o começo da unidade, o de cada parte do molde
  e o código de cada trecho da fonte que explica. Um script lê esses códigos e diz o
  trecho que falta, o que está na parte errada, o que não existe mais, o trecho sem cartão
  e o próximo texto a escrever. A leitura dos códigos é uma peça genérica: o projeto que a
  usa dá os níveis e o que espera em cada lugar.
- **A conferência dos cartões não depende do gerador de referências.** As chamadas ficam
  num arquivo de dados escrito à mão, com molde, e a conferência reconhece cada citação
  por ele; duas fontes com a mesma chamada são erro, porque a chamada não diria de qual
  delas é o trecho.

## 7. As ferramentas

- Toda ferramenta, mesmo a de uso único, segue as regras de código desde a primeira
  linha: nada do projeto no código, modular, determinística, com teste de dados
  inventados. A que não segue é apagada depois de usada.
- As ferramentas de trabalho que não vão no projeto ficam numa prateleira à parte, cada
  uma descrita e independente das outras.
- **O projeto guarda só os dados dele:** a configuração de cada peça que usa e as
  entradas. As peças rodam direto da prateleira, recebendo esses dados; nada é copiado da
  prateleira para o projeto, e o que é do projeto nasce no projeto, nunca dentro de uma
  peça. A cópia de uma peça só serve ao projeto que precisa funcionar sem a prateleira por
  perto.
- **Cada rodada de teste usa uma pasta nova, num disco local, apagada no fim**, com os
  arquivos temporários dentro dela; os temporários deixados fora dela pelas bibliotecas
  podem encher o disco temporário da máquina.

## 8. O trabalho com uma IA

- A IA responde antes de fazer e diz o plano antes de investigar; um "sim" vale só para o
  que ela listou.
- Agente só para trabalho grande e não localizado, um de cada vez, todos com o mesmo
  texto de instrução. Quando várias partes são analisadas, cada agente lê só a sua, para
  as análises não copiarem critérios umas das outras. Na escrita com a base pronta, o
  trabalho já é localizado: a escrita e a conferência leriam a mesma coisa, e o agente só
  somaria leitura, então a IA escreve e confere sozinha.
- Palavras simples, termo técnico explicado na primeira vez. Para confirmar que entendeu
  um pedido: uma ideia, um exemplo, uma pergunta.
- Antes de usar uma palavra para algo contado, a IA abre os dados e vê o que a coisa é; e
  nunca diz o que um arquivo faz sem abri-lo.
- **A palavra de uma regra vira ordem para a IA.** Uma regra, um rótulo ou o nome de uma
  marca é seguido ao pé da letra: uma marca chamada "comparação" faz procurar comparação
  até onde a fonte não compara. Os nomes dizem só o que a coisa é, e a regra diz "como a
  fonte o usa".
- Uma decisão de escopo, público ou nível fica registrada na hora em que é tomada.
- **Regra que a IA já quebrou vira gancho.** A regra que só está na memória da IA falha de
  novo; um gancho do programa em que a IA trabalha a cobra na hora da ação e barra o que a
  quebra. Assim, as regras de código chegam antes da primeira escrita de cada tarefa,
  nenhum código se escreve pelo terminal, e o registro do que a limpeza tira da memória só
  cresce, e só na resposta em que algo saiu dela. Um gancho que barra a busca por palavra
  segura a leitura inteira enquanto se faz a base; com a base pronta, ele sai, porque a
  busca só acha o lugar e o que ela acha se lê inteiro.
- **A IA não assina como coautora.** Pela lei brasileira de direitos autorais, autor é a
  pessoa física que cria a obra, e o simples auxílio não faz coautoria (Lei nº 9.610/1998,
  arts. 11 e 15, § 1º; para programas, Lei nº 9.609/1998, art. 2º). No lugar da
  assinatura, o projeto diz como a IA foi usada — o que ela faz, o que nunca fica com ela e
  um diário dos passos —, porque o que conferir precisa estar dito. As recomendações do
  ICMJE para revistas médicas seguem o mesmo princípio. O esqueleto da mensagem de commit
  lembra disso, e o documento dos ganchos explica, com as citações.
