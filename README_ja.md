# gramide-cli

`gramide` コマンド。コーディングエージェントのための構文木で、[Almide](https://github.com/almide/almide)
で書かれています。`gramide` はソースファイルを、エージェントが問い合わせられる木にします。このファイルはまだパースできるか、
各宣言はどこから始まりどこで終わるか、このノードの名前は何か。文法は言語の普通の値で、パーサはそれを
解釈します。生成ステップも、エージェントと木の間に挟まるネイティブライブラリもありません。

[English](README.md)

```
gramide check   src/main.almd     パースできれば exit 0、失敗なら `file:line:col: unexpected X (expected …)`
gramide check   src/*.almd        ファイルは何個でも: 文法を読むのはファイルごとではなく一度だけ
gramide outline src/main.almd     宣言ごとに一行: `L12-40 function parse`。メソッドは型付きで
                                  `L82-89 method Applicability::as_str`
                                  パースできないファイルでも、読めた部分のアウトラインは出る
gramide symbols src/main.almd     名前・所有者・行と byte の範囲をバージョン付き JSON で（厳密パース）
gramide symbols-recovered a.py    同じものを回復パースの上で。対応するパッケージだけ
gramide parse   src/main.almd     木全体を S 式で
gramide tags    src/main.almd     `def function parse L40-58`、`ref call list.map L44`、`ref type Node L12` — リポジトリマップの入力
gramide balance Widget.java       括弧とリテラルだけ。文法のない言語向け:
                                  セミコロン抜けは見えないが、正しいコードを拒否することもない
gramide tokens  src/main.almd     トークン列を一行ずつ
gramide map . --budget 1024 --task "fix parse_rule"
                                  トークン予算内に収めたリポジトリの地図: 他ファイルから最も使われる定義を、
                                  タスクが言及するものへ寄せて順位付け — エージェントがファイルを開く前に読むもの
gramide languages                 このバイナリが出荷するパッケージを JSON で
gramide version                   何から作られたか: バイナリ、エンジン、各パッケージ
```

## なぜ

コードを編集するエージェントがパーサに求めるものは二つです。「いま壊したか」への速くて正直な答えと、
必要な部分だけ読むための「何がどこにあるか」の地図。コンパイラのフロントエンド全体は要らないし、
触る言語ごとに別のネイティブライブラリを要求すべきでもありません。gramide はその二つの答えを、
エージェントのツールと同じ言語で返す最小のものです。文法を他のモジュールと同じように読み、直し、
テストできます。

## 構成

このリポジトリは 1 ファイルです。全言語パッケージを合成するバイナリ。エンジンと各言語は
それぞれ独立したリポジトリにあります。tree-sitter がランタイム、文法ごとのリポジトリ、そして
`tree-sitter-cli` からなるのと同じ形です。

| パッケージ | 内容 | |
|---|---|---|
| [gramide](https://github.com/O6lvl4/gramide) | エンジン: 字句解析・パーサ・木・読み手・ライブラリとしてのコマンドライン・パッケージ契約 | `gramide` |
| gramide-cli | このリポジトリ: バイナリ。`PATH` 上の `gramide` | `gramide_cli` |
| [gramide-almide](https://github.com/O6lvl4/gramide-almide) | Almide `.almd` | `gramide_almide` |
| [gramide-go](https://github.com/O6lvl4/gramide-go) | Go `.go` | `gramide_go` |
| [gramide-rust](https://github.com/O6lvl4/gramide-rust) | Rust `.rs` | `gramide_rust` |
| [gramide-python](https://github.com/O6lvl4/gramide-python) | Python 3.14 `.py` `.pyi` | `gramide_python` |

各言語パッケージは、字句解析器、値としての文法、その文法をコンパイルしてコミットした表、
どのノードが名前を宣言するかの規則、テスト、その言語の参照パーサに対するオラクル、そして
自前の小さなバイナリ（`gramide_go` は Go だけの `gramide`）を持ちます。だから他の言語なしに
テスト・計測・リリースできます。何をどのコーパスでカバーしているかは各 README にあります。

ここの `src/main.almd` は 4 つを列挙してエンジンに渡すだけ。言語を足すのはそこに 1 行と
`almide.toml` に 1 行。あるプロジェクトが使う言語だけを出荷するバイナリは、同じファイルの
リストを短くしたものです。Almide は静的リンクなので、合成はローダではなくファイルです。

## インストール

```
almide install github.com/O6lvl4/gramide-cli --name gramide      # ネイティブバイナリ 1 つ → ~/.local/bin/gramide
```

`--name` が要るのは、Almide がバイナリをパッケージ名で名付け、パッケージ名が `gramide_cli`
だからです。チェックアウトからは `almide build --release -o gramide` で `./gramide` ができます。
エンジンと 4 つの言語パッケージは `almide.lock` が記録するコミットで取得されます。Almide 0.62 以降が必要です。
[hew](https://github.com/O6lvl4/hew) は `PATH` 上の `gramide` を見つけてコードを読みます。

## 現状

4 パッケージを出荷しています。各パッケージが立てる保証は一方向です。**gramide が拒否する
ファイルは、その言語の参照パーサにとっても壊れている。** それぞれの言語のコーパスで計測し、
各リポジトリに記録しています。Almide リポジトリの全 `.almd`、`GOROOT/src` 配下の全 `.go`、
Almide コンパイラの全 `.rs`、そして標準ライブラリ 12 ファイル完全版を含む 645 の Python 宣言を
CPython 自身の AST と照合。各文法は既知の数箇所でコンパイラより寛容で、一覧は各 README に
あります。Python は `symbols-recovered`（編集途中のファイルを hew が読むための契約）を提供する
パッケージでもあります。

コーパス全体の `check`（ファイル一覧を byte 量で 8 分割して並列）: `.almd` 4,105 ファイルが
**0.118 秒**（42 MB/s）、`GOROOT/src` の `.go` 全 7,702 ファイル・90.2 MB が **0.695 秒**
（130 MB/s）。エンジンの設計とその背後の全計測は
[gramide](https://github.com/O6lvl4/gramide/blob/main/docs/design.md) にあります。パッケージ分割の
代償はありません。分割前の最後のモノリスと比べて、このバイナリは 16% 小さく、全コマンドで同等か
より速く、出力は byte 単位で同一です（[証拠](docs/evidence/split-comparison.json)）。

## 検査

`bash ci/check.sh` はバイナリをビルドし、言語横断のスモーク、パッケージ発見の契約
（`gramide languages`）、4 パッケージ全体での `symbols` スキーマ契約を走らせます
（[ci/README.md](ci/README.md)）。個々の言語に関することは、その言語のリポジトリで検査します。

## ライセンス

MIT または Apache-2.0、お好みで。
