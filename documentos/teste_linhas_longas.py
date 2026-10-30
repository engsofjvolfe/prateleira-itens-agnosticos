"""Confere que nenhuma linha passa do limite de caracteres: em cada arquivo dado e, numa
pasta, em cada arquivo dela e das subpastas cujo nome segue o padrao. Mostra
arquivo:linha (tamanho) de cada linha acima do limite, em ordem, e sai com codigo 0
quando nenhuma passa. Uso:
    python3 -I teste_linhas_longas.py <limite> <padrao do nome> <arquivo ou pasta>...
Por exemplo: 120 "*.py" scripts
"""
import sys
from pathlib import Path

if len(sys.argv) < 4:
    raise SystemExit(__doc__)
limite, padrao, alvos = int(sys.argv[1]), sys.argv[2], [Path(a) for a in sys.argv[3:]]
for alvo in alvos:
    if not alvo.exists():
        raise SystemExit(f"não existe: {alvo}")
arquivos = sorted({a for alvo in alvos for a in (alvo.rglob(padrao) if alvo.is_dir() else [alvo]) if a.is_file()})
falhas = [f"{arquivo}:{n} ({len(linha)})"
          for arquivo in arquivos
          for n, linha in enumerate(arquivo.read_text(encoding="utf-8").split("\n"), 1)
          if len(linha) > limite]
print("\n".join(falhas) or f"nenhuma linha passa de {limite} caracteres")
sys.exit(1 if falhas else 0)
