"""
Prova que o teste de uma peca pega os defeitos: para cada estrago da lista, copia a peca
para uma pasta nova, troca nela um texto de um arquivo pelo texto estragado e roda o teste
contra a copia. O estrago e pego quando o teste falha (sai com codigo diferente de 0).

A lista e um JSON com o molde esquemas/estragos.schema.json: cada estrago com o "nome", o
"arquivo" (o caminho dentro da peca), o texto "de", que tem de aparecer uma vez so no
arquivo, e o texto "para". Campo que o molde nao conhece, ou que falta, e erro. Precisa
do extrator_comum.py, do extrator, na pasta irma "extrator" ou na mesma pasta.

Com --so <campo>=<valor>, so rodam os estragos que tem esse valor nesse campo, como
nome=sem-irma ou arquivo=calculo.py, na ordem da lista; pode repetir, e rodam os que batem
com qualquer um. O --so sem o sinal, ou que nao bate com nenhum estrago, e erro.

O teste recebe a pasta da copia, os argumentos de --antes, se houver, e uma pasta de
trabalho nova, nessa ordem. Com --irma, essa pasta e copiada ao lado da copia da peca, com
o mesmo nome, sem a pasta testes/ dela: e para a peca que acha outra na pasta irma. Pode
repetir; duas pastas com o mesmo nome sao erro. A peca original nunca e mudada. Com erro na
lista ou nas opcoes, nada roda.

Mostra uma linha por estrago (pego, nao pego ou o erro) e, no fim, quantos foram pegos.
Sai com codigo 0 so quando todos sao pegos.

Uso:
    python3 -I estraga.py <peca> <teste.py> <lista.json> <pasta de trabalho nova>
        [--so <campo>=<valor>]... [--irma <pasta>]... [--antes <arg>]...
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
for pasta in (PASTA.parent / "extrator", PASTA):  # na prateleira, o extrator fica na pasta irma
    sys.path.insert(0, str(pasta))
from extrator_comum import ErroDeDados, le_conferido  # noqa: E402

MOLDE = PASTA / "esquemas" / "estragos.schema.json"  # o molde da lista
SINAL = "="  # entre o campo e o valor, em --so


def roda(estrago, a, trabalho):
    """(pego: True, False ou None, quando o estrago nao se aplica; o que mostrar)."""
    pasta = trabalho / estrago["nome"]
    copia = pasta / "peca"
    shutil.copytree(a.peca, copia, ignore=shutil.ignore_patterns("__pycache__"))
    for irma in a.irma:
        shutil.copytree(irma, pasta / irma.name, ignore=shutil.ignore_patterns("__pycache__", "testes"))
    alvo = copia / estrago["arquivo"]
    texto = alvo.read_text(encoding="utf-8")
    if texto.count(estrago["de"]) != 1:
        return None, f"ERRO: o texto a estragar aparece {texto.count(estrago['de'])} vez(es) em {estrago['arquivo']}"
    alvo.write_text(texto.replace(estrago["de"], estrago["para"]), encoding="utf-8")
    r = subprocess.run([sys.executable, "-I", "-B", a.teste, str(copia), *a.antes, str(pasta / "t")],
                       capture_output=True, text=True)
    ultima = ((r.stdout + r.stderr).strip().split("\n") or [""])[-1][:200]
    pego = r.returncode != 0
    return pego, f"{'pego' if pego else 'NÃO PEGO'} (o teste saiu com {r.returncode}: {ultima})"


def escolhidos(estragos, filtros):
    """Os estragos que batem com algum filtro <campo>=<valor>, na ordem da lista; todos, sem
    filtro. O filtro sem o sinal, ou que nao bate com nenhum estrago, e erro."""
    pares = []
    for filtro in filtros:
        campo, sinal, valor = filtro.partition(SINAL)
        if not sinal:
            raise ErroDeDados(f"--so {filtro}: falta o {SINAL} entre o campo e o valor")
        if not any(e.get(campo) == valor for e in estragos):
            raise ErroDeDados(f"--so {filtro}: nenhum estrago da lista tem esse valor nesse campo")
        pares.append((campo, valor))
    return [e for e in estragos if not pares or any(e.get(c) == v for c, v in pares)]


def nomes_repetidos(pastas):
    """Os nomes que mais de uma das pastas tem, em ordem."""
    nomes = [p.name for p in pastas]
    return sorted({n for n in nomes if nomes.count(n) > 1})


def main(argv=None):
    p = argparse.ArgumentParser(description="Prova que o teste de uma peça pega os defeitos de uma lista.")
    p.add_argument("peca", type=Path)
    p.add_argument("teste")
    p.add_argument("lista", type=Path)
    p.add_argument("trabalho", type=Path)
    p.add_argument("--so", action="append", default=[],
                   help="<campo>=<valor>: só os estragos com esse valor nesse campo (pode repetir)")
    p.add_argument("--irma", action="append", default=[], type=Path,
                   help="pasta copiada ao lado da cópia da peça (pode repetir)")
    p.add_argument("--antes", action="append", default=[], help="argumento do teste antes da pasta de trabalho")
    a = p.parse_args(argv)
    try:
        estragos = escolhidos(le_conferido(a.lista, MOLDE)["estragos"], a.so)
        repetidos = nomes_repetidos(a.irma)
        if repetidos:
            raise ErroDeDados(f"--irma: mais de uma pasta com o nome {', '.join(repetidos)}")
    except ErroDeDados as e:
        print(f"ERRO: {e}")
        return 1
    if a.trabalho.exists() and any(a.trabalho.iterdir()):
        print(f"ERRO: a pasta de trabalho precisa estar vazia: {a.trabalho}")
        return 1
    pegos = 0
    for estrago in estragos:
        pego, texto = roda(estrago, a, a.trabalho)
        pegos += bool(pego)
        print(f"{estrago['nome']}: {texto}", flush=True)
    print(f"{pegos} de {len(estragos)} estrago(s) pego(s)")
    return 0 if pegos == len(estragos) else 1


if __name__ == "__main__":
    sys.exit(main())
