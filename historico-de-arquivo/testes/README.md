# testes de historico-de-arquivo

    python3 -I teste_historico_de_arquivo.py <pasta de historico_de_arquivo.py> <pasta de trabalho nova> [--semente N]

Testa o `historico_de_arquivo.py` e o `transcricoes.py`, que lê as transcrições para ele.
Tudo é inventado e sorteado com uma semente, a 1 ou outra com `--semente`: o padrão do
nome e a codificação das transcrições, os nomes dos campos dos eventos e das ferramentas,
as sessões, os caminhos, as horas e os textos e, da saída, os nomes dos arquivos, os
rótulos, as marcas e a codificação. Nada é de um projeto real nem de um programa de verdade.

O teste confere o que o script faz, nunca uma frase pronta:

- acha cada uso de uma ferramenta da configuração no arquivo pedido, e só eles: nem o uso
  em outro arquivo, nem o de uma ferramenta que a configuração não tem, nem o bloco de
  outro tipo com os mesmos campos; nas transcrições da pasta e das subpastas cujo nome
  segue o padrão, e não no arquivo de outro nome; a pasta cujo nome segue o padrão não é
  lida como transcrição;
- pelo nome, acha os usos de um arquivo com esse nome em qualquer pasta, e não os de outro
  nome;
- lê as transcrições na codificação da configuração e grava a saída na dela;
- põe os achados na ordem do tempo, que as transcrições trazem embaralhada;
- cada achado traz a sessão, a hora, a ferramenta, o caminho, a transcrição e a linha, cada
  um depois do rótulo e do separador da configuração; os campos da entrada que a
  configuração diz, sob o título entre as marcas dela, o que não é texto em JSON, e nenhum
  outro; e, só na ferramenta que pede, o texto do resultado, dado em texto ou em lista de
  blocos, um bloco por linha, ou a marca de sem resultado, quando ele não vem;
- os arquivos dos achados têm a extensão da configuração, e a lista dos achados e a das
  linhas que não se leram, os nomes e os rótulos dela; nada mais é gravado;
- lista as linhas que não se leem, fora da codificação ou que não são objeto JSON, e não a
  linha em branco; o evento sem mensagem, a mensagem que não é objeto, o conteúdo que não é
  lista (texto ou número) e o bloco que não é objeto não quebram nada;
- a configuração com campo desconhecido, sem um dos campos que o script lê, com uma
  codificação que não existe (a das transcrições, numa pasta sem transcrição nenhuma), com
  dois arquivos da saída de mesmo nome ou com ferramentas de mesmo nome, e a pasta das
  transcrições que não existe dão erro e não criam a pasta de saída; o erro das
  ferramentas de mesmo nome diz o nome de cada uma; a pasta de saída que já existe dá erro
  e fica como estava;
- duas rodadas dão o mesmo.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas de `historico_de_arquivo.py` e de `transcricoes.py` estão em
`estragos.json`, nesta pasta, para o [`estraga.py`](../../copias-estragadas/README.md), com
a pasta do extrator ao lado da cópia:

    python3 -I ../../copias-estragadas/estraga.py .. teste_historico_de_arquivo.py estragos.json <pasta de trabalho nova> --irma ../../extrator
