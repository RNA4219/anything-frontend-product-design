# SESSION C round 03 — 独立Critic初期評価

## 結論

**固定候補の純粋な入力モデル検査器はREVISE、C-UI-008 / C-UI-009のUnit全体はHOLDが妥当。** 初回の127ケースは118一致・9不一致だった。9件は4欠陥群に集約できる。幾何計算の閾値と証拠ラベルの分離には、この検査集合で不一致はなかったが、既知FAILをHOLDへ弱める処理とCLIの入力・出力例外は修正が必要である。

この文書は初期固定候補への評価であり、修正版の再検査は別の `recheck-results.json` / `recheck.json` / `recheck.md` に保存する。初期不合格を修正後の成功で上書きしない。

## 固定対象と検査方法

- 事前基準は `plan.json` と `evaluation-plan.md`。候補は `candidate-snapshot.json` の8ファイルすべてと一致した。初回127ケースの実行前後でもハッシュは不変だった。
- 中核 `layout.py` の初期SHA-256は `da066ac8c6a2543d5dbfa0c49ccceeef9a3082af7aa0d791b86f3988ec888670`。元snapshotに含まれていない2例示JSONとC-UI-008/009も、Critic開始時のハッシュを `initial-results.json` に記録した。
- 新規 `independent-probes.py` からPython CLIへ入力した。既存testを再実行して独立検証とはしていない。Decimal字句をfloatへ変換せず、対角接触・1e-18摂動・全方向・未知形状・例外条件・保持・形式を別の期待値で検査した。
- 124ケースはCriticが作成。巨大指数の3ケースは、実行前に親が発見を通知していたため親発見の再現として分離した。独立発見は3群、親発見再現は1群である。
- 初回127 CLI実行に加え、Unicode2ケースだけを元stdout/stderrのhex記録用にもう一度実行した。異なる検査ケースは127、初期CLI総起動は129である。
- 同一基盤モデルの別タスクであり、別モデルや外部評価者による再現ではない。実装と既存testを読んだ後に作成したため盲検でもない。この独立性の限界を残す。

入力全文、期待値、stdout/stderr、実際のJSON、終了値、不一致、対象・スクリプトのハッシュ、再現コマンドは `initial-results.json`。元のUnicode出力bytesは `initial-unicode-byte-evidence.json` に保存した。

## 実行結果

| 分類 | 件数 | 不一致 | 確認した点 |
| --- | ---: | ---: | --- |
| 幾何 | 34 | 0 | 24境界、23.999、18桁小数、対角接触、全実矩形、幅広薄型、負座標、未知形状、重なり、不完全一覧 |
| 例外 | 33 | 2 | 全名称、根拠不足、矛盾、自己/3点循環、障害物保持、size PASSでも不正な条件型を拒否 |
| リフロー | 24 | 2 | 保持、代替経路、局所例外、隣接本文、320/256、page_overflowからの誤判定防止 |
| 証拠由来 | 10 | 0 | 5種のevidence申告×2モデルでもbrowser/AT/WCAG成功へ昇格しない |
| 入力・CLI | 26 | 5 | 型、有限・精度・寸法・行数・ファイル上限、重複、混在座標、巨大指数、Unicode |
| **計** | **127** | **9** | **118一致** |

24未満の孤立対象でもspacingを満たせばMODEL_PASSになるため、23.999を自動的にMODEL_FAILとするoracleにはしていない。確認したのは `size=UNDERSIZED` を保持することである。サイズを満たす対象に不要なspacingを追加要求することもなかった。

## 重大指摘

### C03-CR-01 — UA例外の成立不能が一条件だけで確定しても、もう一条件がないと既知spacing FAILをHOLDへ上書きする。

- **位置**：`modules/ui-engineering-design-system/checks/layout.py` 初期版299〜300行、targets / UA exception review。
- **発見区分**：independent_critic。
- **入力**：a=[-1,-1,2,2]、obstacle=[10,-12,24,24]。aの例外はuaでauthor_resized=trueのみ、またはua_determined=falseのみ。
- **期待**：MODEL_FAIL、a.status=FAIL_MODEL_SPACING、exception=CONDITIONS_CONTRADICT_CLAIM。
- **実際**：MODEL_HOLD、a.status=HOLD_EXCEPTION_REVIEW、spacing=FAIL、exception=MISSING_CONDITION_OR_EVIDENCE。exit=3。
- **根拠**：initial-results.json / evaluation-plan.md §4 / C-S007 SC2.5.8 User Agent Control / C-S033 Exceptions / User agent control / references/layout-contracts.md §3。
- **影響**：サイズ条件を満たす隣接対象だけを用いた反例なので、全体にほかのFAILはなく、確定欠陥が未確定扱いになる。条件を省略するほど評価が弱くなる。
- **修正方向**：ua_determined=false または author_resized=true の明示値を不足条件判定より先に不成立として扱い、既知spacing FAILを保持する。

再現：

```sh
python3 campaigns/C/rounds/03/independent-probes.py --case E-ua-partial-contradiction-author_resized --stdout
```

### C03-CR-02 — availability=missing という欠落申告を、evidence_refが空または空白という理由で未観測HOLDへ消し込む。

- **位置**：`modules/ui-engineering-design-system/checks/layout.py` 初期版165〜168行、reflow / required-item verdict。
- **発見区分**：independent_critic。
- **入力**：report-editorの必須export-reportをavailability=missing、evidence_ref=""または"   "とする。page_overflow=false、両regionのreflows=true、inventory_complete=true。
- **期待**：MODEL_FAIL、export-report.status=FAIL_REQUIRED_ITEM_LOST。参照不足は別欄で残す。
- **実際**：MODEL_HOLD、export-report.status=HOLD_ITEM_UNOBSERVED。exit=3。
- **根拠**：initial-results.json / evaluation-plan.md §1 / plan.json rubric 1,4 / references/layout-contracts.md §4 MODEL_FAIL優先。
- **影響**：明示的な欠落と、単に観測していないunknownが同じになる。参照補記待ちにより、既知の操作欠落への修正判断を遅らせる。
- **修正方向**：itemが存在しavailability=missingなら欠落FAILを優先し、証拠参照の有無は別の未充足情報として保存する。unknownや存在しないitemはHOLDのままにする。

再現：

```sh
python3 campaigns/C/rounds/03/independent-probes.py --case R-known-loss-empty-ref-0 --stdout
```

### C03-CR-03 — 巨大指数のJSON数値をDecimalが解釈する段階でdecimal.InvalidOperationが未捕捉になり、構造化INPUT_ERRORを返さない。

- **位置**：`modules/ui-engineering-design-system/checks/layout.py` 初期版352〜357行、main / parse_float and error handling。
- **発見区分**：parent_discovery_independently_reproduced。
- **入力**：rectのwidthへ1e99999999999999999999999999999999、その負指数版、0の巨大指数版を渡す。
- **期待**：INPUT_ERRORのJSON、exit=2、Tracebackなし。
- **実際**：stdout空、decimal.InvalidOperationのTraceback、exit=1。
- **根拠**：initial-results.json / parent-extra-probe-initial.json（親発見を別管理） / evaluation-plan.md §3 / references/layout-contracts.md §4 数値・CLI契約。
- **影響**：INPUT_ERRORとMODEL_FAILの終了値の区別が失われる。機械処理側がJSONを読めず、診断の位置・理由も欠落する。
- **修正方向**：数値字句の変換限界を構造化入力エラーへ変換し、出力契約を維持する。

再現：

```sh
python3 campaigns/C/rounds/03/independent-probes.py --case I-huge-positive-exponent --stdout
```

### C03-CR-04 — JSONエスケープで入力した孤立surrogateをensure_ascii=Falseでstdoutへ出すと、出力不能または無効UTF-8になる。

- **位置**：`modules/ui-engineering-design-system/checks/layout.py` 初期版358〜358行、main / JSON serialization to stdout。
- **発見区分**：independent_critic。
- **入力**：正常24×24対象のcontext.idをJSONの\ud800または\udcffにする。
- **期待**：非対応文字列としてINPUT_ERROR/exit2、または安全にエスケープされたMODEL_PASS/exit0の有効UTF-8 JSON。UI/WCAGはHOLD/NOT_ASSESSED。
- **実際**：high: UnicodeEncodeError、stdout空、exit1。low: exit0だがstdoutに無効UTF-8の0xFF。
- **根拠**：initial-results.json / initial-unicode-byte-evidence.json（元stdout/stderrをhexで保存） / evaluation-plan.md §3 / references/layout-contracts.md §4 CLI契約。
- **影響**：同じ文字列形式でクラッシュと壊れた成功レスポンスが分かれ、JSON消費者が結果を読めない。
- **修正方向**：非対応Unicodeを明示拒否するか、ensure_ascii等の安全な直列化でUTF-8/JSON出力を保証する。

再現：

```sh
python3 campaigns/C/rounds/03/independent-probes.py --case I-lone-surrogate-high --case I-lone-surrogate-low --stdout
```

上のコマンドは固定候補用である。修正版に実行する場合だけ `--allow-revised` を付け、別ファイルへ記録する。期待値は変更しない。

## 出典・主張・例外の照合

[W3C Target Size解説](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)については、公式ページから追跡された[固定repository source](https://github.com/w3c/wcag/blob/2766fae25fc8286f60181d655115cba054b797e1/understanding/22/target-size-minimum.html)を私有領域で読んだ。SHA-256は `ede35144e897503a5970d1e33a6bfe6aa3dd1e7476ee47bc1d10e08fa672cfb0`。実効領域内の24×24、円と他の実対象、UA条件などの説明と候補契約は整合する。ただし本文の全要件が実装されているという意味ではない。第三者原文はこの報告や公開ファイルへ転載していない。

接触のstrict `<`は、公式図5・図10の寸法と間隔から導いた限定モデルの推論として記載されている。規範本文が数式やepsilonを定義したとの誤表示はなかった。対角方向でも円どうしの距離二乗576、円と矩形の最短距離二乗144の等号と微小な侵入を分けられた。

[Reflow解説](https://www.w3.org/WAI/WCAG22/Understanding/reflow)とC-S007の該当箇所は、位置付き研究記録および私有readerと照合した。320/256、情報・操作保持、二次元性の局所性、page overflowだけを結論にしない説明が契約と観測protocolに保たれる。局所scroll containerを一律の規範必須条件にはしていない。規範全文を今回新規に完全取得した、生成済み公開ページと固定repository fileがbyte一致するといった主張はしない。

BCR、点sampling、reading-flow、pointer/hover能力queryの資料については、研究記録から契約・登録Unitへの意味と制約の引継ぎを読取確認した。現在のブラウザ対応や実APIの挙動を独立に再現したわけではない。

## 誤ったPASS、HOLD、FAILの区別

この集合では、既知の幾何・保持欠陥をMODEL_PASSへする反例は出なかった。確定FAILをHOLDへ弱める4ケースと、CLI診断破損5ケースは発見した。形式が正しい例外でも根拠の真偽は検証していないためHOLDを維持すべきであり、自己参照や3点循環で例外を自動承認することはなかった。

サイズを満たす対象の不要な例外は `NOT_NEEDED_BY_MODEL` と記録される。これは例外の承認ではない。条件の型が不正なら、サイズが24×24でもINPUT_ERRORになった。一方、型は正しいが矛盾する不要な申告の診断を詳しくする余地はある。今回は候補文書が不要例外の扱いを明示しているため、これを新しい必須要件として不合格にはしない。

表の例外は別regionの非例外本文のFAILを隠さず、例外targetも他対象の障害物一覧に残った。未知・clip・overlap・不完全一覧は対応範囲外/HOLDに保たれ、非矩形そのものをWCAG不適合とはしていない。

## 実作業での価値と適用限界

独立モデルでは予約ではなくreport-editorの情報・操作IDを使った。必要なexportが失われた場合、例外のある表に隣接する本文がreflowしない場合、広く薄い操作対象へ円が入る場合を診断できる。入力モデルが特定の予約IDやHTML構造へ固定されていない点は確認できた。現場では、測定・観測を入力する前の形式検査と、明示的な幾何関係の確認に使える。

`examples/reflow-targets.html` は静的な記述を確認しただけである。長いラベルの描画、ラジオの実効領域、表のスクロール、submit/resetのactivation、フォーカス、400%や文字200%、入力切替、AT発話は未実行。合成モデル内でlong-labelの保持を申告しても、長いラベルの実画面を検証したことにはならない。例示JSONはHTMLから抽出していないと明示され、CSSの2.75remを実測済み44 CSS pxとして扱っていない。

## Art Directionとの重複

`../art-direction/references/e-accessibility.md` と `../art-direction/references/visual-composition.md` を読んだ。320/256と例外はE-02、小targetの例外はE-07、focus完全/部分遮蔽はE-03/E-04、順序や狭幅での意味・操作名の保持はE4-07とvisual-compositionに既にある。今回の増分は、必要ID・局所region・実効target・証拠由来の入力契約、exact arithmetic、衝突対の診断、例外根拠、未観測時のHOLDを運用できる形にすることにある。新たな視覚原則を発明したとして数えるべきではない。

A/Bが決める必要情報と順序、既存C-UI-001〜004の意味・イベント・keyboard/focus、Dの実画面採否の責務は残される。この分担であれば、Cの実装・検査単位として追加する意味がある。

## 採否提案と次の確認

1. 初期候補の純検査採用はREVISE。上の4群を修正し、同じ127ケースを同じ期待値で再検査する。
2. 修正版がすべて一致した場合は、供給された入力モデルの形式・有理数幾何・明示的保持申告のprecheckという範囲に限って採用を提案できる。
3. C-UI-008とC-UI-009の全体はHOLDを維持する。実効領域と矩形の一致、実reflow、実操作、順序、focus、ATが今回の実行では確認されていないためである。

ブラウザ、サーバー、CDP、UI操作、DOM double、ATは起動していない。拒否された操作の代替経路も使っていない。実装変更は親担当とし、Criticは検査sourceと結果・報告だけを書いた。
