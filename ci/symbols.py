"""Every shipped package answers `symbols` with the same schema; no model calls."""
from pathlib import Path
import json, subprocess, tempfile
BIN = Path(__file__).resolve().parents[1] / 'gramide'
FIXTURES = {
    'almd': ('fn real() -> Int = {\n  1\n}\n', 'real'),
    'go': ('package p\n\ntype Shape struct{ w int }\n\nfunc (s *Shape) Area() int { return s.w }\n', 'Shape.Area'),
    'rs': ('impl Box {\n #[inline]\n pub fn read(&self) -> i32 { 1 }\n}\n', 'Box::read'),
    'py': ('class Box:\n    def read(self) -> int: ...\n', 'Box.read'),
    'js': ('export class Box {\n  read() { return /re/.test(this.x) }\n}\n', 'Box.read'),
    'ts': ('export class Box<T> {\n  read(): T { return this.x as T }\n}\n', 'Box.read'),
}
with tempfile.TemporaryDirectory() as tmp:
    for ext, (source, name) in FIXTURES.items():
        path = Path(tmp) / ('sample.' + ext)
        path.write_text(source)
        doc = json.loads(subprocess.check_output([str(BIN), 'symbols', str(path)], text=True))
        assert doc['schema_version'] == 1 and doc['complete'] is True and doc['total_lines'] == source.count('\n'), doc
        names = [s['name'] for s in doc['symbols']]
        assert name in names, (ext, names)
        raw = source.encode()
        for s in doc['symbols']:
            assert set(s) >= {'kind', 'syntax_kind', 'name', 'owner', 'start', 'end', 'start_byte', 'end_byte'}, s
            assert 1 <= s['start'] <= s['end'] <= doc['total_lines'] and 0 <= s['start_byte'] < s['end_byte'] <= len(raw), s
            assert raw[s['start_byte']:s['end_byte']].strip(), s
        broken = Path(tmp) / ('broken.' + ext)
        broken.write_text(source + ')\n')
        p = subprocess.run([str(BIN), 'symbols', str(broken)], capture_output=True, text=True)
        assert p.returncode != 0 and not p.stdout, (ext, p.stdout, p.stderr)
print('Symbols schema passed: six packages, one contract, invalid input refused without JSON')
