# 型・テーマ・CSS出力の契約

使用するInstruction Unitは `C-UI-005`（構文・型・参照）、`C-UI-006`（テーマと必須ロール）、`C-UI-007`（名前と出力）である。配色やロール名は既存の製品とArt Directionから受け取る。

## 1. 対応範囲を先に決める

`checks/tokens.py` は **DTCG 2025.10を参照した限定サブセット**である。2025.10はFinal Community Group Reportであり、W3C勧告ではない。このスクリプトは完全なFormat / Color / Resolver実装ではない。

| 対象 | この実装の契約 |
| --- | --- |
| グループ | 通常の入れ子object、親からの`$type`継承、文字列`$description` |
| トークン | `$value`、任意の`$type`と`$description`。値の形から型を推測しない |
| 参照 | 値全体の`{token.path}`だけ。完全なトークンへ解決する |
| dimension | 有限数`value`と`unit: px / rem`。ゼロにも単位を付ける |
| duration | 有限数`value`と`unit: ms / s`。負の値は型一般の不正としない |
| number | booleanを除く有限JSON数値。利用先固有の範囲は別契約 |
| color | `colorSpace: srgb`、0〜1の数値3要素、任意alphaは0〜1で既定1。任意hexは6桁。出力はcomponents/alphaを使う |
| 名前 | 各パス要素はASCII英数字・`_`・`-`。大小文字を維持する。これは出力側の限定方針 |
| 未対応 | `$root`、`$ref`、`$extends`、`$extensions`、`$deprecated`、複合型、他色空間、`none`、外部参照、raw `var()/calc()`、補間、出力filter |
| 上限 | グループ深さ32、テーマごと10,000トークン、参照chainのノード数256、JSON全体の深さ64・ノード数250,000、整数の絶対値のbit長1,024。規格上の上限ではなく実装契約 |

未対応は`UNSUPPORTED`として止める。合法な`$root`やP3色までDTCG一般の不正と断定しない。対応型の不正値は`INVALID`、ロール欠落など製品の契約違反は`CONTRACT`、上限超過は`LIMIT`で返す。未知構文を空グループとして捨てない。

明示`$type`があるaliasは参照先の型と一致させる。未明示aliasは参照先の型を使うが、親型と参照型が異なる場合は明示`$type`を要求する。Format §5.2.2と§6.7.3の記述の違いを保留した局所方針であり、公式解釈を確定したという意味ではない。

## 2. 製品のテーマを合成する

[入力例](../examples/booking-tokens.json) は次の独自wrapperを使う。DTCG Resolver文書の構文ではない。

| フィールド | 入力するもの |
| --- | --- |
| `format` | 固定値`C-token-subset/1` |
| `prefix` | CSS変数の接頭辞。ASCII英字で始め、英数字・`_`・`-`だけ |
| `base` | 基底トークン文書 |
| `themes` | テーマ名→上書きobject。各テーマでbase→その上書きの順に処理する |
| `default_theme` | 宣言済みテーマの一つ |
| `roles` | 製品が必要とするトークンパス→期待型。空の一覧は受け付けない |

テーマごとに基底をコピーし、グループを再帰的に統合し、トークンを一単位として置換する。部分的な`$value.value`上書きやグループ/トークンの入替えは拒否する。配列で複数の上書き層を渡す機能はない。追加するときは順序と置換単位を新たに固定する。

**合成後に**全トークンを解決し、必須ロールの存在と型を確認する。別テーマの解決キャッシュを流用しない。同じロールがテーマによって別のprimitiveを指すことは許す。基底から継承したロールも有効であり、全テーマへの同じ宣言の複製を要求しない。

報告には宣言型・親型・実効型・参照経路、定義元と終端値の由来を残す。全テーマが通らなければCSSは`null`になり、成功テーマだけを全体成功と扱わない。

## 3. 変数名と単一CSS bundleを作る

`--<prefix>-<path segments joined with hyphens>`に写像し、異なるパスが同じ変数名になったら両パスを報告して拒否する。例えば`a-b.c`と`a.b-c`は衝突する。A/aは大小文字を保持するため区別する。

全トークンを解決済みliteralで出す。dimension/durationは値と単位を一つにし、数値sRGBは`color(srgb … / …)`にする。数値はPythonの最短round-trip表記を基本に、整数は小数点なし、正負ゼロは`0`に正規化する。パスをソートし、既定テーマを先に、残りを名前順に出力する。同じ意味のJSONでメンバーの挿入順だけが違ってもCSSは同一になる。

各テーマは生成した`[data-theme="id"]`セレクターを持ち、既定テーマには`:root`も付ける。IDはprefixと同じ安全な文字集合に限定する。生成ファイルを一つのjobが所有する。テーマ別の出力先設定を受理しないため、複数ファイルの公開や出力先競合を検査済みとは呼ばない。

literal出力は後からprimitive変数だけを変えてもsemantic変数を自動更新しない。必要な変更はテーマを再ビルドする。runtime参照、外部変数、filterを追加するなら、参照先を落とした出力を拒否するか、明示的にliteralへ解決する機構と別の試験を追加する。

## 実行と失敗時の扱い

リポジトリルートから実行する。

```sh
python3 modules/ui-engineering-design-system/checks/tokens.py modules/ui-engineering-design-system/examples/booking-tokens.json
python3 modules/ui-engineering-design-system/checks/tokens.py modules/ui-engineering-design-system/examples/booking-tokens.json --css /tmp/booking-tokens.css
python3 -m unittest discover -s modules/ui-engineering-design-system/tests -p 'test_tokens.py' -v
```

終了0は対応範囲の成功、1は検査で拒否、2は入力解析やI/Oの失敗。JSON解析前段で拒否した巨大な整数や不正UTF-8も2、解析後に判定した上限違反は1になる。`build()`と`resolve()`は再帰copy前に反復処理で深さ・整数サイズを検査する。`--css`は全検査後に単一ファイルを一時ファイルから置換する。検査が失敗した場合は前の出力を保持する。利用側は終了コードを見て、保持された古いCSSを今回の成功出力として公開しない。出力ディレクトリは先に用意する。

正常値、欠落参照、循環、型違い、テーマによる循環・型変化、ロール欠落、名前衝突、JSON順序入替え、別製品のロールを検査する。入力例の色は変換検査のデータであり、画面のコントラスト実績ではない。

## 成功に含めない観測

CSSの利用先プロパティの全文法、ブラウザーの対応、端末設定、入れ子テーマ、強制色、透明度合成後のコントラスト、フォーカス表示、AT、WCAG適合は別途観測する。`color(srgb …)`の出力成功を対象ブラウザーでの対応確認に置き換えない。`var(--x, red)`も、存在する`--x:16px`をcolorへ修復する根拠にはならない。

## 原典と判断の境界

- [DTCG Format 2025.10](https://www.designtokens.org/TR/2025.10/format/): §5.2.2、§6.7.3、§7、§8.2、§8.5。型・参照と対応型の値形の根拠。全JSON Pointer対応は本実装の範囲外。
- [DTCG Color 2025.10](https://www.designtokens.org/TR/2025.10/color/): §4.1、§4.2.1。構造化色の根拠。取得証拠はreader断片で、完全原文ではない。
- [DTCG Resolver 2025.10](https://www.designtokens.org/TR/2025.10/resolver/): §6。統合後の参照解決を採用する根拠。独自wrapperはその完全実装ではない。
- [Style Dictionary references](https://styledictionary.com/reference/utils/references/): 出力filterで参照先がなくなる実装上の条件。
- [Style Dictionary #1398](https://github.com/style-dictionary/style-dictionary/issues/1398): 寸法オブジェクト出力の歴史的な失敗報告。最新版での未修正を主張しない。
- [CSS Custom Properties](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/): §2.3、§3、§3.1。CSSの参照・継承・fallbackを静的token graphと混同しない根拠。

対応subset、ロール一覧、ASCII名、上限、token単位置換、single bundle、literal出力、原典の文面差に対する明示型要求は今回の製品方針である。既存Art Directionのテーマ・配色・面/文字の対の指示は参照して使う。
