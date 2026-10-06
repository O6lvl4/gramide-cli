# Reproducible composition checks

Run `bash ci/check.sh` with Almide installed, or set `ALMIDE_BIN` to its absolute
path. The CLI reads the engine and fourteen independent grammar repositories at
the commits pinned in `almide.lock`; it contains no grammar source.

The checks run the explicit CLI test root, build the native binary, retain the
seven established-definition smoke checks, verify all fifteen manifest entries
and capability boundaries, and exercise the common strict-symbols schema across
all fifteen definitions. A malformed file must not emit complete symbol JSON.

Each grammar repository owns its scanner/grammar tests, generated-table check,
source corpus, byte-range checks and applicable reference-parser oracle. New core
readers deliberately omit `check` and `symbols-recovered`; JSON adds syntax check.
No full-language or tree-sitter-parity claim follows from composition tests.

The existing Quality workflow pins Almide to
`dff9a458f2e581631bb6537c856a7974036e4153` and Rust to `1.94.0`.

The current lockfile selects merged engine parent-window/node-identity fixes,
JSON missing-closer recovery, and Java qualified `TypeName.this` parsing. The
engine uses an exact main-branch commit because the v0.2.11 tag predates those
fixes. Opt-in paired-head recovery remains in separate draft PRs and is not
selected by these pins.
