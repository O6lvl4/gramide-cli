"""Exercise the built CLI without network or model credentials."""
from pathlib import Path
import subprocess
import tempfile

BIN = Path(__file__).resolve().parents[1] / "gramide"

def run(*args, code=0):
    p = subprocess.run([str(BIN), *map(str, args)], capture_output=True, text=True, timeout=30)
    assert p.returncode == code, (args, p.returncode, p.stdout, p.stderr)
    return p.stdout

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    for ext, text in {
        "py": "def real(): return 1\n",
        "rs": "fn real() { let value = 1; }\n",
        "go": "package main\nfunc real() {}\n",
        "almd": "fn real() -> Int = 1\n",
        "js": "export function real() { return /re/.test(x) }\n",
        "ts": "export function real<T>(x: T): T { return x }\n",
        "jsx": "export function real() { return <p>{x}</p> }\n",
        "tsx": "export function real<T>({ x }: { x: T }) { return <Box<T> x={x} /> }\n",
    }.items():
        source = root / ("valid." + ext)
        source.write_text(text)
        run("check", source)
        assert "real" in run("outline", source)
        broken = root / ("broken." + ext)
        broken.write_text(text + "}\n")
        run("check", broken, code=1)
print("CLI smoke passed: outlines and syntax rejection across all seven definitions")
