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
gramide balance Widget.cpp       括弧とリテラルだけ。文法のない言語向け:
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

このリポジトリは言語パッケージを合成する薄い CLI です。エンジンも 14 個の言語パッケージも、
すべて独立したリポジトリにあります。各 `gramide-*` が manifest、字句解析器、文法、生成表、
テスト、単体 CLI、Quality ワークフローを所有します。CLI は git 依存で参照し、正確なコミットを
`almide.lock` に記録します。ここに文法ソースは同梱しません。

| パッケージ | 内容 | |
|---|---|---|
| [gramide](https://github.com/O6lvl4/gramide) | エンジン: 字句解析・パーサ・木・読み手・ライブラリとしてのコマンドライン・パッケージ契約 | `gramide` |
| gramide-cli | このリポジトリ: バイナリ。`PATH` 上の `gramide` | `gramide_cli` |
| [gramide-almide](https://github.com/O6lvl4/gramide-almide) | Almide `.almd` | `gramide_almide` |
| [gramide-go](https://github.com/O6lvl4/gramide-go) | Go `.go` | `gramide_go` |
| [gramide-rust](https://github.com/O6lvl4/gramide-rust) | Rust `.rs` | `gramide_rust` |
| [gramide-python](https://github.com/O6lvl4/gramide-python) | Python 3.14 `.py` `.pyi` | `gramide_python` |
| [gramide-javascript](https://github.com/O6lvl4/gramide-javascript) | JavaScript(JSX 込み)`.js` `.mjs` `.cjs` `.jsx` | `gramide_javascript` |
| [gramide-typescript](https://github.com/O6lvl4/gramide-typescript) | TypeScript 5.9 `.ts` `.mts` `.cts`、`.tsx` は独立パッケージ | `gramide_typescript` |
| [JSON](https://github.com/O6lvl4/gramide-json) | JSON `.json`; 構文検査対応 | `gramide_json` |
| [TOML](https://github.com/O6lvl4/gramide-toml) | TOML 1.0 コア構文の読み取り `.toml` | `gramide_toml` |
| [CSS](https://github.com/O6lvl4/gramide-css) | CSS コア構文の読み取り `.css` | `gramide_css` |
| [SQL](https://github.com/O6lvl4/gramide-sql) | SQL コア構文の読み取り `.sql` | `gramide_sql` |
| [Lua](https://github.com/O6lvl4/gramide-lua) | Lua コア構文の読み取り `.lua` | `gramide_lua` |
| [C](https://github.com/O6lvl4/gramide-c) | C コア構文の読み取り `.c` `.h` | `gramide_c` |
| [Java](https://github.com/O6lvl4/gramide-java) | Java コア構文の読み取り `.java` | `gramide_java` |
| [C#](https://github.com/O6lvl4/gramide-csharp) | C# コア構文の読み取り `.cs` | `gramide_csharp` |

各言語パッケージは、字句解析器、値としての文法、その文法をコンパイルしてコミットした表、
どのノードが名前を宣言するかの規則、テスト、その言語の参照パーサに対するオラクル、そして
自前の小さなバイナリ（`gramide_go` は Go だけの `gramide`）を持ちます。だから他の言語なしに
テスト・計測・リリースできます。何をどのコーパスでカバーしているかは各 README にあります。

ここの `src/main.almd` は 14 パッケージ、15 定義（`.tsx` は TypeScript の第二の定義）を列挙してエンジンに渡します。言語を足すのはそこに 1 行と
`almide.toml` に 1 行。あるプロジェクトが使う言語だけを出荷するバイナリは、同じファイルの
リストを短くしたものです。Almide は静的リンクなので、合成はローダではなくファイルです。

## インストール

```
almide install github.com/O6lvl4/gramide-cli --name gramide      # ネイティブバイナリ 1 つ → ~/.local/bin/gramide
```

`--name` が要るのは、Almide がバイナリをパッケージ名で名付け、パッケージ名が `gramide_cli`
だからです。チェックアウトからは `almide build --release -o gramide` で `./gramide` ができます。
エンジンと既存 6 パッケージは `almide.lock` のコミットで取得し、新規 8 パッケージも独立した git リポジトリから取得します。Almide 0.62 以降が必要です。
[hew](https://github.com/O6lvl4/hew) は `PATH` 上の `gramide` を見つけてコードを読みます。

## 現状

登録定義は **7 → 15** になりました。既存 7 定義と JSON は `check` に対応します。
TOML・CSS・SQL・Lua・C・Java・C# は、実際の文法と構文木を持つ **コア構文の読み取り対応** です。
全言語仕様への適合や tree-sitter との同等性は主張しません。対応構文と制限は各 README に明記しています。
これらの言語への `check` は「no language package provides check」として失敗し、
有効なソースを壊れていると判定する検査器にはなりません。`symbols` は回復済みの木を完全な結果として返さず、
新規パッケージは `symbols-recovered` を公開しません。

新規 8 パッケージのコーパス全体・性能比較は未確立です。以下の計測は従来のパッケージとバイナリのもので、
今回の拡張版の計測ではありません。

既存パッケージのコーパス検証は各リポジトリにあります。従来の Almide・Go・Rust・Python の検証が立てる保証は一方向です。**gramide が拒否する
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
より速く、出力は byte 単位で同一です（[証拠](docs/evidence/split-comparison.json)）。tree-sitter
に対しては、新規プロセス・起動込みで、Go 800 関数の構造化読み取りが tree-sitter の 0.78 倍の時間、
Python の `inspect.py` が 0.70 倍、Python 標準ライブラリ全体のパースが 0.51 倍。数 KB のファイルは
中央値ではコイントスです。起動の床では gramide の方が C のアダプタより速く始まるのに、Rust のバイナリは
負荷がかかると床から離れやすく、その背後にあるランタイム初期化 0.2 ミリ秒はコンパイラ側で
しか外せません（[記録](https://github.com/O6lvl4/gramide/blob/main/bench/README.md)）。

## 検査

`bash ci/check.sh` はバイナリをビルドし、言語横断のスモーク、パッケージ発見の契約
（`gramide languages`）、15 定義の `symbols` 契約を走らせます。各言語の文法テスト、生成表、正常・異常 fixture、
UTF-8 範囲、オラクル検証は各リポジトリの CI が担当します
（[ci/README.md](ci/README.md)）。ここでは合成と共通スキーマを検証します。

## ライセンス

MIT または Apache-2.0、お好みで。
