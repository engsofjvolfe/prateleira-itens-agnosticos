# ganchos

Ganchos: programas que o programa em que a IA trabalha roda em momentos de uma sessão, com
o evento em JSON na entrada padrão. Cada um tem a pasta, a configuração e os testes dele. O
que é do programa — os eventos, as chaves do evento, a forma das respostas e as ferramentas
dele — vem do protocolo, num arquivo do projeto.

**[protocolo/](protocolo/README.md)** — lê o protocolo dos ganchos de um programa, de um
arquivo do projeto: os eventos, as chaves do evento, a forma de cada resposta e as
ferramentas, com os campos de cada uma; lê o evento, monta a resposta e dá o arquivo da
anotação de cada sessão; não se roda (com testes).

**[regras-de-codigo/](regras-de-codigo/README.md)** — gancho que entrega as regras de código
antes da primeira escrita de código ou de dados de cada tarefa, bloqueia o comando de
terminal que escreve em arquivo ou roda código escrito nele e não deixa a resposta encerrar
sem a conferência desses arquivos; textos e planilhas ficam de fora (com testes).

**[busca-por-palavra/](busca-por-palavra/README.md)** — gancho que barra a busca por palavra
para achar ou decidir o que ler ou mudar, no terminal e nas ferramentas de busca, menos a
dos padrões livres, como a lista dos títulos de um texto, e, no terminal, a dos códigos
exatos no arquivo que se dá a ele (com testes).

**[leitura-do-terminal/](leitura-do-terminal/README.md)** — lê um comando de terminal como
o shell lê, com os prefixos do shell na configuração dela, para os ganchos que precisam
saber o que ele roda; não se roda (com testes).

**[destino-da-limpeza/](destino-da-limpeza/README.md)** — gancho que guarda o arquivo para
onde uma limpeza leva o que tira de outros arquivos: ele só cresce, entre blocos, e só na
resposta em que saiu texto de uma das origens; o terminal não mexe nele (com testes).

**[chamadas-permitidas/](chamadas-permitidas/README.md)** — dois ganchos: a cancela, que só
deixa rodar a chamada de ferramenta que uma regra da lista do projeto permite, cada regra
com a forma exata da chamada e o trecho da documentação que a dá, e barra o resto na hora,
também um programa que ainda não existe; e o registro, que grava cada chamada antes de ela
rodar e não deixa rodar a que não consegue gravar (com testes).
