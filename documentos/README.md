# documentos

Conferências dos documentos e do código de um repositório: as linhas que passam de um limite
de caracteres e os links internos dos documentos Markdown; e o módulo comum que lê um texto
Markdown como o GitHub o lê.

Usam a biblioteca padrão do Python e o `extrator_comum.py`, do
[extrator](../extrator/README.md), que lê os textos; na prateleira, ele é achado na pasta
irmã `extrator/`. O `confere_links.py` precisa também do git e lê o Markdown, os links e os
documentos do repositório pelo [módulo de Markdown](#o-módulo-de-markdown), desta pasta.

## As linhas longas

    python3 -I <prateleira>/documentos/linhas_longas.py 120 "*.py" <arquivo ou pasta>...

O `linhas_longas.py` confere que nenhuma linha passa de um limite de caracteres (o limite
das regras de código é 120): em cada arquivo dado, qualquer que seja o nome, e, numa pasta,
em cada arquivo dela e das subpastas cujo nome segue o padrão; o arquivo achado duas vezes é
conferido uma vez só. O tamanho de uma linha é o número de caracteres dela, sem a quebra do
fim, qualquer que seja ela. Lê o código, não roda nada.

Mostra uma linha `ERRO arquivo:linha: motivo` por linha acima do limite, com o tamanho dela,
em ordem de arquivo e de linha, e um resumo com o número de arquivos conferidos, o de linhas
acima do limite e o limite. Sai com código 0 quando nenhuma passa e 1 quando alguma passa. O
limite que não é um inteiro de 1 para cima, o arquivo ou a pasta que não existe e o arquivo
que não se lê em UTF-8 são `ERRO`, que sai com código 2, sem nenhuma linha conferida.

## Os links

    python3 -I <prateleira>/documentos/confere_links.py <raiz do repositório>

O `confere_links.py` confere os links internos dos documentos Markdown de um repositório
git: os `.md` versionados e os novos que o `.gitignore` não deixa de fora. Em cada link fora
de código (o texto do link pode quebrar de uma linha para a outra), confere que o arquivo do
alvo existe e, quando o alvo tem âncora, que ela é a de um título do arquivo de destino,
calculada como o GitHub calcula (títulos repetidos ganham `-1`, `-2`...), ou a de um
marcador dele (o `id` ou o `name` de uma tag HTML fora de código e de comentário, como
`<a id="x"></a>`, lida como o CommonMark lê uma tag), ou, quando a âncora é a de uma linha
(`#L12`, que o GitHub e o VS Code abrem na linha), que o arquivo, de qualquer tipo, tem essa
linha. Links com esquema, como `https:` e `mailto:`, ficam de fora.

Mostra uma linha `ERRO arquivo:linha: alvo — motivo` por link quebrado, com a linha do
começo do alvo, em ordem de arquivo e de linha, e um resumo com o número de links internos,
o dos com âncora e o de erros. Sai com código 0 quando nenhum está quebrado e 1 quando algum
está. A pasta que não é um repositório git e o documento, ou o Markdown de destino de uma
âncora, que não se lê em UTF-8 são `ERRO`, que sai com código 2, sem nenhum link mostrado.

## O módulo de Markdown

O `markdown_comum.py` guarda o que as peças da prateleira fazem do mesmo jeito com um texto
Markdown, lido como o GitHub o lê. Não se roda: as peças o importam da pasta irmã
`documentos/` ou da própria pasta (numa cópia fora da prateleira, ao lado do script). Usa só
a biblioteca padrão do Python e, nos documentos do repositório, o git.

| Função | O que faz |
| --- | --- |
| `linhas_fora_de_codigo(texto)` | o número e o texto de cada linha fora dos blocos de código: o bloco abre numa cerca de três ou mais `` ` `` ou `~`, com até três espaços antes, e fecha na primeira cerca do mesmo sinal, do mesmo tamanho ou maior, sem texto depois |
| `texto_fora_de_codigo(texto)` | o texto com as linhas dos blocos de código vazias e sem o código na linha, cada linha no número dela |
| `ancora(titulo)` | a âncora que o GitHub dá a um título: o texto como aparece, em minúsculas, sem pontuação, com hífen no lugar de cada espaço |
| `titulos(texto)` | cada título fora dos blocos de código, na ordem, com a linha, o nível (quantos `#`), o texto, sem os `#` e os espaços das pontas, e a âncora; o título repetido ganha `-1`, `-2`... no fim dela |
| `marcadores(texto)` | o valor do `id` e do `name` de cada tag HTML fora de código e de comentário, lida como o CommonMark lê uma tag |
| `links(texto)` | a linha e o alvo de cada link `[texto](alvo)` e `![texto](alvo)` fora de código, na ordem; o texto do link pode quebrar de uma linha para a outra, a linha é a do começo do alvo, e o alvo vem sem os `<` e `>` em volta |
| `alvo_sem_sinais(alvo)` | o alvo de um link sem os `<` e `>` em volta, quando vem entre eles |
| `caminho_relativo(arquivo, pasta)` | o caminho do arquivo a partir da pasta, os dois pelo caminho inteiro, com `/` entre as partes, como vai no alvo de um link |
| `alvo_de_link(alvo)` | o alvo como vai num link: entre `<` e `>` quando tem espaço ou parênteses |
| `link_markdown(texto, alvo)` | o link `[texto](alvo)`, com o alvo como `alvo_de_link` o dá |
| `documentos_do_repositorio(raiz, padroes, fora)` | os caminhos, a partir da raiz e em ordem, dos arquivos de um repositório git, os versionados e os novos que o `.gitignore` não deixa de fora, que existem e seguem um dos padrões do git (pathspec) e nenhum dos de fora; o erro do git e a falta dele vão para a peça que chama |

As expressões `LINK`, do link inteiro, com o alvo no grupo 1, `ALVO_DE_LINK`, do alvo, e
`ESQUEMA`, do começo do alvo de um link externo, como `https:`, e o sinal da âncora no alvo,
`ANCORA`, também ficam no módulo, para as peças que leem os links do mesmo jeito.

## Testes

Em [testes/](testes/README.md).

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../LICENSE-CONTENT.txt).*
