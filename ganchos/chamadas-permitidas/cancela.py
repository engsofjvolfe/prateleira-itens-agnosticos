"""Gancho que so deixa rodar a chamada de ferramenta que uma regra da lista permite, menos a
das ferramentas livres.

Le o evento pela entrada padrao, em JSON, pelo protocolo do programa que roda o gancho
(--protocolo). A chamada de uma ferramenta livre passa. A de outra passa so quando roda da
pasta principal (--raiz) e o campo da entrada que a configuracao diz para a ferramenta bate
inteiro com a forma, uma expressao regular, de uma regra da lista (--regras) que vale para
aquela ferramenta; a forma pode usar, como <<nome>>, uma das partes com nome que a lista
guarda, para que um pedaco repetido fique num lugar so. A regra vale quando o trecho da
fonte dela esta no arquivo da fonte e, se ela pede, quando o texto que ela monta com as
partes nomeadas da forma esta no arquivo que ela diz. O resto e barrado, com o motivo e o
codigo de --barra-com, como o evento.py faz: nenhuma regra que bata, e as que perderam a
fonte. O protocolo, a configuracao (--config), a lista ou o evento fora da forma tambem
barram. A lista e lida pelo molde dela, em esquemas/, com o extrator_comum.py, do extrator,
que o evento.py poe no caminho de importacao. Os caminhos que nao sao absolutos partem da
pasta principal. So biblioteca padrao.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # os modulos da peca, que o python -I nao poe no caminho
import evento  # noqa: E402
from extrator_comum import ErroDeDados, compila, le_conferido, le_texto  # noqa: E402 -- no caminho do evento.py

DOCUMENTADA = "documentada"  # a chave que a regra pode ter a mais
CHAVES_DA_DOCUMENTADA = ("arquivo", "texto")
PARTE = re.compile(r"<<([a-z_]+)>>")  # como uma forma usa uma parte com nome


def aberta(forma, partes, onde):
    """A forma, compilada, com cada <<nome>> trocado pela parte de mesmo nome, entre
    parenteses que nao guardam o que acham; o nome que nao e de uma parte e erro."""
    def troca(achado):
        if achado.group(1) not in partes:
            raise ErroDeDados(f"{onde}: a parte {achado.group(1)!r} não está nas partes da lista")
        return f"(?:{partes[achado.group(1)]})"
    return compila(PARTE.sub(troca, forma), onde)


def le_partes(valor, onde):
    """As partes com nome, cada uma uma expressao regular, com o nome na forma que as formas
    usam."""
    for nome, parte in valor.items():
        if not PARTE.fullmatch(f"<<{nome}>>"):
            raise ErroDeDados(f"{onde}: nome de parte fora da forma: {nome!r}")
        compila(parte, f"{onde}/{nome}")
    return valor


def le_regras(caminho):
    """As regras da lista, lida pelo molde dela, cada uma com a forma aberta pelas partes e
    compilada, sem dois nomes iguais."""
    valor = le_conferido(caminho, evento.MOLDES / "regras.schema.json")
    partes = le_partes(valor["partes"], f"{caminho}: partes")
    regras = [dict(regra, forma=aberta(regra["forma"], partes, f"{caminho}: regras/{k}/forma"))
              for k, regra in enumerate(valor["regras"])]
    nomes = [r["nome"] for r in regras]
    repetidos = sorted({nome for nome in nomes if nomes.count(nome) > 1})
    if repetidos:
        raise ErroDeDados(f"{caminho}: nome de regra repetido: {repetidos}")
    return regras


def tem(raiz, arquivo, texto):
    """Se o arquivo tem o texto; o arquivo que nao se le nao tem."""
    caminho = Path(arquivo).expanduser()
    try:
        return texto in le_texto(caminho if caminho.is_absolute() else raiz / caminho)
    except ErroDeDados:
        return False


def documentada(raiz, valor, achada):
    """Se a regra que pede o texto montado com as partes nomeadas da forma o acha no arquivo
    que ela diz; a regra que nao pede, sempre."""
    if DOCUMENTADA not in valor:
        return True
    partes = {nome: parte or "" for nome, parte in achada.groupdict().items()}
    try:
        arquivo, texto = (valor[DOCUMENTADA][chave].format(**partes) for chave in CHAVES_DA_DOCUMENTADA)
    except (KeyError, IndexError, ValueError) as erro:
        raise ErroDeDados(f"regra {valor['nome']}: {DOCUMENTADA} pede uma parte que a forma não nomeia ({erro})")
    return tem(raiz, arquivo, texto)


def motivo(config, regras, raiz, partes):
    """None quando a chamada de uma ferramenta que nao e livre pode rodar; senao, o motivo de
    barra-la."""
    ferramenta = partes["ferramenta"]
    if Path(partes["pasta"]).resolve() != raiz:
        return f"a chamada roda em {partes['pasta']}, e não na pasta principal {raiz}"
    campo = config["campos"].get(ferramenta)
    if campo is None:
        return f"nenhuma regra da lista pode permitir a ferramenta {ferramenta!r}: a configuração não diz o campo dela"
    valor = partes["entrada"].get(campo)
    if not isinstance(valor, str):
        return f"a entrada não tem o texto {campo!r}, que as regras conferem"
    da_ferramenta, sem_fonte = [], []
    for candidata in regras:
        if candidata["ferramenta"] != ferramenta:
            continue
        da_ferramenta.append(candidata["nome"])
        if not tem(raiz, candidata["fonte"]["arquivo"], candidata["fonte"]["trecho"]):
            sem_fonte.append(candidata["nome"])
            continue
        achada = candidata["forma"].fullmatch(valor)
        if achada and documentada(raiz, candidata, achada):
            return None
    texto = f"nenhuma regra da lista permite esta chamada; as regras de {ferramenta!r} são {da_ferramenta}"
    return texto + (f"; perderam a fonte na documentação: {sem_fonte}" if sem_fonte else "")


def main(argumentos=None):
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    leitor.add_argument("--protocolo", required=True, type=Path, help="o protocolo do programa que roda o gancho")
    leitor.add_argument("--config", required=True, type=Path, help="a configuração da peça")
    leitor.add_argument("--regras", required=True, type=Path, help="JSON com a lista das regras do projeto")
    leitor.add_argument("--raiz", required=True, type=Path, help="a pasta principal do projeto")
    leitor.add_argument("--barra-com", required=True, type=int,
                        help="o código de saída com que o programa não roda a chamada")
    args = leitor.parse_args(argumentos)

    def trabalho():
        config = evento.ler_configuracao(args.config)
        partes = evento.chamada(evento.ler_protocolo(args.protocolo), sys.stdin.read())
        # antes da lista: uma lista quebrada nunca barra a livre que a conserta
        if partes["ferramenta"] in config["livres"]:
            return None
        return motivo(config, le_regras(args.regras), args.raiz.resolve(), partes)

    evento.guarda(trabalho, "chamada barrada", args.barra_com)


if __name__ == "__main__":
    main()
