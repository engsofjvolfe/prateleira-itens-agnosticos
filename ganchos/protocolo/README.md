# protocolo

O protocolo dos ganchos de um programa: o que o programa que roda os ganchos manda a eles e
o que ele espera de volta. Os ganchos desta prateleira o leem de um arquivo de dados do
projeto, e nada de um programa fica no código deles: nem o nome de um evento, nem a chave de
uma parte dele, nem a forma de uma resposta, nem o nome de uma ferramenta. O módulo dá
também o arquivo em que um gancho anota o que guarda de uma sessão, ou de cada chave dela,
como um documento.

Usa só a biblioteca padrão do Python e o `extrator_comum.py`, do
[extrator](../../extrator/README.md), que lê o arquivo pelo molde dele; ele é achado duas
pastas acima (na prateleira) ou na pasta irmã (numa cópia de teste). Não se roda: os ganchos
[busca-por-palavra](../busca-por-palavra/README.md),
[destino-da-limpeza](../destino-da-limpeza/README.md),
[leitura-completa](../leitura-completa/README.md),
[regras-de-codigo](../regras-de-codigo/README.md) e
[chamadas-permitidas](../chamadas-permitidas/README.md) importam o `protocolo.py`, da pasta
irmã.

## O arquivo do protocolo

O molde está em `esquemas/protocolo.schema.json`. O arquivo fica fora da peça: cada programa
tem o seu, e o projeto guarda o do programa em que se trabalha nele.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `eventos` | o nome, no programa, do evento de `antes` de uma chamada de ferramenta e do de `fim` de uma resposta |
| `chaves` | a chave do evento que traz cada parte dele: o nome do `evento`, a `sessao`, a `ferramenta` chamada, a `entrada` dela, a `pasta` de onde ela roda e o `fim_repetido`, o aviso de que o fim da resposta já foi travado uma vez |
| `respostas` | o modelo de cada resposta, um objeto JSON: `nega` (barra a chamada, com o motivo), `contexto` (entrega um texto antes da chamada) e `trava` (não deixa a resposta acabar, com o motivo) |
| `terminal` | a `ferramenta` de terminal e o `campo_comando` da entrada dela |
| `buscas` | cada ferramenta de busca: o `nome` e o `campo_padrao` da entrada dela |
| `escritas` | os `campos_caminho`, que trazem o caminho do arquivo escrito; as `trocas`, ferramentas que trocam um trecho, cada uma com o campo do trecho de `antes`, o do de `depois` e o que pede `todas` as vezes; e os `inteiros`, ferramentas que gravam o arquivo inteiro, cada uma com o campo do texto |
| `leituras` | cada ferramenta de leitura: o `nome`, o `campo_caminho`, o `campo_comeco` (a linha em que a leitura começa), o `campo_quantas` (quantas linhas ela lê), as `linhas_sem_limite` (quantas ela lê sem esse campo) e a `primeira_linha` (o número que o programa dá à primeira linha do arquivo) |
| `resumos` | as ferramentas que leem por outro modelo e entregam um resumo |

No modelo de uma resposta, `{texto}`, em qualquer texto de dentro dele, vira o texto do
gancho: o motivo do bloqueio ou o texto entregue. As chaves e o que não é texto ficam como
estão.

São erro: a versão que não é a do molde; campo que o molde não conhece, que falta, de outro
tipo ou vazio; os dois eventos com o mesmo nome; duas partes com a mesma chave; nenhum campo
de caminho de escrita; a ferramenta repetida numa lista; o modelo de resposta sem `{texto}`
ou com outro campo entre chaves; e o número de uma leitura abaixo do menor que ele pode ser
(1 linha sem limite, 0 para a primeira linha). A mensagem diz o que e onde.

## O que dá

| Nome | O que é |
| --- | --- |
| `ler(caminho)` | o protocolo do arquivo, conferido |
| `le_evento(protocolo, texto)` | as partes do evento que chega em texto JSON: `evento`, que é `antes` ou `fim`, e cada parte que ele traz, pelo nome no molde; erro quando o texto não é um objeto JSON e quando o nome do evento falta ou é de outro evento |
| `resposta(protocolo, qual, texto)` | uma cópia do modelo da resposta `nega`, `contexto` ou `trava`, com o texto no lugar de `{texto}` |
| `anotacao(pasta, sessao, *chaves)` | o arquivo, na pasta, em que um gancho anota o que guarda da sessão; com chaves, como o caminho de um documento, o de cada chave, dentro da pasta da sessão, uma pasta dentro da outra na ordem das chaves. Cada nome é a impressão digital (SHA-256) do id da sessão ou da chave, e por isso nunca sai da pasta; a sessão sem id e a chave que não é texto são erro |
| `ErroDeDados` | o erro de um arquivo ou de um evento fora da forma, do `extrator_comum.py` |

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../LICENSE-CONTENT.txt).*
