"""Testes do chamadas-permitidas, com tudo inventado: a configuracao, as ferramentas, as
sessoes, as entradas, as regras, as fontes delas, as pastas e o codigo que barra; e o
protocolo do programa que roda os ganchos, sorteado (os eventos, as chaves e as respostas).
Nada e de um projeto real.

    python3 -I teste_chamadas_permitidas.py <pasta da peca> <pasta de trabalho nova>

O teste confere o que a peca faz, nunca uma frase pronta dela, menos o nome inventado de uma
regra e a chave inventada de uma parte do evento no motivo do bloqueio. Diz "0 falha(s)"
quando passa; senao, uma linha FALHA para cada conferencia que nao passou, e sai com o
codigo 1. O protocolo inventado vem do protocolo_inventado.py, da pasta de testes do
protocolo.
"""
import json
import random
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "protocolo" / "testes"))
import protocolo_inventado  # noqa: E402

SORTE = random.Random(13)
VERSAO = 1  # a versao dos moldes da configuracao e da lista, pelo README
BARRA_COM = SORTE.randint(3, 120)  # o codigo que barra, longe dos de erro do Python (1) e dos argumentos (2)
LINHA = ("sessao", "ferramenta", "entrada")  # as chaves de uma linha do registro, pelo README
FORA = ["so-olha", "so-escreve"]
LIVRES = ["so-olha"]
CAMPOS = {"roda-x": "linha"}
DENTRO = ["roda-x", "acha-y"]
SESSOES = ["sessao-um", "sessao-dois"]
PARALELAS = 16  # chamadas ao mesmo tempo
GRANDE = 200_000  # caracteres de uma entrada, grande para que gravacoes ao mesmo tempo possam se cruzar
PROTOCOLO = protocolo_inventado.inventado(SORTE, {"ferramenta": "roda-x", "campo_comando": "linha"})
CHAVES = PROTOCOLO["chaves"]

falhas = []


def confere(condicao, descricao):
    if not condicao:
        falhas.append(descricao)


def escreve_json(caminho, valor):
    caminho.write_text(json.dumps(valor, ensure_ascii=False), encoding="utf-8")
    return caminho


def roda(peca, script, argumentos, entrada="", protocolo=None):
    """O gancho, com o protocolo (o dado, ou o inventado, gravado ao lado da peca de trabalho) e o codigo que barra."""
    protocolo = protocolo or ARQUIVO_DO_PROTOCOLO
    return subprocess.run([sys.executable, "-I", str(peca / script), "--protocolo", str(protocolo),
                           "--barra-com", str(BARRA_COM), *map(str, argumentos)], input=entrada,
                          capture_output=True, text=True, encoding="utf-8")


def config_valida():
    return {"versao_schema": VERSAO, "fora_do_registro": list(FORA), "livres": list(LIVRES), "campos": dict(CAMPOS)}


def evento(ferramenta, entrada, sessao=SESSOES[0], nome=None, pasta="/", sem=None):
    """O texto JSON de um evento de antes de uma chamada, pelo protocolo inventado; com nome, o
    evento desse nome; com sem, sem a chave dessa parte."""
    valor = {CHAVES["evento"]: nome or PROTOCOLO["eventos"]["antes"], CHAVES["sessao"]: sessao,
             CHAVES["ferramenta"]: ferramenta, CHAVES["entrada"]: entrada, CHAVES["pasta"]: pasta}
    if sem is not None:
        del valor[CHAVES[sem]]
    return json.dumps(valor, ensure_ascii=False)


def linhas_de(caminho):
    return caminho.read_text(encoding="utf-8").splitlines() if caminho.exists() else []


# ---- o registro ----

def testa_registro(peca, trabalho):
    config = escreve_json(trabalho / "config.json", config_valida())
    reg = trabalho / "registro.jsonl"
    grava = lambda texto, c=config, r=reg: roda(peca, "registra.py", ["--config", c, "--registro", r], texto)

    primeira = {"comando": "procura algo\ncom duas linhas", "nota": "ação"}
    r = grava(evento(DENTRO[0], primeira))
    linhas = linhas_de(reg)
    confere(r.returncode == 0 and r.stdout == "", f"chamada de dentro: código {r.returncode}, saída {r.stdout!r}")
    confere(len(linhas) == 1, f"chamada de dentro: {len(linhas)} linha(s) no registro, e não 1")
    if linhas:
        confere(json.loads(linhas[0]) == dict(zip(LINHA, (SESSOES[0], DENTRO[0], primeira))),
                f"linha gravada: {linhas[0]!r}")

    grava(evento(DENTRO[1], {"padrao": "x"}, sessao=SESSOES[1]))
    depois = linhas_de(reg)
    confere(len(depois) == 2 and depois[:1] == linhas[:1], "a segunda chamada não ficou no fim, depois da primeira")

    r = grava(evento(FORA[1], {"arquivo": "z"}))
    confere(r.returncode == 0 and linhas_de(reg) == depois, "a chamada de uma ferramenta de fora mudou o registro")

    grava(evento(DENTRO[0], primeira))
    grava(evento(DENTRO[0], primeira))
    final = linhas_de(reg)
    confere(len(final) == 4 and final[2] == final[3] == depois[0], "a mesma chamada não deu a mesma linha")


def testa_bloqueios_do_registro(peca, trabalho):
    reg = trabalho / "bloqueio.jsonl"
    reg.write_text("", encoding="utf-8")
    boa = config_valida()

    def bloqueia(descricao, texto, config=boa, registro_=reg, protocolo=None, diz=""):
        caminho = config if isinstance(config, Path) else escreve_json(trabalho / "config-bloqueio.json", config)
        r = roda(peca, "registra.py", ["--config", caminho, "--registro", registro_], texto, protocolo)
        confere(r.returncode == BARRA_COM and r.stderr.strip() and diz in r.stderr,
                f"{descricao}: código {r.returncode}, erro {r.stderr!r}, que tem de dizer {diz!r}")
        confere(reg.read_text(encoding="utf-8") == "", f"{descricao}: o registro mudou")

    entrada = {"comando": "w"}
    bloqueia("entrada que não é JSON", "{ não é json")
    bloqueia("evento que não é objeto", json.dumps([1, 2]))
    bloqueia("evento de outro nome", evento(DENTRO[0], entrada, nome="outro-evento"))
    bloqueia("evento de fim", evento(DENTRO[0], entrada, nome=PROTOCOLO["eventos"]["fim"]))
    bloqueia("evento sem a chave do nome", evento(DENTRO[0], entrada, sem="evento"))
    for parte in ("sessao", "ferramenta", "entrada", "pasta"):
        bloqueia(f"evento sem a chave de {parte}", evento(DENTRO[0], entrada, sem=parte), diz=CHAVES[parte])
    bloqueia("entrada que não é objeto", evento(DENTRO[0], "texto solto"))
    bloqueia("sessão vazia", evento(DENTRO[0], entrada, sessao=""))
    bloqueia("pasta que não é texto", evento(DENTRO[0], entrada, pasta=3))
    bloqueia("ferramenta que não é texto", evento(7, entrada))
    bloqueia("configuração com chave a mais", evento(DENTRO[0], entrada), {**boa, "outra": 1})
    bloqueia("configuração de outra versão", evento(DENTRO[0], entrada), {**boa, "versao_schema": VERSAO + 1})
    for chave in boa:
        bloqueia(f"configuração sem {chave}", evento(DENTRO[0], entrada), {k: v for k, v in boa.items() if k != chave})
    # uma lista escrita como texto deixaria de fora toda ferramenta cujo nome esta dentro dele
    bloqueia("ferramentas de fora num texto", evento(FORA[0][:2], entrada), {**boa, "fora_do_registro": FORA[0]})
    bloqueia("ferramenta de fora vazia", evento(DENTRO[0], entrada), {**boa, "fora_do_registro": [""]})
    bloqueia("livres num texto", evento(DENTRO[0], entrada), {**boa, "livres": LIVRES[0]})
    bloqueia("campos que não são objeto", evento(DENTRO[0], entrada), {**boa, "campos": ["linha"]})
    bloqueia("campo vazio", evento(DENTRO[0], entrada), {**boa, "campos": {DENTRO[0]: ""}})
    torta = trabalho / "torta.json"
    torta.write_text("{", encoding="utf-8")
    bloqueia("configuração que não é JSON", evento(DENTRO[0], entrada), torta)
    bloqueia("ferramenta de fora com a configuração quebrada", evento(FORA[0], entrada), torta)
    sem_sessao = {**PROTOCOLO, "chaves": {k: v for k, v in CHAVES.items() if k != "sessao"}}
    bloqueia("protocolo sem uma chave", evento(DENTRO[0], entrada),
             protocolo=escreve_json(trabalho / "protocolo-sem-sessao.json", sem_sessao))
    bloqueia("protocolo que não é JSON", evento(DENTRO[0], entrada), protocolo=torta)
    bloqueia("registro numa pasta que não existe", evento(DENTRO[0], entrada), boa, trabalho / "nao-ha" / "r.jsonl")


def testa_paralelas(peca, trabalho):
    config = escreve_json(trabalho / "config-paralela.json", config_valida())
    reg = trabalho / "paralelas.jsonl"
    entradas = [{"comando": str(k) * GRANDE} for k in range(PARALELAS)]
    with ThreadPoolExecutor(max_workers=PARALELAS) as grupo:
        list(grupo.map(lambda e: roda(peca, "registra.py", ["--config", config, "--registro", reg],
                                      evento(DENTRO[0], e)), entradas))
    lidas = []
    for linha in linhas_de(reg):
        try:
            lidas.append(json.loads(linha)["entrada"])
        except (json.JSONDecodeError, KeyError, TypeError):
            lidas.append(None)
    confere(sorted(map(json.dumps, lidas)) == sorted(map(json.dumps, entradas)),
            "chamadas ao mesmo tempo misturaram ou perderam linhas")


# ---- a cancela ----

def testa_cancela(peca, trabalho):
    raiz, outra = trabalho / "raiz", trabalho / "outra"
    raiz.mkdir()
    outra.mkdir()
    (raiz / "regras-inventadas.md").write_text("Para achar, escreva: procura -x ALGO.\nOutra linha.\n",
                                               encoding="utf-8")
    (raiz / "leiame.md").write_text("## `rodar.py`\nroda assim.\n", encoding="utf-8")
    absoluta = trabalho / "fonte-de-fora.md"
    absoluta.write_text("vale também: mostra TUDO\n", encoding="utf-8")
    ferramenta, campo = next(iter(CAMPOS.items()))
    sem_campo = next(f for f in DENTRO if f not in CAMPOS)
    regras = {"versao_schema": VERSAO, "partes": {"palavra": "[a-z]+"}, "regras": [
        {"nome": "procura", "ferramenta": ferramenta, "forma": r"procura -x <<palavra>> <<palavra>>\.txt",
         "fonte": {"arquivo": "regras-inventadas.md", "trecho": "procura -x ALGO"}},
        {"nome": "rodar", "ferramenta": ferramenta, "forma": r"rodar (?P<nome>[a-z_]+\.py)",
         "fonte": {"arquivo": "regras-inventadas.md", "trecho": "Outra linha"},
         "documentada": {"arquivo": "leiame.md", "texto": "## `{nome}`"}},
        {"nome": "mostra", "ferramenta": ferramenta, "forma": "mostra tudo",
         "fonte": {"arquivo": str(absoluta), "trecho": "mostra TUDO"}},
        {"nome": "perdida", "ferramenta": ferramenta, "forma": "perdida",
         "fonte": {"arquivo": "regras-inventadas.md", "trecho": "um trecho que o arquivo não tem"}},
        {"nome": "de-outra", "ferramenta": sem_campo, "forma": ".*",
         "fonte": {"arquivo": "regras-inventadas.md", "trecho": "Outra linha"}}]}
    config = escreve_json(trabalho / "config.json", config_valida())
    lista = escreve_json(trabalho / "regras.json", regras)
    certa = "procura -x abc dados.txt"

    def tenta(nome, entrada, pasta=raiz, lista_=lista, config_=config):
        return roda(peca, "cancela.py", ["--config", config_, "--regras", lista_, "--raiz", raiz],
                    evento(nome, entrada, pasta=str(pasta)))

    def passa(descricao, r):
        confere(r.returncode == 0 and r.stdout == "" and r.stderr == "",
                f"{descricao}: código {r.returncode}, erro {r.stderr!r}")

    def barra(descricao, r, *nomes):
        confere(r.returncode == BARRA_COM and r.stderr.strip() and all(n in r.stderr for n in nomes),
                f"{descricao}: código {r.returncode}, erro {r.stderr!r}")

    passa("chamada que bate com uma regra", tenta(ferramenta, {campo: certa}))
    passa("regra com a fonte num caminho absoluto", tenta(ferramenta, {campo: "mostra tudo"}))
    passa("regra documentada no arquivo que ela diz", tenta(ferramenta, {campo: "rodar rodar.py"}))
    passa("pasta principal escrita com ..", tenta(ferramenta, {campo: certa}, pasta=raiz / ".." / raiz.name))
    passa("ferramenta livre, de qualquer pasta e com qualquer entrada", tenta(LIVRES[0], {"x": 1}, pasta=outra))
    barra("regra documentada num texto que o arquivo não tem", tenta(ferramenta, {campo: "rodar outro.py"}))
    barra("chamada que bate só no começo", tenta(ferramenta, {campo: certa + "; mais"}))
    barra("chamada que não bate", tenta(ferramenta, {campo: certa.upper()}))
    barra("regra que perdeu a fonte", tenta(ferramenta, {campo: "perdida"}), "perdida")
    barra("chamada fora da pasta principal", tenta(ferramenta, {campo: certa}, pasta=outra))
    barra("ferramenta sem campo, mesmo com regra", tenta(sem_campo, {campo: certa}))
    barra("ferramenta que ainda não existe", tenta("nova-z", {campo: certa}))
    barra("entrada sem o campo", tenta(ferramenta, {"outro": certa}))
    barra("campo que não é texto", tenta(ferramenta, {campo: [certa]}))

    primeira, partes = regras["regras"][0], regras["partes"]
    tortas = {"lista com chave a mais": {**regras, "x": 1},
              "lista de outra versão": {**regras, "versao_schema": VERSAO + 1},
              "lista sem as partes": {"versao_schema": VERSAO, "regras": regras["regras"]},
              "regra sem fonte": {**regras, "regras": [{k: v for k, v in primeira.items() if k != "fonte"}]},
              "regra com chave a mais": {**regras, "regras": [{**primeira, "x": 1}]},
              "forma que não é expressão": {**regras, "regras": [{**primeira, "forma": "procura ("}]},
              "forma com uma parte que não existe": {**regras,
                                                     "regras": [{**primeira, "forma": "procura -x <<nada>>"}]},
              "parte que não é expressão": {**regras, "partes": {"palavra": "("}, "regras": [primeira]},
              "parte com nome fora da forma": {**regras, "partes": {**partes, "Outra": "x"}, "regras": [primeira]},
              "partes numa lista": {**regras, "partes": ["[a-z]+"], "regras": [primeira]},
              "nome repetido": {**regras, "regras": [primeira, primeira]},
              "fonte sem trecho": {**regras,
                                   "regras": [{**primeira, "fonte": {"arquivo": "regras-inventadas.md"}}]},
              "documentada sem texto": {**regras,
                                        "regras": [{**primeira, "documentada": {"arquivo": "leiame.md"}}]},
              "regras num texto": {**regras, "regras": "procura"}}
    for k, (descricao, torta) in enumerate(tortas.items()):
        caminho = escreve_json(trabalho / f"torta-{k}.json", torta)
        barra(f"lista com {descricao}", tenta(ferramenta, {campo: certa}, lista_=caminho))
        passa(f"ferramenta livre com a lista com {descricao}", tenta(LIVRES[0], {"x": 1}, lista_=caminho))
    quebrada = trabalho / "quebrada.json"
    quebrada.write_text("{", encoding="utf-8")
    barra("lista que não é JSON", tenta(ferramenta, {campo: certa}, lista_=quebrada))
    barra("configuração que não é JSON", tenta(ferramenta, {campo: certa}, config_=quebrada))
    sem_parte = {**regras,
                 "regras": [{**regras["regras"][1], "documentada": {"arquivo": "leiame.md", "texto": "## `{outra}`"}}]}
    barra("documentada que pede uma parte que a forma não nomeia",
          tenta(ferramenta, {campo: "rodar rodar.py"}, lista_=escreve_json(trabalho / "sem-parte.json", sem_parte)))


def main():
    global ARQUIVO_DO_PROTOCOLO
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    peca, trabalho = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    trabalho.mkdir(parents=True, exist_ok=True)
    if any(trabalho.iterdir()):
        sys.exit(f"a pasta de trabalho tem de ser nova: {trabalho}")
    ARQUIVO_DO_PROTOCOLO = escreve_json(trabalho / "protocolo.json", PROTOCOLO)
    for teste in (testa_registro, testa_bloqueios_do_registro, testa_paralelas, testa_cancela):
        pasta = trabalho / teste.__name__
        pasta.mkdir()
        teste(peca, pasta)
    for falha in falhas:
        print(f"FALHA: {falha}")
    print(f"{len(falhas)} falha(s)")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
