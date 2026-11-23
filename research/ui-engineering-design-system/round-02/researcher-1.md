# Round 02 Researcher-1 — トークンの型・参照・CSS出力の境界

## 結論

**今回は「DTCG 2025.10の限定サブセット」を明記し、全値エイリアス・型・参照グラフ・テーマ適用後の解決・CSS名衝突を検査する範囲が妥当。** JSON Pointer、グループ拡張、複合型、色空間変換まで対応したと扱わない。対応外の入力は、形式そのものが不正な入力と診断を分ける。これは実装方針の提案であり、この調査では実装・ブラウザ試験を行っていない。

2026-11-23確認時、公式一覧の安定版は **2025.10（2025-10-28）**。Format / Color / Resolver は Final Community Group Report で、W3C勧告ではない。2026年のpreviewを安定版の根拠に混ぜない。[S01][S02][S03][S06]

## 一次資料と確認位置

| ID | 資料・公開位置 | 確認位置と位置付け |
| --- | --- | --- |
| C02-R1-S01 / S01 | [DTCG Format 2025.10](https://www.designtokens.org/TR/2025.10/format/) | §1、§5.1–5.2.2、§6.4、§6.7.3、§7.1–7.5、§8.2、§8.5。Final Community Group Report |
| C02-R1-S02 / S02 | [DTCG Resolver 2025.10](https://www.designtokens.org/TR/2025.10/resolver/) | §5.1–5.2、§6.1–6.3。Final Community Group Report |
| C02-R1-S03 / S03 | [DTCG Color 2025.10](https://www.designtokens.org/TR/2025.10/color/#format) | §4.1、§4.1.1、§4.2、§4.2.1。Format §8.1から追跡 |
| C02-R1-S04 / S04 | [CSS Custom Properties Level 1](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/) | §2、§2.3、§3、§3.1。2022-06-16 Candidate Recommendation Snapshot |
| C02-R1-S05 / S05 | [CSS Color Level 4](https://www.w3.org/TR/css-color-4/) | §10.1–10.2。読取時は2026-11-18 Candidate Recommendation Draft。Colorから追跡 |
| C02-R1-S06 / S06 | [DTCG Technical Reports](https://www.designtokens.org/technical-reports/) | 安定版一覧 |
| C02-R1-S07 / S07 | 既存 Art Direction の `references/i-components.md` | `#i-01`〜`#i-06`、`#i-14`。手元で本文確認 |

ほとんどのHTMLフラグメントはreaderがリンク先を保持しなかったため推測していない。JSONに正確な節名・reader行番号・取得refを保存した。Colorの `#format` とArt Directionのアンカーは実際に確認できたもの。

## 仕様上の事実

| 論点 | 確認した規則 | 根拠 |
| --- | --- | --- |
| 型 | 明示型、参照先からの型、親グループ型を区別。値の形から型を推測しない | S01 §5.2.2 |
| 全値エイリアス | 波括弧はトークン全体を指定し、その `$value` へ解決する。グループや値内部のプロパティは対象外 | S01 §7.1.1 |
| 失敗 | 欠落、循環、不正な参照構文、非トークン対象、型不一致はエラーとして扱う | S01 §7.4.5 |
| 別構文 | プロパティ参照は `$ref`。完全実装にはJSON Pointer対応を要求する本文がある | S01 §7.1.2、§7.3 |
| 寸法 | 数値と `px/rem` のオブジェクト。ゼロでもunitが必要 | S01 §8.2–8.2.1 |
| 時間 | 数値と `ms/s` のオブジェクト | S01 §8.5–8.5.1 |
| テーマ | ソースと選択contextを順序どおり統合した後でエイリアスを解決する | S02 §6.2–6.3 |
| 色 | colorSpaceとcomponentsが必要。alpha省略時は1。hexは任意の6桁fallback。componentsにはnoneも定義される | S03 §4.1–4.1.1 |
| sRGB | RGB各成分は0〜1 | S03 §4.2.1 |
| CSS | 変数名は大小文字を区別。循環依存にはfallback内部の参照も含む。代入後の文法不一致はcomputed-value時に発生する | S04 §2–3.1 |

### 仕様の文面が揃っていない箇所

**型の優先順位は要注意。** §5.2.2は、型を明示していないエイリアスの型を参照先から求める。§6.7.3の継承リストにはその分岐がない。親にdimension、参照先にdurationがある未明示型エイリアスは、今回の小さな実装では解釈方針を宣言するかHOLDとする。[S01]

また、§6.6導入のMAYと§6.6.2 / §7.1.2のMUST、グループ拡張のdeep merge説明とJSON Schema制約の説明には読み合わせが必要。これを短い汎用マージで解決済みにしない。[S01]

§6.9.2の例には寸法unitの `%` が出るが、§8.2の規範規則はpx/remに限定する。§1に従い、非規範の例を型規則の拡張根拠にしない。[S01]

## 今回の検査器への提案

以下は**プロジェクト方針**。そのままDTCGの要求と呼ばない。

1. 入力形を先に調べ、未対応の `$ref`、`$extends`、複合型を検出する。無視して「空グループ」と扱わない。
2. 対応する全トークンのパス・宣言型・親型を集める。
3. テーマの上書きを適用してから、テーマごとに参照グラフを作る。
4. 欠落と循環を確認し、終端まで解決してから型の一致と値を検証する。
5. CSS名を生成した後に一意性を確認する。
6. 対象テーマの検査がすべて成功した場合だけCSSを出力する。失敗時の部分的な成功ファイルを残さない。
7. 結果には「形式不正」「サブセット未対応」「プロジェクト契約違反」「実画面未検証」を区別して記録する。

許容型は `color` の数値sRGB、`dimension`、`duration` から始め、`number` は必要時に追加する。数値判定でbooleanを通さない。NaN・Infinity・実装の数値範囲外は明示的に失敗させる。数値上限や参照深さ上限は実装の制約として記録する。

**負のdurationを一律に「DTCG不正」としない。** 確認した時間型の節に一般的な非負制約はない。利用先のプロパティや製品方針で制限するなら、その制限を別の契約として示す。[S01 §8.5] 負の寸法もpadding等への使用可否とは別に扱う。

## 反例・境界例

完全な入力オブジェクトと期待結果は `researcher-1.json` の44件の `test_vectors` に記録した。これらは今回作成した検査用の例で、実行結果ではない。

| ケース | 入力の特徴 | 期待判定 |
| --- | --- | --- |
| valid-chain | dimension終端 → 未明示型alias → 明示dimension alias | 対応範囲なら同じ値へ解決 |
| missing-reference / cycle | 欠落対象、自己参照、3ノード循環 | エラー。経路を示す |
| type-mismatch | durationがdimensionを参照 | エラー |
| invalid-group-target | `{group}` がグループを指す | エラー |
| invalid-property-target | `{token.$value.value}` | 波括弧による値内部アクセスとしてエラー |
| unsupported-property-ref | `$ref: "#/a/$value/value"` | 未対応。DTCG一般の無効とはしない |
| unsupported-extension | `$extends: "{base}"` | 未対応 |
| unsupported-root-token | グループ内の予約トークン `$root` と `{g.$root}` | 実装しない場合は未対応。通常のドル接頭辞禁止でDTCG不正と断定しない |
| invalid-zero-no-unit | dimensionに `{value: 0}` のみ | エラー |
| invalid-dimension-unit | dimensionのunitが `%` | 規範の型規則ではエラー |
| invalid-color-string | colorの値が `"#123456"` | 2025.10の値形ではエラー |
| unsupported-none / unsupported-p3 | noneを含むHSL、Display P3 | 正当な構文をサブセット未対応として扱う |
| invalid-fallback-hex | fallbackが4桁/8桁 | DTCGの6桁fallback要件に不一致 |
| theme-override | 基本色のみをdarkで上書き | semantic aliasもdarkの最終値へ解決 |
| theme-induced-cycle | 上書きによって循環が生じる | そのテーマを失敗 |
| name-collision | `a-b.c` と `a.b-c` をハイフン結合 | 両方 `--a-b-c` になるため出力を失敗 |
| case-distinct | `A` と `a` | 大小文字維持なら別名。小文字化時は衝突を検出 |
| css-name-injection | 名前に空白や区切り記号 | CSS escapeまたは出力対象名の制限。一般DTCG不正としない |
| permuted-json-key-order | JSONメンバーの挿入順だけ変更 | 宣言したソート方針で出力バイト列を一致させる |
| css-wrong-type-fallback | `--ink:12px; color:var(--ink,black)` | fallbackでblackに修復されるとは判断しない |
| css-fallback-cycle | `--x:var(--y,var(--x))` | fallback参照も依存に含める |

## 決定的CSS出力の限界

「同じ入力から同じCSS文字列」はビルド方針として定義できる。具体的にはパスのソート規則、大小文字、CSS名への変換、数値表現、単位保持、セレクター、改行を固定する。CSS標準がDTCGからの唯一の出力形式を定めるわけではない。[S01 §3.4、S04 §2からの推論]

数値sRGBだけなら、例として `color(srgb 0.125 0.5 0.875 / 0.75)` を生成できる。[S05 §10.1–10.2] hexへ丸めて精度を落とすか、fallbackを別に使うかは追加方針であり、黙って変換しない。DTCGのsRGB範囲と、CSS側のout-of-gamut色の許容範囲も混同しない。[S03 §4.2.1、S05 §10.1]

解決済みリテラルを出力した場合、後からCSSで基本変数だけ上書きしてもsemantic変数は自動追従しない。全テーマを再生成するか、実行時var依存を別に設計・検証する必要がある。[S02 §6.3、S04 §2.3からの推論]

実際のカスケード、利用先CSS文法、ブラウザ機能対応、透明度の合成、forced-colors、コントラストは今回のグラフ検査では測定していない。成功したJSON解決から、画面の見え方やアクセシビリティ適合を推定しない。

## Art Directionとの重複と追加範囲

既存I-01〜06はCSS変数、面と前景の対、ライト/ダーク公開、角丸、初期配色などを扱い、I-14はテーマクラスの反復を扱う。[S07]

Cで追加するのは、**既存の役割と値を受け取って、参照・型・テーマごとの存在・出力名を検査する仕組み**。配色や角丸の段階を新たに選ばない。必須semantic roleを全テーマに要求する場合、それは製品契約でありDTCGが固定のrole一覧を強制しているとは説明しない。

## 調査記録と未確認

- 検索は一次資料を対象に3クエリ、検索呼出し2回、返却ヒット15件。最初の2クエリは同じ呼出しだったため、個々のヒットがどちらに属するかは不明と記録した。
- `fetch.py <sources_dir> <name> <url>` をFormatに一度実行し、DNS失敗を記録。再試行の反復や安全設定の解除は行っていない。
- web readerのopen/find/clickによる断片を非公開領域に保存。**full_original=false**。Colorはreader自身がrewritten summaryと表示したため、原文完全保存や原文引用照合の成功を主張しない。
- Format → Color → CSS Color、Format → normative RFC6901リンクを実際に追跡。RFC6901はランディングページまで確認し、JSON Pointer実装は今回の対象外として全文検討を止めた。
- 発見済み：型、全値参照、値形、テーマ後解決、CSS依存・fallbackの一次根拠。
- 探した範囲で見つけていない：DTCGからCSSへの単一必須シリアライズ方式、時間型一般の非負規則。
- 未調査：全Resolver文書の実装適合、グループ拡張の曖昧さの解消、wide-gamut変換、対象ブラウザの実画面、WCAG適合。
- 停止理由：今回の限定サブセットを設計する論点に一次資料の位置が付いた。仕様文面の衝突とreaderの限界を未解決として残し、対象外の実装・視覚検証へ範囲を広げない。

