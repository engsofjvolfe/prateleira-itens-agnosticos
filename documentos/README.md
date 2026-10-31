# documentos

Conferências dos documentos e do código de um repositório: os links internos dos
documentos Markdown, com o teste do conferidor e as cópias estragadas dele, e as linhas que
passam de um limite de caracteres. Só usam a biblioteca padrão do Python.

**teste_linhas_longas.py** — lista as linhas que passam de um limite de caracteres (o
limite das regras de código é 120): em cada arquivo dado e, numa pasta, em cada arquivo
dela e das subpastas cujo nome segue o padrão. Lê o código, não roda nada. Mostra
`arquivo:linha (tamanho)` de cada uma, em ordem; sai com código 0 quando nenhuma passa, 1
quando alguma passa e 2 quando um argumento não serve (o limite que não é um inteiro de 1
para cima, o arquivo ou a pasta que não existe).

    python3 -I <prateleira>/documentos/teste_linhas_longas.py 120 "*.py" <arquivo ou pasta>...

**confere_links.py** — confere os links internos dos documentos Markdown de um
repositório git: os `.md` versionados e os novos que o `.gitignore` não deixa de fora.
Em cada link fora de código (o texto do link pode quebrar de uma linha para a outra),
confere que o arquivo do alvo existe e, quando o alvo tem âncora, que ela é a de um título
do arquivo de destino, calculada como o GitHub calcula (títulos repetidos ganham `-1`,
`-2`...), ou a de um marcador dele (o `id` ou o `name` de uma tag HTML fora de código e de
comentário, como `<a id="x"></a>`, lida como o CommonMark lê uma tag), ou, quando a âncora
é a de uma linha (`#L12`, que o GitHub e o VS Code abrem na linha), que o arquivo, de
qualquer tipo, tem essa linha. Links com esquema, como `https:` e `mailto:`, ficam de fora.
Mostra uma linha
`ERRO arquivo:linha: alvo — motivo` por link quebrado e um resumo; sai com código 0 quando
nenhum está quebrado, 1 quando algum está e 2 quando a pasta não é um repositório git.

    python3 -I <prateleira>/documentos/confere_links.py <raiz do repositório>

**teste_confere_links.py** — testa o `confere_links.py` da pasta dada com repositórios
inventados: arquivo e âncora que faltam, link com o texto em duas linhas, títulos
repetidos, título com código e com link, caminho com espaço (entre `<>` e codificado),
pasta, imagem, âncora em arquivo que não é Markdown, links externos, código na linha e
blocos de código de cercas diferentes, documento novo fora do git e documento que o
`.gitignore` deixa de fora; links para uma linha (a primeira, a última, depois da última, a
zero, com `l` minúsculo, num arquivo sem quebra no fim, num Markdown, no próprio documento,
numa pasta e com espaço) e links para um marcador (pelo `id`, pelo `name`, entre aspas
simples, sem aspas, com o atributo em maiúsculas, depois de outro atributo, pelo valor de
outro atributo, num texto sem tag, que falta, num bloco de código, no código da linha e num
comentário), dos quais confere quais dão erro; a mesma saída em duas rodadas; repositório
sem erro; pasta sem git. Precisa do git; só usa a biblioteca padrão.

    python3 -I <prateleira>/documentos/teste_confere_links.py <prateleira>/documentos <pasta de trabalho nova>

As cópias estragadas do `confere_links.py` estão em `estragos-confere-links.json`, nesta
pasta, para o [`estraga.py`](../copias-estragadas/README.md):

    python3 -I <prateleira>/copias-estragadas/estraga.py <prateleira>/documentos <prateleira>/documentos/teste_confere_links.py <prateleira>/documentos/estragos-confere-links.json <pasta de trabalho nova>
