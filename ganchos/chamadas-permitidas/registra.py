"""Gancho que grava num registro cada chamada de ferramenta antes de ela rodar, menos a das
ferramentas que a configuracao deixa fora dele.

Le o evento pela entrada padrao, em JSON, pelo protocolo do programa que roda o gancho
(--protocolo), e poe no fim do registro (--registro) a linha da chamada, na forma do
registro.py: a sessao, a ferramenta e a entrada inteira dela. A chamada de uma ferramenta de
fora passa sem linha. A chamada que nao se consegue gravar nao roda: com o protocolo, a
configuracao (--config), o evento ou o registro com problema, o gancho diz o erro e sai com
o codigo de --barra-com, como o evento.py faz. So biblioteca padrao.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # os modulos da peca, que o python -I nao poe no caminho
import evento  # noqa: E402
import registro  # noqa: E402


def main(argumentos=None):
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    leitor.add_argument("--protocolo", required=True, type=Path, help="o protocolo do programa que roda o gancho")
    leitor.add_argument("--config", required=True, type=Path, help="a configuração da peça")
    leitor.add_argument("--registro", required=True, type=Path, help="o arquivo onde cada chamada ganha uma linha")
    leitor.add_argument("--barra-com", required=True, type=int,
                        help="o código de saída com que o programa não roda a chamada")
    args = leitor.parse_args(argumentos)

    def trabalho():
        config = evento.ler_configuracao(args.config)
        partes = evento.chamada(evento.ler_protocolo(args.protocolo), sys.stdin.read())
        if partes["ferramenta"] not in config["fora_do_registro"]:
            linha = registro.linha(partes["sessao"], partes["ferramenta"], partes["entrada"])
            registro.acrescenta(args.registro, linha)
        return None

    evento.guarda(trabalho, f"a chamada não foi registrada em {args.registro} e não roda", args.barra_com)


if __name__ == "__main__":
    main()
