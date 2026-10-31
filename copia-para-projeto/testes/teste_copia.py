"""Testes do copia.py, com uma peca e um projeto inventados aqui: arquivos de codigo com a
extensao do script de referencia e outros, um script de referencia com um cabecalho de
comentario de tamanho sorteado e um sinal de comentario inventado. Conferem regras, nunca
uma frase pronta: a copia do arquivo de codigo e o cabecalho do script de referencia mais
o arquivo da peca, e a dos outros e o arquivo da peca; o destino e o dado; com
--conferir, nada e gravado, as copias em dia passam e a copia mudada e acusada, pelo nome;
sem cabecalho no script de referencia, a copia e o arquivo como esta; o arquivo da peca ou
o script de referencia que nao existe, o par sem destino e o sinal de comentario vazio sao
erro, que sai com codigo 2, sem gravar nada; duas rodadas dao o mesmo. Uso:
    python3 -I teste_copia.py <pasta do copia.py> <pasta de trabalho nova>
Precisa do grava_ou_confere.py e do extrator_comum.py, nas pastas irmas da peca.
"""
import random
import string
import subprocess
import sys
from pathlib import Path

PECA_COPIA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
FALHAS = []
SORTEIO = random.Random(1)


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def texto(linhas=5):
    return "\n".join("".join(SORTEIO.choice(string.ascii_letters + " ") for _ in range(30)) for _ in range(linhas))


SINAL, EXT = "%%", ".cod"  # um sinal de comentario e uma extensao inventados
PECA, PROJETO = TRABALHO / "peca", TRABALHO / "projeto"
ARQUIVOS = {f"prog{EXT}": texto(), f"sub/outro{EXT}": texto(), "dados/molde.json": texto(2)}
for nome, conteudo in ARQUIVOS.items():
    (PECA / nome).parent.mkdir(parents=True, exist_ok=True)
    (PECA / nome).write_text(conteudo, encoding="utf-8")
CABECA = [f"{SINAL} {texto(1)}" for _ in range(SORTEIO.randint(1, 3))]
REFERENCIA = PROJETO / "codigo" / f"ref{EXT}"
REFERENCIA.parent.mkdir(parents=True)
REFERENCIA.write_text("\n".join(CABECA) + "\n\n" + texto(), encoding="utf-8")
SEM_CABECA = PROJETO / "codigo" / f"sem{EXT}"
SEM_CABECA.write_text(texto(), encoding="utf-8")
DESTINOS = {f"prog{EXT}": f"codigo/prog{EXT}", f"sub/outro{EXT}": f"codigo/outro{EXT}",
            "dados/molde.json": "codigo/moldes/molde.json"}
PARES = [f"{o}={d}" for o, d in DESTINOS.items()]


def roda(*args, referencia=REFERENCIA, projeto=PROJETO, sinal=SINAL):
    r = subprocess.run([sys.executable, "-I", str(PECA_COPIA / "copia.py"), str(PECA), str(projeto), str(referencia),
                        *args, "--comentario", sinal], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def esperado(origem, cabeca):
    return (cabeca if origem.endswith(EXT) else "") + ARQUIVOS[origem]


cod, out = roda(*PARES)
cabeca = "\n".join(CABECA) + "\n\n"
confere(cod == 0, f"a cópia sai com 0: {out}")
for origem, destino in DESTINOS.items():
    feito = (PROJETO / destino).read_text(encoding="utf-8") if (PROJETO / destino).is_file() else None
    confere(feito == esperado(origem, cabeca), f"{origem}: a cópia vai para o destino dado, com o cabeçalho só no "
                                               f"arquivo com a extensão do script de referência")
primeira = {d: (PROJETO / d).read_bytes() for d in DESTINOS.values()}
roda(*PARES)
confere({d: (PROJETO / d).read_bytes() for d in DESTINOS.values()} == primeira, "duas rodadas dão o mesmo")

cod, out = roda(*PARES, "--conferir")
confere(cod == 0, f"com as cópias em dia, --conferir sai com 0: {out}")
mudado = PROJETO / DESTINOS[f"prog{EXT}"]
if confere(mudado.is_file(), f"a cópia está no destino dado: {mudado}"):
    mudado.write_text(mudado.read_text(encoding="utf-8") + "x", encoding="utf-8")
    antes = mudado.read_bytes()
    cod, out = roda(*PARES, "--conferir")
    diferentes = [l for l in out.split("\n") if l.startswith(str(PROJETO)) and "em dia" not in l]
    confere(cod == 1 and len(diferentes) == 1 and diferentes[0].startswith(str(mudado)),
            f"--conferir acusa a cópia mudada, e só ela: {out}")
    confere(mudado.read_bytes() == antes, "--conferir não grava nada")

outro = TRABALHO / "projeto-sem-cabecalho"
cod, out = roda(*PARES, referencia=SEM_CABECA, projeto=outro)
confere(cod == 0 and all((outro / d).read_text(encoding="utf-8") == ARQUIVOS[o] for o, d in DESTINOS.items()),
        f"sem cabeçalho no script de referência, a cópia é o arquivo como está: {out}")

ERROS = [("arquivo da peça que não existe", PARES + [f"nao-existe{EXT}=codigo/x{EXT}"], {}),
         ("par sem destino", PARES + [f"prog{EXT}"], {}),
         ("script de referência que não existe", PARES, {"referencia": PROJETO / "codigo" / f"nao-existe{EXT}"}),
         ("sinal de comentário vazio", PARES, {"sinal": ""})]
for numero, (descricao, pares, opcoes) in enumerate(ERROS):
    vazio = TRABALHO / f"projeto-com-erro-{numero}"
    cod, out = roda(*pares, projeto=vazio, **opcoes)
    confere(cod == 2 and out.startswith("ERRO") and not vazio.exists(),
            f"{descricao} é erro, que sai com 2, sem gravar nada: {out}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
