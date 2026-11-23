# Round 02 / Analyst — 型付きtokenとtheme出力の限定契約

**結論：C-003の増分を3つのInstruction Unitにまとめる。** U1は対応subsetと型・参照、U2はテーマ統合後のrole契約、U3は衝突のない決定的literal CSS出力である。既存部品の再利用・合成・新設、booking例、一般theme guidanceは保持する。これは分解・理解・溶解の結果であり、実装・採用判定・登録ではない。

## 方法と根拠の扱い

sankai README、現行SKILLと分解・理解・溶解の3参照を読み、LLMで意味と条件を照合した。CLIは使わない。固定planのrubricは変更していない。schemaはround01 analysis.jsonに合わせた。研究入力は両Researcherのmd/jsonで、原典の直接再取得は行っていない。

- 【事実】：Researcherが特定した原典節の内容。規範と製品docs・歴史的issueは区別する。
- 【推論】：事実から導いた実装上の含意。
- 【製品policy】：今回採用できる限定検査器の契約。原典の普遍的要求とは呼ばない。

DTCG 2025.10はFinal Community Group Reportであり、W3C勧告ではない。DTCG 2026 previewは対象外。両Researcherの原文fetchは計2回ともDNS失敗。reader断片は完全原文ではなく、Colorは書き換え要約の表示もある。出典は短い要約と位置だけを記し、raw/非公開制御記録や第三者全文を出力しない。費用はunknown。

## Instruction Units

### C003-U1 — 対応範囲を宣言し、型付き参照グラフを検証する

**指示本文**

1. 【製品policy】入力をDTCG 2025.10の限定サブセットとして宣言する。候補は単一JSON内のグループ、全値の波括弧alias、colorの数値sRGB、dimensionのpx/rem、durationのms/s、有限numberである。採用する型ごとに値形とserializerを列挙し、未実装の型を受理しない。全Format/Color/Resolver対応とは表示しない。
2. 【事実＋製品policy】意味を持つ構文を検出してからグループとトークンを列挙する。未実装の$ref、$extends、$root、複合型、未知$type、外部参照、noneや非sRGB色はunsupportedとして拒否し、メタデータや空グループとして捨てない。原典で合法な構文をDTCG一般の不正と呼ばない。無視できる記述メタデータも明示的な許可リストに限定する。
3. 【事実＋解釈policy】宣言$type、親グループ型、alias参照先の型を別々に保持し、値の見た目から型を推測しない。非aliasの未明示型は最も近い親型を使う。未明示aliasは§5.2.2の参照先型の扱いを採用候補とし、§6.7.3の継承リストにはこの分岐がないことを残す。親型と参照型が異なる場合は明示$typeを要求する局所契約エラーにし、仕様矛盾を解消したとは主張しない。明示型があるaliasは終端の型と一致させる。
4. 【事実】波括弧aliasを値全体として解析し、トークンを指す有向辺として扱う。グループやtoken.$value内部への波括弧参照、壊れた構文、欠落対象、自己参照と多段循環、型不一致を拒否する。全トークンを走査し、失敗したテーマ・パス・参照経路を返す。文字列置換で補間やcalcを実装したことにしない。
5. 【事実＋subset policy】終端値を型別に検証する。dimensionは有限数valueとpx/rem、durationは有限数valueとms/s、numberは有限数のみとしbooleanを数値として通さない。ゼロでも寸法unitを要求する。colorはcolorSpace=srgb、3個の有限数componentsを各0〜1、alphaを0〜1（省略時1）、hexがあれば6桁として確認する。noneと他色空間は未対応、sRGB範囲外や4/8桁fallbackは対応型の形式不正として区別する。
6. 【製品policy】形式不正、サブセット未対応、製品契約違反、実装資源上限を区別して報告する。数値範囲・トークン数・参照深さに実装上限を設けるなら値を明記する。例外落ちや途中までの受理を成功として返さない。

**使う場面：** 既存トークン文書の取込、変換、テーマ検査の前段。

**入力：** 版と対応subset / 型付きトークン文書 / 型継承の解釈policy / 資源上限と診断分類

**出力：** パス・宣言型・実効型・解決値・出典を持つグラフ結果 / 失敗分類とテーマ/パス/参照経路

**維持する条件：** DTCG 2025.10はFinal Community Group ReportでありW3C勧告ではない。DTCG 2026 previewを採用根拠に混ぜない。 / 値検証はCSSの利用先プロパティの全制約を検査するものではない。 / 未対応型に含まれる別の誤りは未検査でもよいが、unsupportedを全面的な仕様妥当性判定にしない。

**例外：** 負のduration・dimensionを型一般のDTCG不正としない。非負制約が必要なら利用先または製品の別契約にする。 / §6.9.2の%の例は§8.2のpx/remの規範規則を広げる根拠にしない。 / 合法な$rootを通常のドル接頭辞禁止だけで形式不正としない。未知typeの拒否は対応範囲の拒否であり、未知値の合法性までは確定しない。

**依存先：** researcher-1.jsonのC02-R1-P01〜P05と原典節 / C003-U2：テーマを扱う場合は合成後の各グラフを入力する

**この単位にする理由：** 型決定と参照解決を分離し過ぎると、aliasの実効型と終端値の条件が落ちる。このまとまりは入力の意味を確定する仕事であり、見た目やCSS出力方式から独立して検査できる。曖昧入力の明示型要求は原典の逐語要求ではなく、解釈差を隠さない局所方針。

**変えられる範囲：** 内部グラフ表現・探索アルゴリズム・言語は同じ成功値と診断条件を保てば変更可能。 / 対応型や構文を追加するときは値形・解決規則・反例を追加し、既存のunsupportedを無根拠にacceptへ変えない。

**未確定：** §5.2.2と§6.7.3の文面差の公式な解消は未確認。 / $ref/$extendsの規範文言の読み合わせと完全実装は範囲外。 / Color資料はreaderが書き換え要約と表示したため、完全原文との逐語照合を保証しない。

**失敗の形：** 合法な未対応構文を無視して空の成功結果を返す / alias型を値形から推測する / 循環を途中のキャッシュで隠す / boolean・unitなしゼロ・無効sRGBを受理する / 負の値を根拠なくDTCG不正と呼ぶ

**出典：**
- [C02-R1-S01](https://www.designtokens.org/TR/2025.10/format/) — 5.2.2 Type; 6.4.2 Reference Resolution and Evaluation; 6.4.3 Inheritance Semantics; 6.7.3 Type Inheritance; 7.1.1 Curly Brace Syntax; 7.1.2 JSON Pointer Syntax; 7.2.2 Chained References; 7.2.3 Circular References; 7.4.5 Error Conditions; 8.2 Dimension; 8.2.1 Validation; 8.5 Duration; 8.5.1 Validation。Final Community Group Report; not W3C Standard/Recommendation。記録：`researcher-1.json#/sources/0`。
- [C02-R1-S03](https://www.designtokens.org/TR/2025.10/color/) — 4.1 Format; 4.1.1 The none keyword; 4.2 Supported Color spaces; 4.2.1.1 Components。Final Community Group Report。記録：`researcher-1.json#/sources/2`。
- [C02-R1-S06](https://www.designtokens.org/technical-reports/) — Technical Reports。Official publication index。記録：`researcher-1.json#/sources/5`。
- [R2-S2](https://styledictionary.com/info/tokens/) — Overview note; Referencing / Aliasing; Collision warnings。primary documentation or author-reported incident; not a universal normative requirement。記録：`researcher-2.json#/sources/1`。
- [R2-S4](https://github.com/style-dictionary/style-dictionary/issues/1398) — Description; collaborator comments 2024-11-26 and 2025-01-20。primary documentation or author-reported incident; not a universal normative requirement。記録：`researcher-2.json#/sources/3`。

**反証手順案（全件未実行）：**

| ケース | 手順 | 失敗判定 |
| --- | --- | --- |
| valid-chain | 明示dimension終端→未明示alias→明示dimension aliasを解決し、同じ型と0.5remを得る。 | 値・型の相違、元JSON順序による結果の変化。 |
| missing-reference | 存在しないトークン参照を入力する。 | 成功、欠落パスのない一般エラー。 |
| cycle | 3ノード循環を入力する。 | 成功、無限再帰、循環経路が不明。 |
| type-mismatch | duration aliasからdimension終端を指す。 | 型を無視した受理。 |
| unsupported-construct | 未実装$ref・$extends・複合型を入力する。 | 黙って無視、DTCG全体の不正と断定。 |
| valid-srgb / invalid-zero-no-unit | 数値sRGB正常例とunitなしのdimensionゼロを別々に判定する。 | 両方accept、または正常sRGB拒否。 |

### C003-U2 — テーマを統合してから意味roleを独立に解決する

**指示本文**

1. 【製品policy】既存の基底トークン、宣言したテーマ一覧、順序付きoverride、必要な意味roleのパスと期待型、既存の面/前景の組を入力として受け取る。必須role一覧やトークン層数は製品契約であり、DTCGの普遍要件として作らない。配色・書体・角丸の新しい選択を加えない。
2. 【事実＋製品policy】各テーマについて基底から独立した文書を作り、宣言した順序でoverrideを適用した後にaliasを解決する。局所wrapperではグループを再帰的に統合し、トークンを一単位として置換する等、置換単位を事前に固定する。グループ/トークンの形の衝突は拒否する。配列の順序とJSONメンバー挿入順を混同せず、暗黙のlast-write-winsを認めない。このwrapperをDTCG Resolver文書の実装とは呼ばない。
3. 【推論】合成後の各テーマへU1の型・値・欠落・循環検査を実行し、テーマ間で解決済み値やaliasキャッシュを使い回さない。基底だけの成功でdark等を成功にしない。意図した同一パスの上書きと、生成名・出力先の衝突を別の判定にする。
4. 【製品policy】各テーマの解決後に必須roleの存在と期待型を確認し、roleのパス・型・解決値・参照先・値の由来を対応づける。同じroleがテーマで別の基底を参照することは許せる。基底のrole継承は宣言したmerge契約が認める場合に成立する。theme内にroleが直接書かれていないだけで欠落としない。
5. 【推論＋製品policy】全宣言テーマが契約に通った場合にだけU3へ渡す。失敗テーマを省いた部分成果を全テーマ成功と報告しない。literal出力はテーマごとの完全なrole値を生成し、後から基本CSS変数だけを変更すれば意味変数が追従すると説明しない。

**使う場面：** ライト/ダーク等のテーマや密度variantを含む既存tokenセットのビルド。

**入力：** 基底と順序付きtheme override / 製品所有の必須role/期待型/既存pairing / merge単位とテーマ/スコープ契約

**出力：** テーマごとの解決済みrole表とprovenance / テーマ名・role・パス付きの契約エラー

**維持する条件：** semantic roleの意味は上流から受け取り、Cが意味名だけを根拠に新配色を創作しない。 / resolverの順序原則を再利用することと完全なsets/modifiers/resolutionOrder形式への適合を区別する。 / 未宣言テーマ・入れ子スコープ・端末の自動切替はこの静的グラフ結果の保証範囲に入れない。

**例外：** 同一パスの明示overrideは意図した置換であり、全重複パス禁止にはしない。 / 意味roleの参照先の変更を型不一致と混同しない。同じ型なら別のpalette値への参照が可能。 / 必須roleの欠落は製品契約エラーであり、DTCG文書自体の形式不正とは限らない。

**依存先：** C003-U1 / 現行SKILL.md「状態・通知と既存テーマの接続」 / Art Direction references/i-components.md I-01〜03/I-14とreferences/b-visual.md B3-03/05/07/14

**この単位にする理由：** グラフが正しくても、別テーマのキャッシュや欠けたroleで画面の契約が壊れる。統合順序・テーマ独立性・role完全性は同じ仕事として保持する。required manifestやtoken単位置換は製品方針であり、標準の追加義務にしない。

**変えられる範囲：** テーマ数・role名・入力ファイル構成は製品契約に合わせて変更可能。 / 別merge方式を採用する場合は置換の単位・順序・欠落の意味を固定し、同じ反例で比較する。

**未確定：** 対象製品のrole一覧・pairing・スコープ・数値制約の具体値は未提示。 / Style Dictionary最新リリースのDTCG対応表とissue修正リリースは未検証。

**失敗の形：** baseの値をdarkに再使用 / darkだけの循環や型変更を見落とす / 存在する全tokenが解決しただけで欠落roleも完了扱い / 原始色の層数や必須roleを全製品に強制

**出典：**
- [C02-R1-S02](https://www.designtokens.org/TR/2025.10/resolver/) — 5.1 Case sensitivity; 5.2 Enforcing strings; 6 Resolution logic; 6.1 Input validation; 6.2 Ordering; 6.3 Aliases。Final Community Group Report; not W3C Standard/Recommendation。記録：`researcher-1.json#/sources/1`。
- [C02-R1-S07](https://github.com/RNA4219/anything-frontend-art-direction) — #i-01; #i-02; #i-03; #i-04; #i-05; #i-06; #i-14。Local project guidance; not interchange standard。記録：`researcher-1.json#/sources/6`。
- [R2-S2](https://styledictionary.com/info/tokens/) — Overview note; Referencing / Aliasing; Collision warnings。primary documentation or author-reported incident; not a universal normative requirement。記録：`researcher-2.json#/sources/1`。
- [R2-S3](https://github.com/style-dictionary/style-dictionary/issues/1590) — Proposal; comments 2026-08-27, 2026-08-28, 2026-08-31, 2026-09-18。primary documentation or author-reported incident; not a universal normative requirement。記録：`researcher-2.json#/sources/2`。
- [R2-S5](https://opensource.adobe.com/spectrum-web-components/tools/styles/) — Global tokens; Color options; Token imports。primary documentation or author-reported incident; not a universal normative requirement。記録：`researcher-2.json#/sources/4`。
- [R2-S8](https://spectrum.adobe.com/page/color) — Solid color background with black or white; Two-tone color pairing。primary documentation or author-reported incident; not a universal normative requirement。記録：`researcher-2.json#/sources/7`。

**反証手順案（全件未実行）：**

| ケース | 手順 | 失敗判定 |
| --- | --- | --- |
| theme-override | baseの基底色だけをdarkで上書きし、semantic aliasが各テーマの値に変わることを確認する。 | baseとdarkの値が同じキャッシュから返る。 |
| theme-induced-cycle | baseは成功するがoverride後に循環する入力を渡す。 | darkを成功または黙って除外する。 |
| theme-role-coverage | 全ての存在tokenは解決するが製品必須roleが欠落するテーマを作る。 | テーマ完全性を成功扱いする。 |
| dark-role-repoints | 同じrole/型を保ち、darkだけ別の有効なpalette tokenへ参照を替える。 | 有効な参照先変更を一律拒否、またはbaseの値を再利用。 |

### C003-U3 — CSS名と出力先を検査し、決定的literalを出力する

**指示本文**

1. 【製品policy】パスのソート、CSS名への写像、大小文字、許容名またはescaping、数値表現、単位、セレクター、改行、出力先を固定する。パスの同一性を保ったまま写像後の名前が一意か調べ、a-b.cとa.b-c等の衝突を元の両パス付きで拒否する。CSS名の制限による拒否をDTCG一般の名前不正としない。
2. 【製品policy】今回を単一の決定的CSS bundleと生成済み[data-theme="id"] selectorに固定するなら、テーマIDからscopeへの写像を一意にし、出力先は一つの集約jobだけが所有する。この構成ではテーマごとの複数file出力を対応範囲から外し、複数出力先の上書き検査を実装済みとは呼ばない。複数file方式を追加する場合にだけ正規化した出力先衝突を検査し、後のテーマによる無言上書きを拒否する。
3. 【推論＋製品policy】限定実装はU1/U2で解決した値をliteralとして型別serializerで出力する。dimension/durationは数値と許可unitを一つの値にし、value/unitを別token化したりobjectを文字列化しない。sRGBの数値・alphaを保つcolor(srgb … / …)等、採用する表記を明示し、hexへの丸めや色空間変換を勝手に加えない。全対象の検査後にだけ出力を確定する。
4. 【事実＋製品policy】reference-preserving出力・export filter・外部CSS変数は未実装なら拒否する。追加実装する場合は、残す全参照が宣言したbundleとscopeで閉じるかを確認し、参照先を出力から落としたら明示的なliteralへ解決するか失敗にする。raw var()/calc()/fallbackを解析しない検査器が、それらを安全と判定してはならない。
5. 【事実＋推論】CSSのfallbackは存在する不適合な値を利用先の型へ修復する機構ではない。fallback内部もCSSの循環依存に関わり、custom propertyの解決と継承には順序がある。literal出力や静的DTCG解決をCSSカスケードのシミュレーターとして扱わない。
6. 【製品policy】結果をgraph/type、theme role、name/destination、serializationの検査範囲として返す。rendered contrast、focus visibility、forced-colors、端末設定、入れ子theme、ブラウザ機能対応、WCAG適合は別の観測欄で未検証/HOLDとする。graph成功をvisual成功に変換しない。

**使う場面：** 検証済みtoken/theme契約をCSS成果物へ変換する直前。

**入力：** U1/U2の解決済み全テーマ / 名前写像と数値/色/単位serializer / scopeと出力先の契約 / 必要なら明示的export対象

**出力：** 決定的なCSS文字列または成果物 / 元パスと生成名/テーマ/出力先の対応表 / 検査済み範囲と未検証visual欄を分けた報告

**維持する条件：** 同じ値・同じoverride順のJSONでメンバー挿入順だけを変えても出力が一致するようにする。 / 全対象の検査に失敗したら新規成功artifactを部分的に残さない。既存成果物の削除を指示する意味ではない。 / ブラウザ起動や保護設定の迂回をこの分解の一部として行わない。 / 固定single-bundle方式を採用した場合、per-theme destinationフィールドは未対応として拒否するか、公開契約から除外する。任意の値を黙って受理して検査済みにしない。

**例外：** 大小文字を維持すればAとaは異なるCSS custom propertyである。小文字化を選ぶ場合は写像後の衝突を拒否する。 / literal方針では出力されない基底tokenを解決に使えても、壊れたvar参照は出力しない。 / 文字列が決定的であることは、全ブラウザの描画・利用先CSS文法の妥当性を保証しない。

**依存先：** C003-U1 / C003-U2（複数テーマの場合） / Art Directionの既存theme/contrast指針 / Dの評価とリリース判定

**この単位にする理由：** 名前とファイルの衝突は入力グラフが正常でも発生する。serializerと成果物の対応を一つに保ち、実画面の意味とは切り分けて反証できる。literal採用はruntime参照の責務を限定する実装提案であり、唯一の標準出力ではない。

**変えられる範囲：** CSS名やselector、ファイルの分け方は互換性と一意性を確認して変更可能。 / 別serializerやruntime alias方式は型・scope・参照閉包・ブラウザ確認を追加した場合に変更可能。

**未確定：** 対象ブラウザでcolor(srgb …)等が使用できる条件と実際の描画。 / nested theme、透過合成、強制色、表示コントラストの結果。 / CSS数値丸め方と資源上限は実装側で固定する必要がある。

**失敗の形：** ハイフン結合の衝突を後勝ちで隠す / テーマファイルの無言上書き / dimensionを分裂または二重unitにする / 出力から消したpaletteへのvarを残す / fallbackが型不一致を直すと誤認 / graph成功をWCAG合格として出力

**出典：**
- [C02-R1-S04](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/) — 2 Defining Custom Properties; 2.3 Resolving Dependency Cycles; 3 Using Cascading Variables: the var() notation; 3.1 Invalid Variables。W3C Candidate Recommendation Snapshot; not yet Recommendation in observed publication。記録：`researcher-1.json#/sources/3`。
- [R2-S1](https://styledictionary.com/reference/utils/references/) — outputReferencesFilter; outputReferencesTransformed。primary documentation or author-reported incident; not a universal normative requirement。記録：`researcher-2.json#/sources/0`。
- [R2-S3](https://github.com/style-dictionary/style-dictionary/issues/1590) — Proposal; comments 2026-08-27, 2026-08-28, 2026-08-31, 2026-09-18。primary documentation or author-reported incident; not a universal normative requirement。記録：`researcher-2.json#/sources/2`。
- [R2-S4](https://github.com/style-dictionary/style-dictionary/issues/1398) — Description; collaborator comments 2024-11-26 and 2025-01-20。primary documentation or author-reported incident; not a universal normative requirement。記録：`researcher-2.json#/sources/3`。
- [R2-S6](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/) — 2.2 Guaranteed-Invalid Values; 2.3 Resolving Dependency Cycles; 3 var(); 3.1 Invalid Variables。primary documentation or author-reported incident; not a universal normative requirement。記録：`researcher-2.json#/sources/5`。
- [R2-S7](https://www.w3.org/TR/2025/CR-css-color-adjust-1-20251216/) — 2 Preferred Color Schemes; 3.1 Properties Affected by Forced Colors Mode。primary documentation or author-reported incident; not a universal normative requirement。記録：`researcher-2.json#/sources/6`。
- [R2-S8](https://spectrum.adobe.com/page/color) — Solid color background with black or white; Two-tone color pairing。primary documentation or author-reported incident; not a universal normative requirement。記録：`researcher-2.json#/sources/7`。

**反証手順案（全件未実行）：**

| ケース | 手順 | 失敗判定 |
| --- | --- | --- |
| name-collision | a-b.cとa.b-cが同名へ写像される入力を与える。 | 両者を一変数へ上書きする。 |
| permuted-json-key-order | 値とoverride配列順を保ちJSONメンバーの順だけ変え、CSSバイトを比較する。 | 出力順や数値表記が変わる。 |
| dimension-object-split | {value:1,unit:px}の出力を検査する。 | value/unit別変数、object文字列化、単位欠落・二重化。 |
| rendered-contrast-hold | graph正常例のレポートを読み、描画・forced-colors・WCAG欄を確認する。 | 未実行のvisual欄にpass/ACCEPTが立つ。 |

## 独立検査へ残す境界

Researcher-1の44例を全て実装側の期待値合わせに使わない。候補側には正常chain、欠落、循環、型不一致、代表未対応構文、正常sRGB、unitなしゼロ、theme override/循環/role欠落、名前衝突、順序置換の14入力を置く。独立検査側では次の境界から独自入力と期待値を作る。隠されたholdoutや統計的独立性を主張する区分ではない。

| 境界 | 判定の焦点 |
| --- | --- |
| `$root`、未知type、`$ref`外部参照、none/P3 | 未実装を明示拒否し、合法性まで否定しない |
| boolean、非有限数、unit `%`、負duration、alpha/hex境界 | 数値型と値域、規範と製品制約の区別 |
| 親型とalias参照型の相違、group/property参照、self-cycle | 暗黙推論・誤った対象・深さ依存の失敗を検出 |
| darkだけの型変更、必須role継承、theme scopeの一意性 | 合成後のテーマ独立性とartifact対応 |
| A/a、CSS名の区切り文字、filter済み参照先 | 名前写像と参照閉包を検査 |
| ancestor alias、forced-colorsのshadow、型違いfallback | graphをブラウザ/アクセシビリティ証拠にしない |

具体的な予約vector IDはanalysis.jsonのmethod.vector_partitionに残した。ここに並ぶ検査を実施済みとは扱わない。

## 検索の比較

| 役割 | 実施記録 | 強み | 限界 |
| --- | --- | --- |
| Researcher-1 | 3query、検索2call、返却15hit | DTCGの型・値形・規範/例・文面差 | 初回query別hit帰属不明、完全原文なし、Color要約 |
| Researcher-2 | 初期3query＋確認1query、確認9hit保存 | serializer、参照filter、theme/名前/出力先の事故 | 初期全hit未保存、最新package未再現、修正版不明 |

規格側の条件とtooling側の失敗経路は相互補完する。意図的overrideと出力衝突を分け、普遍role一覧や全DTCG対応へ一般化しない。探索の飽和、検索件数による品質優位、ブラウザ実績は主張しない。

## 重複判定

- **現行module「既存部品の再利用・合成・新設」、booking-change例と継承証跡**：保持。今回のtoken検査に置換・吸収・再登録しない。
- **現行module「状態・通知と既存テーマの接続」**：参照元・利用箇所・pairing・意味共有の一般指示を再利用。増分は型/参照/role完全性と機械的診断。
- **Art Direction I-01〜06 / I-14**：CSS変数、面/前景、light/dark公開、radius、初期色、theme反復は参照再利用。新規は限定subset・graph・名前写像・成果物の検査。
- **Art Direction B-01〜04 / B3-03,05,07,11,14**：コントラスト・端末設定・theme管理は再利用。graphの成功からそれらの実画面成功を導かない。
- **round01の部品契約/DOM/フォーカスunit**：そのまま保持。今回の3unitはtokenビルド契約に限定する。

## 対象外と未解決

- DTCG全Format/Color/Resolver準拠の主張、DTCG 2026 preview
- 未実装$ref/$extends/$root/複合型/未知type/外部参照/none/非sRGBの受理
- 新しいpalette・typography・radius・token階層数・普遍role一覧の選択
- 一般的な部品再利用・合成・新設とtheme guidanceの重複登録
- CSSカスケード・利用先全プロパティ・入れ子themeのシミュレーション
- ブラウザ・contrast・forced-colors・WCAGの未実行合格
- registry/skill/checker実装、登録、commit、非公開制御記録出力

- **文面差**：Format §5.2.2のalias参照型と§6.7.3の継承リストが揃わない。 未明示aliasで親型と参照型が違うケースに明示$typeを要求する局所policyを候補とし、原典の解釈確定とはしない。
- **未取得**：両Researcherの完全原文取得は各1回DNS失敗。Color readerは書き換え要約。 reader由来の位置付き研究成果を根拠にするが、完全原文検証済み・未表示箇所まで網羅とはしない。
- **未実行**：本分析のtoken実装・CSSブラウザ・contrast・強制色・WCAG試験は未実行。 verificationは反証手順案であり、実行結果ではない。
- **適用先未提示**：製品role manifest、merge詳細、theme scope、serializerの正確な表記と資源上限。 実装前に局所契約として固定する。既存色や意味の再選定は不要。
- **範囲外**：$ref/$extends/Resolver全体、最新Style Dictionary対応・歴史的issueの修正版。 限定subsetの実装をこれらの完全対応や修正確認へ一般化しない。

## 実行済み／未実行

実行済みは資料読取、指示本文の意味照合、JSON encode/decode、必須schema項目、3unit数、原典IDとrecord位置、44vectorと独立候補IDの確認である。analysis.md/jsonの2ファイルのみ作成した。

token checker、CSS出力実装、ブラウザ、contrast、forced-colors、WCAG試験は未実行。verificationは反証手順案であり、合格証拠ではない。registry変更・skill変更・登録・commitなし。実装側は固定planの7必須caseとrubricで測定し、失敗はREVISE、実行できた限定graph/contractだけをACCEPT候補、visualはHOLDとして扱う。
