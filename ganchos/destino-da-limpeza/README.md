# destino-da-limpeza

Gancho que guarda o arquivo para onde uma limpeza leva o que tira de outros arquivos, como
um registro do que a memória de trabalho deixou de usar. Esse arquivo, o destino, só recebe
o que sai das origens, e nunca muda o que já tem:

- **Antes de escrever num arquivo de origem**: a escrita que tira ou muda texto que estava
  lá fica anotada, para a sessão. A origem nunca é bloqueada.
- **Antes de escrever no destino**: passa só a escrita que faz o destino crescer, com o
  texto novo entre blocos (separado deles por uma linha em branco), e só depois de sair
  texto de uma origem na mesma resposta. É bloqueada a escrita que muda ou tira uma linha,
  a que gruda texto num bloco ou o põe no meio dele, a que chega sem nada saído e a da
  ferramenta que o gancho não sabe ler. A escrita que não muda nada passa.
- **Antes de um comando de terminal**: o comando que tem o nome do destino é bloqueado.
- **Ao encerrar a resposta**: a anotação some; a resposta seguinte começa sem nada saído.

Quando algo dá errado ao conferir (a configuração fora do molde, um aviso que não se lê,
uma entrada que não se lê), a escrita ou o comando que nomeia o destino é bloqueado, com o
erro no motivo; o resto sai com o erro. Com o protocolo que não se lê, não há como
responder, e o gancho só sai com o erro. O gancho só lê o destino e as origens: a escrita é
da ferramenta.

Pode barrar a mais, nunca a menos. Ele não lê o sentido do texto: garante quando o destino
recebe texto e que o que ele tem fica como está, não que o texto novo seja o que saiu da
origem.

Usa só a biblioteca padrão do Python, o `extrator_comum.py`, do
[extrator](../../extrator/README.md), que lê a configuração pelo molde dela, e o
[protocolo](../protocolo/README.md), da pasta irmã, que lê o protocolo do programa que roda
o gancho; o extrator é achado duas pastas acima (na prateleira) ou na pasta irmã (numa cópia
de teste).

## Como rodar

O programa que roda os ganchos chama este antes de cada chamada das ferramentas que
escrevem arquivo e da de terminal, e no fim de cada resposta, e manda o evento pela entrada
padrão, em JSON:

    python3 -I <prateleira>/ganchos/destino-da-limpeza/destino_da_limpeza.py \
        --config <configuração.json> --protocolo <protocolo.json> --destino <arquivo> --origem <arquivo ou pasta> \
        --aviso-muda <texto> --aviso-sem-origem <texto> --aviso-terminal <texto>

- `--protocolo`: o protocolo do programa, na forma do [protocolo](../protocolo/README.md):
  dele vêm o evento, a resposta que nega, a ferramenta de terminal, com o campo do comando,
  e as escritas: os campos do caminho, as ferramentas que trocam um trecho e as que gravam o
  arquivo inteiro.
- `--destino`: o arquivo guardado; pode repetir.
- `--origem`: um arquivo, ou uma pasta com tudo o que há dentro dela, de onde a limpeza
  tira texto; pode repetir.
- `--aviso-muda`, `--aviso-sem-origem` e `--aviso-terminal`: os textos dos bloqueios — o
  destino não cresceu só entre blocos; nada saiu de uma origem; o terminal nomeou o
  destino —, como os desta pasta.

O destino, as origens e os textos são do projeto e ficam no comando que o programa roda. A
resposta sai pela saída padrão, em JSON, só quando bloqueia.

## A configuração

O molde está em `esquemas/destino-da-limpeza.schema.json`. O caminho da pasta parte da
pasta da configuração. A `configuracao.json` desta pasta é a de uso geral.

| Chave | O que é |
| --- | --- |
| `versao_schema` | a versão do molde |
| `estado` | a pasta das anotações, uma por sessão, com o nome tirado do id da sessão |

## Os textos

- `muda.md`: o destino não cresceu só entre blocos.
- `sem-origem.md`: nada saiu de uma origem na mesma resposta.
- `terminal.md`: o terminal nomeou o destino.

## Testes

Em [testes/](testes/README.md).
