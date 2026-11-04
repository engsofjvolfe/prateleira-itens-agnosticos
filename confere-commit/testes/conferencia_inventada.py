"""Uma conferencia inventada, para o teste do confere_commit.py: grava num registro JSON o que recebeu (os
arquivos, a pasta em que rodou, o texto de cada arquivo e os arquivos que o git da nela) e sai com o codigo dado.

Uso:
    python3 -I conferencia_inventada.py <registro.json> <codigo> [<arquivo>...]
"""
import json
import subprocess
import sys
from pathlib import Path

registro, codigo, *arquivos = sys.argv[1:]
do_git = subprocess.run(["git", "ls-files", "-z"], capture_output=True)
Path(registro).write_text(json.dumps({
    "pasta": str(Path.cwd().resolve()),
    "arquivos": arquivos,
    "textos": {arquivo: Path(arquivo).read_text(encoding="utf-8") for arquivo in arquivos},
    "do_git": sorted(p for p in do_git.stdout.decode("utf-8").split("\0") if p) if do_git.returncode == 0 else None,
}, ensure_ascii=False), encoding="utf-8")
print(f"{len(arquivos)} arquivo(s)")
sys.exit(int(codigo))
