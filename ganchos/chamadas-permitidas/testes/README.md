# testes de chamadas-permitidas

    python3 -I teste_chamadas_permitidas.py <pasta da peça> <pasta de trabalho nova>

Tudo é inventado: a configuração, as ferramentas, as sessões, as entradas, as regras, as
fontes delas, as pastas e o código que barra, sorteado longe dos códigos de erro do Python e
dos argumentos; e o protocolo do programa que roda os ganchos, sorteado pelo
[`protocolo_inventado.py`](../../protocolo/testes/protocolo_inventado.py) (os eventos, as
chaves e as respostas). Nada é de um projeto real.

O teste confere o que a peça faz, nunca uma frase pronta dela, menos o nome inventado de uma
regra e a chave inventada de uma parte do evento no motivo do bloqueio:

- o registro põe no fim a linha de cada chamada de dentro, com a sessão, a ferramenta e a
  entrada inteira, também a que tem quebra de linha, numa linha só; a chamada de fora não muda
  o registro; a mesma chamada dá a mesma linha;
- a chamada não roda, sai com o código que barra e o registro fica como estava, com a
  entrada que não é JSON, o evento que não é objeto, de outro nome, o de fim ou sem uma das
  chaves (e o motivo diz a chave que falta), a entrada que não é objeto, a sessão vazia, a
  pasta ou a ferramenta que não são texto, a configuração que não é JSON, com chave a mais
  ou a menos, de outra versão, com uma lista de ferramentas escrita como texto ou com um
  nome vazio, com os campos que não são objeto ou com um campo vazio, também para uma
  ferramenta de fora, o protocolo sem uma chave ou que não é JSON, e o registro numa pasta
  que não existe;
- chamadas grandes ao mesmo tempo dão uma linha inteira cada uma, sem mistura nem perda;
- a cancela deixa passar a chamada que bate inteira com a forma de uma regra que vale, também
  a forma que usa uma parte com nome, com a fonte por caminho relativo à pasta principal ou
  absoluto, a regra documentada no arquivo que ela diz e a pasta principal escrita com `..`; e
  a ferramenta livre, de qualquer pasta, com qualquer entrada e com a lista quebrada;
- a cancela barra, com o código que barra, a chamada que bate só no começo ou que não bate, a
  da regra documentada num texto que o arquivo não tem, a da regra que perdeu a fonte, com o
  nome dela no motivo, a que roda fora da pasta principal, a da ferramenta sem campo, mesmo
  com regra, a da ferramenta que ainda não existe, a entrada sem o campo ou com o campo que
  não é texto, a lista fora da forma (que não é JSON, de outra versão, com chave a mais, sem
  as partes, regra sem fonte ou com chave a mais, forma que não é expressão regular ou que
  usa uma parte que não existe, parte que não é expressão regular ou com nome fora da forma,
  partes numa lista, nome repetido, fonte sem trecho, documentada sem texto, regras num
  texto), a configuração que não é JSON e a documentada que pede uma parte que a forma não
  nomeia.

Diz `0 falha(s)` quando passa; senão, uma linha `FALHA` para cada conferência que não passou,
e sai com código 1.

As cópias estragadas da peça estão em `estragos.json`, nesta pasta, para o
[`estraga.py`](../../../copias-estragadas/README.md), com o protocolo e o extrator ao lado da
cópia:

    python3 -I <prateleira>/copias-estragadas/estraga.py <pasta da peça> \
        <pasta da peça>/testes/teste_chamadas_permitidas.py <pasta da peça>/testes/estragos.json \
        <pasta de trabalho nova> --irma <prateleira>/ganchos/protocolo --irma <prateleira>/extrator

---

*Este documento está licenciado sob [CC BY-NC-SA 4.0](../../../LICENSE-CONTENT.txt).*
