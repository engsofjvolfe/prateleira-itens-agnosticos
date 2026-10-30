"""Testes do custo.py, com configuracao e transcricoes inventadas aqui: os nomes de todos os
campos, o padrao dos arquivos, o tamanho do comeco e os rotulos das colunas sao sorteados,
com letras de fora do ASCII, e os numeros de cada turno tambem. O teste calcula de novo, por
conta propria, o que cada linha da tabela tem de dizer e confere: o cabecalho com os
rotulos; uma linha por transcricao com alguma linha, na ordem do caminho, com o caminho a
partir da pasta (a da subpasta entra; a de fora do padrao e a vazia, nao); os turnos (so os
eventos com uso que e objeto), o maior contexto, o processado e a saida, com o campo que
falta, o texto e o booleano valendo 0; o comeco da primeira pergunta (nao de outro tipo de
evento, nem de pergunta sem texto), com os espacos juntados e cortado no tamanho; vazio
quando nao ha pergunta. A linha que nao e objeto JSON e a mensagem que nao e objeto ficam de
fora. Configuracao e pasta que nao servem saem com 2; duas rodadas dao o mesmo. Uso:
    python3 -I teste_custo.py <pasta do custo.py> <pasta de trabalho nova>
"""
import json
import random
import subprocess
import sys
from pathlib import Path

PECA, TRABALHO = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
SCRIPT = PECA / "custo.py"
FALHAS = []
SORTEIO = random.Random(5)
LETRAS = "abcdefghijklmnop" + "áçõüéñ"  # com letras de fora do ASCII


def confere(condicao, descricao):
    if not condicao:
        FALHAS.append(descricao)
    return condicao


def palavra():
    return "".join(SORTEIO.choice(LETRAS) for _ in range(SORTEIO.randint(4, 9)))


def frase(n):
    return " ".join(palavra() for _ in range(n))


def nomes(n):
    """n nomes sorteados, todos diferentes."""
    saida = []
    while len(saida) < n:
        nome = palavra()
        if nome not in saida:
            saida.append(nome)
    return saida


TIPO, PERGUNTA, OUTRO_TIPO, MENSAGEM, CONTEUDO, USO, SAIDA, E1, E2, E3 = nomes(10)
ENTRADA = [E1, E2, E3]
EXTENSAO = palavra()
LETRAS_DO_COMECO = SORTEIO.randint(8, 20)
ROTULOS = nomes(6)
CONFIGURACAO = {
    "versao_schema": 1,
    "transcricoes": {"padrao": f"*.{EXTENSAO}", "codificacao": "utf-8"},
    "eventos": {"tipo": TIPO, "pergunta": PERGUNTA, "mensagem": MENSAGEM, "conteudo": CONTEUDO, "uso": USO},
    "uso": {"entrada": ENTRADA, "saida": SAIDA},
    "comeco": {"letras": LETRAS_DO_COMECO},
    "colunas": dict(zip(["transcricao", "turnos", "contexto_maximo", "processado", "saida", "comeco"], ROTULOS)),
}


def grava_configuracao(dados):
    caminho = TRABALHO / f"{palavra()}.json"
    caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return caminho


def evento(tipo=None, conteudo=None, uso=None, mensagem=True):
    corpo = {}
    if conteudo is not None:
        corpo[CONTEUDO] = conteudo
    if uso is not None:
        corpo[USO] = uso
    saida = {TIPO: tipo or OUTRO_TIPO, MENSAGEM: corpo if mensagem else frase(2)}
    return json.dumps(saida, ensure_ascii=False)


def uso_sorteado():
    return {**{c: SORTEIO.randint(0, 9000) for c in ENTRADA}, SAIDA: SORTEIO.randint(0, 900)}


def esperado(usos):
    """(turnos, contexto maximo, processado, saida) calculados aqui, com o que nao e numero inteiro valendo 0."""
    def n(u, c):
        v = u.get(c, 0)
        return v if isinstance(v, int) and not isinstance(v, bool) else 0
    contextos = [sum(n(u, c) for c in ENTRADA) for u in usos]
    saidas = [n(u, SAIDA) for u in usos]
    return len(usos), max(contextos, default=0), sum(contextos) + sum(saidas), sum(saidas)


TRABALHO.mkdir(parents=True)
PASTA = TRABALHO / palavra()
(PASTA / palavra()).mkdir(parents=True)
SUBPASTA = next(PASTA.iterdir())
ESPERADO = {}

# transcricao com quase todos os casos
curta = "".join(SORTEIO.choice(LETRAS) for _ in range(3))  # a quebra e a tabulacao vem antes do corte
pergunta = f"{curta}\n\t {frase(4)}  {frase(3)}"
usos = [uso_sorteado(), dict(uso_sorteado(), **{E2: palavra(), E3: True}), {E1: SORTEIO.randint(1, 99)}, uso_sorteado()]
linhas = ["{" + palavra(), "[1, 2]", evento(conteudo=frase(5)), evento(PERGUNTA, conteudo=pergunta, uso=usos[0]),
          "", evento(uso=usos[1]), evento(PERGUNTA, conteudo=frase(3), uso=usos[2]), evento(mensagem=False),
          evento(uso=[1, 2]), evento(uso=usos[3])]
A = PASTA / f"{palavra()}.{EXTENSAO}"
A.write_text("\n".join(linhas) + "\n", encoding="utf-8")
ESPERADO[A] = esperado(usos) + (" ".join(pergunta.split())[:LETRAS_DO_COMECO],)

# na subpasta: pergunta sem texto antes da que tem
usos_b = [uso_sorteado() for _ in range(SORTEIO.randint(1, 4))]
pergunta_b = frase(6)
B = SUBPASTA / f"{palavra()}.{EXTENSAO}"
B.write_text("\n".join([evento(PERGUNTA, conteudo=[frase(2)])] + [evento(uso=u) for u in usos_b]
                       + [evento(PERGUNTA, conteudo=pergunta_b)]) + "\n", encoding="utf-8")
ESPERADO[B] = esperado(usos_b) + (" ".join(pergunta_b.split())[:LETRAS_DO_COMECO],)

# sem pergunta nenhuma
usos_c = [uso_sorteado()]
C = PASTA / f"{palavra()}.{EXTENSAO}"
C.write_text(evento(uso=usos_c[0]) + "\n", encoding="utf-8")
ESPERADO[C] = esperado(usos_c) + ("",)

# fora do padrao e vazia: nao aparecem
(PASTA / f"{palavra()}.{palavra()}").write_text(evento(PERGUNTA, conteudo=frase(3), uso=uso_sorteado()) + "\n",
                                                 encoding="utf-8")
(PASTA / f"{palavra()}.{EXTENSAO}").write_text("", encoding="utf-8")


def roda(configuracao, pasta):
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), str(configuracao), str(pasta)],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout


CONF = grava_configuracao(CONFIGURACAO)
codigo, saida = roda(CONF, PASTA)
tabela = [l.split("\t") for l in saida.rstrip("\n").split("\n")]
confere(codigo == 0, f"sai com 0: {codigo}, {saida}")
confere(tabela[0] == ROTULOS, f"o cabeçalho são os rótulos, na ordem: {tabela[:1]}")
ordem = sorted(ESPERADO)
confere([l[0] for l in tabela[1:]] == [p.relative_to(PASTA).as_posix() for p in ordem],
        f"uma linha por transcrição com alguma linha, na ordem e com o caminho a partir da pasta: {tabela[1:]}")
for caminho, linha in zip(ordem, tabela[1:]):
    turnos, maximo, processado, saida_ = ESPERADO[caminho][:4]
    numeros = [str(turnos), str(maximo), str(processado), str(saida_)]
    confere(linha[1:5] == numeros,
            f"{caminho.name}: turnos, contexto máximo, processado e saída: {linha[1:5]} != {numeros}")
    confere(linha[5:] == [ESPERADO[caminho][4]], f"{caminho.name}: o começo da primeira pergunta: {linha[5:]}")
confere(roda(CONF, PASTA)[1] == saida, "duas rodadas dão o mesmo")


def com(caminho, valor):
    """Uma copia da configuracao com o valor no caminho ("a/b"); None tira o campo."""
    dados = json.loads(json.dumps(CONFIGURACAO))
    alvo, partes = dados, caminho.split("/")
    for parte in partes[:-1]:
        alvo = alvo[parte]
    if valor is None:
        del alvo[partes[-1]]
    else:
        alvo[partes[-1]] = valor
    return grava_configuracao(dados)


ESTRAGADAS = {
    "campo que o molde não conhece": com(palavra(), palavra()),
    "campo que falta": com("uso/saida", None),
    "tamanho negativo": com("comeco/letras", -1),
    "tamanho que não é número": com("comeco/letras", "9"),
    "entrada vazia": com("uso/entrada", []),
    "entrada que não é nome": com("uso/entrada", [1]),
    "codificação que não existe": com("transcricoes/codificacao", palavra()),
    "rótulo que falta": com("colunas/comeco", None),
}
for nome, caminho in ESTRAGADAS.items():
    codigo, saida = roda(caminho, PASTA)
    confere(codigo == 2, f"configuração com {nome} sai com 2: {codigo}, {saida}")
codigo, _ = roda(CONF, TRABALHO / palavra())
confere(codigo == 2, f"pasta que não existe sai com 2: {codigo}")

for f in FALHAS:
    print("FALHA:", f)
print(f"{len(FALHAS)} falha(s)")
sys.exit(1 if FALHAS else 0)
