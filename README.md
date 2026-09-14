# gramide-cli

The `gramide` command: syntax trees for coding agents, written in
[Almide](https://github.com/almide/almide). `gramide` turns a source file into a tree an agent can ask questions of: does this
file still parse, where does each declaration start and end, what is this node's
name. A grammar is an ordinary value in the language, the parser interprets it, and
there is no generator step and no native library between the agent and the tree.

[日本語](README_ja.md)

```
gramide check   src/main.almd     exit 0 if it parses, else `file:line:col: unexpected X (expected …)`
gramide check   src/*.almd        any number of files: each grammar is read once, not once per file
gramide outline src/main.almd     one line per declaration: `L12-40 function parse`, and a method
                                  named with its type: `L82-89 method Applicability::as_str`
                                  a file that does not parse still gets an outline of the parts that do
gramide symbols src/main.almd     versioned JSON names, owners, line and byte ranges (strict parse)
gramide symbols-recovered a.py    the same over a recovered parse, where a package offers it
gramide parse   src/main.almd     the whole tree as an s-expression
gramide tags    src/main.almd     `def function parse L40-58`, `ref call list.map L44`, `ref type Node L12` — a repo map's input
gramide balance Widget.java       delimiters and literals only, for a language with no grammar here:
                                  it cannot see a missing semicolon, and it cannot reject valid code
gramide tokens  src/main.almd     the token stream, one per line
gramide map . --budget 1024 --task "fix parse_rule"
                                  a ranked map of the repository within the token budget:
                                  the definitions other files use most, personalised toward
                                  what the task mentions — what an agent reads before opening files
gramide languages                 the packages this binary ships, as JSON
gramide version                   what it was built from: the binary, the engine, each package
```

## Why

An agent that edits code needs two things from a parser: a fast, honest answer to
"did I just break the file", and a map of what is where so it can read only the part
it needs. It does not need a full compiler front end, and it should not need a
different native library for each language it touches. gramide is the smallest thing
that gives an agent those two answers, in the same language the agent's tools are
written in, so a grammar can be read, patched and tested like any other module.

## How it is put together

This repository is one file: the binary that composes every language package.
The engine and each language live in repositories of their own, the way
tree-sitter is a runtime, one repository per grammar, and `tree-sitter-cli`.

| package | what it is | |
|---|---|---|
| [gramide](https://github.com/O6lvl4/gramide) | the engine: lexer, parser, tree, readers, the command line as a library, and the package contract | `gramide` |
| gramide-cli | this repository: the binary, `gramide` on `PATH` | `gramide_cli` |
| [gramide-almide](https://github.com/O6lvl4/gramide-almide) | Almide `.almd` | `gramide_almide` |
| [gramide-go](https://github.com/O6lvl4/gramide-go) | Go `.go` | `gramide_go` |
| [gramide-rust](https://github.com/O6lvl4/gramide-rust) | Rust `.rs` | `gramide_rust` |
| [gramide-python](https://github.com/O6lvl4/gramide-python) | Python 3.14 `.py` `.pyi` | `gramide_python` |

Each language package holds its lexer, its grammar as a value, that grammar
compiled and committed as a table, the rules that say which of its nodes declare
a name, its tests, its oracles against the language's own reference parser, and
a small binary of its own — `gramide_go` is `gramide` over Go alone — so the
package is tested, measured and released without the others. What each one
covers, on which corpus, is in its README.

`src/main.almd` here lists the four and hands them to the engine. Adding a
language is one line there and one in `almide.toml`; a binary that ships only
the languages a project uses is the same file with a shorter list. Almide links
statically, which is why the composition is a file and not a loader.

## Install

```
almide install github.com/O6lvl4/gramide-cli --name gramide      # one native binary → ~/.local/bin/gramide
```

`--name` because Almide names a binary after its package, and the package is
`gramide_cli`. From a checkout, `almide build --release -o gramide` writes
`./gramide`, fetching the engine and the four language packages at the
commits `almide.lock` records. Requires Almide 0.62 or
later. [hew](https://github.com/O6lvl4/hew) finds `gramide` on `PATH` and reads
code through it.

## Status

Four packages ship. The guarantee each establishes runs one way: **a file
gramide rejects is broken for the language's reference parser too**, measured
on that language's corpus and recorded in its repository — every `.almd` file
in the Almide repository, every `.go` file under `GOROOT/src`, every `.rs`
file in the Almide compiler, and 645 Python declarations across 12 complete
standard-library files checked against CPython's own AST. Each grammar is more
permissive than its compiler in a few known places, listed in its README.
Python is also the package that offers `symbols-recovered`, the contract hew
uses to read a file that is halfway through being edited.

Whole-corpus `check`, eight byte-balanced slices of the file list in parallel:
4,105 `.almd` files in **0.118 s** (42 MB/s), and every `.go` file under
`GOROOT/src` — 7,702 files, 90.2 MB — in **0.695 s** (130 MB/s). The engine's
design and every measurement behind it are in
[gramide](https://github.com/O6lvl4/gramide/blob/main/docs/design.md). Splitting
the packages cost nothing: against the last monolithic build, this binary is
16% smaller and equal or faster on every command with byte-identical output
([evidence](docs/evidence/split-comparison.json)). Against tree-sitter, fresh
process and startup included: a structured read of 800 Go functions takes
5.4 ms to its 5.9, Python's `inspect.py` 7.2 ms to its 10.8, and the whole
Python standard library parses at 0.60x its time; what still loses is a file
of a few kilobytes, by the 0.2 ms of Rust runtime a C binary does not pay
([the board](https://github.com/O6lvl4/gramide/blob/main/bench/README.md)).

## Checks

`bash ci/check.sh` builds the binary and runs the cross-language smoke test,
the package discovery contract (`gramide languages`) and the `symbols` schema
contract over all four packages ([ci/README.md](ci/README.md)). Everything
about one language is checked in that language's repository.

## License

MIT or Apache-2.0, at your option.
