# testes de protocolo

    python3 -I teste_protocolo.py <pasta do protocolo.py> <pasta de trabalho nova> [--semente N]

Tudo é inventado e sorteado, sempre igual, porque a semente é fixa (outra semente vem com
`--semente`): os nomes dos eventos, as chaves, os modelos das respostas, as ferramentas e os
campos de cada uma, com letras de fora do ASCII. Nada é de um programa de verdade.

O teste confere o que o módulo faz, nunca uma frase pronta:

- o protocolo lido dá os eventos pelo nome no programa, as chaves, os modelos, a
  ferramenta de terminal, as de busca, os campos das escritas, as de leitura, com os
  números, e as que resumem; as listas de ferramentas vazias e os menores números de uma
  leitura passam;
- o evento lido dá `antes` ou `fim` e cada parte que ele traz, e só elas; o evento sem o
  nome, com outro nome, com o nome que não é texto ou noutra chave, que não é objeto ou que
  não é JSON é erro;
- cada resposta é uma cópia do modelo dela com o texto no lugar de `{texto}`, em todo texto
  de dentro dele, também nas listas e nos objetos de dentro, com as chaves e o que não é
  texto como estão; o texto entra como é, com chaves, aspas, barra e quebra de linha; o
  modelo não muda;
- a anotação de uma sessão fica na pasta dada, com o nome de 64 algarismos hexadecimais, a
  mesma para a mesma sessão e outra para outra; o id com nome de caminho nunca sai da pasta;
  a sessão sem id, vazia ou que não é texto, é erro;
- a anotação de uma chave fica na pasta da sessão, com o nome de 64 algarismos
  hexadecimais, a mesma para a mesma chave e outra para outra chave ou outra sessão; duas
  chaves dão uma pasta dentro da outra, na ordem delas; a chave com nome de caminho nunca
  sai da pasta da sessão; a chave que não é texto é erro;
- é erro, com o que ou onde na mensagem: a versão que não é a do molde; campo desconhecido,
  que falta, de outro tipo ou vazio, também numa ferramenta de uma lista ou numa troca; os
  dois eventos com o mesmo nome; duas partes com a mesma chave; nenhum campo de caminho de
  escrita; a ferramenta repetida numa lista; o modelo sem `{texto}`, com outro campo ou que
  não é objeto; o número de uma leitura abaixo do menor;
- duas leituras e duas respostas dão o mesmo.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não
passou, e sai com código 1.

As cópias estragadas de `protocolo.py` estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../../copias-estragadas/README.md), com o extrator ao lado da cópia:

    python3 -I ../../../copias-estragadas/estraga.py .. teste_protocolo.py estragos.json <pasta de trabalho nova> --irma ../../../extrator

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../../LICENSE-CONTENT.txt).*
