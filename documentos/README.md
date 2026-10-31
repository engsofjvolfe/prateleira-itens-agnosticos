# documentos

Conferências dos documentos e do código de um repositório: as linhas que passam de um limite
de caracteres e os links internos dos documentos Markdown.

Usam a biblioteca padrão do Python e o `extrator_comum.py`, do
[extrator](../extrator/README.md), que lê os textos; na prateleira, ele é achado na pasta
irmã `extrator/`. O `confere_links.py` precisa também do git.

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

## Testes

Em [testes/](testes/README.md).
