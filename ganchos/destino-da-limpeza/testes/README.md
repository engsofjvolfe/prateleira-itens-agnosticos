# testes de destino-da-limpeza

    python3 -I teste_destino_da_limpeza.py <pasta de destino_da_limpeza.py> <pasta de trabalho nova> [--semente N]

Tudo é inventado: os textos dos avisos, a pasta das anotações, os nomes e o que tem cada
arquivo de destino e de origem, sorteado sempre igual, porque a semente é fixa (outra
semente vem com `--semente`); e o protocolo do programa que roda o gancho, sorteado pelo
[`protocolo_inventado.py`](../../protocolo/testes/protocolo_inventado.py) (os eventos, as
chaves e as respostas), com a ferramenta de terminal, os campos do caminho, uma ferramenta
que troca um trecho e uma que grava o arquivo inteiro. Nada é de um projeto real.

O teste confere o que o gancho faz, nunca uma frase pronta:

- no destino, passa a escrita que só cresce, entre blocos, depois de sair texto de uma
  origem na mesma resposta, pela troca de uma vez, pela troca de todas e pela escrita
  inteira; é bloqueada, na resposta que nega, com o texto do aviso e o caminho, a que muda
  ou tira uma linha, a que gruda texto num bloco ou o põe no meio dele e a da ferramenta que
  o gancho não sabe ler; e a que chega sem nada saído, com o texto e as origens;
- só conta como saída a escrita que tira ou muda texto de um arquivo de origem, ou de um
  arquivo dentro de uma pasta de origem; a que só acrescenta, a de fora das origens e a da
  ferramenta que o gancho não sabe ler não contam;
- o fim da resposta apaga a anotação, que fica na pasta da configuração; cada sessão tem a
  sua, e o id da sessão nunca vira caminho;
- o caminho por atalho ou com `..` é o mesmo arquivo;
- a escrita que não muda nada passa, e a troca que não se aplica também;
- no terminal, o comando com o nome do destino é bloqueado, e o resto passa;
- com a configuração fora do molde ou sem um campo, o aviso que não existe, a entrada que
  não é JSON, o evento desconhecido, a ferramenta sem campo de caminho ou a sessão sem id, o
  que nomeia o destino, mesmo escrito como no JSON, é bloqueado com o erro, e o resto sai
  com erro; o protocolo fora da forma e a falta da opção de um aviso saem com erro;
- o gancho nunca escreve no destino nem nas origens, e a mesma entrada dá a mesma saída.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas de `destino_da_limpeza.py` estão em `estragos.json`, nesta pasta,
para o [`estraga.py`](../../../copias-estragadas/README.md), com o extrator e o protocolo ao
lado da cópia:

    python3 -I ../../../copias-estragadas/estraga.py .. teste_destino_da_limpeza.py estragos.json \
        <pasta de trabalho nova> --irma ../../../extrator --irma ../../protocolo
