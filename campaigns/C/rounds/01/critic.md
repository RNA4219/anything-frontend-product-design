# Round 01 — 独立 Critic / Evaluator

## 結論

**現在の判断: F1・F3・F4は作者の修正後、限定した純粋プローブで再現しなくなった。F2の障害分類も純粋関数と静的読解で修正を確認した。この範囲で未修正の再現済み所見はないが、C-UI-001〜004 のブラウザー／ATに関わる判断は引き続き HOLD。** 初回判定はREVISEで、宣言チェッカーの不正入力受入れ、再表示の古い値、focus結果の確認不足を記録した。作者の13件のPythonテストと6件のNodeテストが成功していることと、初回の反例成立は両立する。以下のF1〜F4の場所と症状は、特に断りがなければ修正前の候補に対するもの。

これは作者から分離された別タスクで実施したレビューである。同じモデルファミリーを使っており、人間による客観的評価や異なるモデルによる評価ではない。実装・Registry・作者のテストは変更していない。ブラウザーを再試行しておらず、環境制約の回避もしていない。

## 実行した独立プローブ

実行コマンド:

```sh
python3 campaigns/C/rounds/01/critic-probes.py > campaigns/C/rounds/01/critic-probe-results.json
```

初回の終了コードは **1**。これは例外や環境エラーではなく、意図した反例が再現されたことを示す。Pythonから候補の `check()` を呼び、Nodeでは実HTMLのmodule scriptを抽出して最小限のDOM代役でアプリ側ハンドラだけを実行した。ブラウザーの代替検証としては扱わない。

結果:

- `submit_policy` が `[]`、`{}`、`true`、`0`、`null`、`"incldue"` の6例とも、native-disabledフィールドなのにエラー0件。
- 対照として、正しい `submit_policy="include"` と `separate_serialization=false` は `DISABLED_PAYLOAD` で拒否、同trueは受入れ。
- 元の候補宣言はエラー0件。反例が最初から壊れたfixtureによるものではないことを確認。
- 実HTMLハンドラで、未選択の確定は実行せず、選択後の確定回数は1、起動元削除後のfallback呼出しは発生。
- 確定後の再表示で、ページの予約は12月10日に変わるが、ダイアログの「変更前」は12月8日の固定表示。
- 有効な起動元が残っている一方でactiveElementがbodyである入力状態では、closeハンドラは何も補正しない。この状態を実際のUAが生むかは未実証。

完全な出力は `critic-probe-results.json`、再実行コードは `critic-probes.py` と `critic-probes.mjs` にある。

## F1 — 不正な送信方針で fail-closed を迂回できる

**重要度: high（評価ゲートの正しさ）。** 場所: `modules/ui-engineering-design-system/checks/contracts.py:37–44,61–68,111–113`。

`submit_policy` が型検証の対象から漏れており、値が厳密に `"include"` であるときだけnative-disabledの送信脱落チェックを行う。上記6例で `check()` は空配列を返す。その結果、CLIの既存分岐では `PASS_DECLARATIONS_ONLY`、終了0になる。

再現は、候補のreadonly予約番号フィールドをコピーし、`availability="native-disabled"`、`submit_policy=[]` とするだけでよい。別シリアライズ計画は設定しない。配列は宣言例の送信方針として解釈できないが、検査を通る。

影響は、不正な契約を「宣言上の矛盾なし」と報告し、必要値が脱落する条件を検査せず進めてしまうこと。凍結したevaluation-planのoracle 11「invalid input structuresでPASSしない」に直接反する。

**修正:** `submit_policy` を明示した型と許容値で検証し、不明値・タイプミスを拒否する。必要なフィールド種別では方針の欠落も拒否するか、未確認として明記する。型検証は状態分岐に入る前に行う。上記6例と既存のinclude対照例を回帰確認する。

## F2 — ブラウザー検査の製品障害が BLOCKED に分類される

**重要度: medium。** 場所: `modules/ui-engineering-design-system/tests/browser_contracts.py:34–65,66–69`。

`AssertionError` 以外の例外を一律にBLOCKEDへ変換する。たとえば、配信・起動成功後にmoduleの不具合でモーダルが開かず `locator.press()` がタイムアウトする場合も、環境制約と同じBLOCKEDになる。これは例外分岐の直接読解で確認した所見で、ブラウザー障害をここで実際に発生させたとの主張ではない。

影響は、将来このsuiteが起動できた際に、コードの回帰を「実行できなかった」に分類して隠すこと。凍結oracle 12の起動不能／URLポリシー起因のBLOCKEDと、起動後に観測した部品障害を区別できない。

**修正:** import・配信・launch・接続確立を準備フェーズとして明示する。そこで確認できた環境不能をBLOCKEDとし、対象ページのロードが成立した後の操作・スクリプト・locator失敗はケース名とともにFAILまたはERRORとして記録する。ページ読み込み自体の失敗も、観測根拠なしに環境原因と決めない。

## F3 — 確定後の再表示で「変更前」が古いまま

**重要度: medium。** 場所: `modules/ui-engineering-design-system/examples/booking-controls.html:34,53–55,59–63`。

12月10日を選んで確定すると `#current` は変更されるが、ダイアログ内の `変更前: 12月8日 14:00` は静的文字列である。再表示してもその文字列を更新する経路がない。独立Nodeプローブは実ハンドラで確定・再表示を実行し、ページの現在値と静的表示の差を記録した。

影響は、同じ部品を繰り返し使う利用者が、現在の予約日を誤認すること。単発の確定回数や古いreturnValueだけを検査する作者のテストでは発見できない。ここで必要なのは新しい予約業務ポリシーではなく、すでに確定した同じ値を2箇所の表示へ反映すること。

**修正:** 確定済みの値を単一のアプリ状態として保持し、一覧と再表示時の「変更前」をそこから描画する。再表示後に取消しても、その確定済み値が保持されることを確認する。

## F4 — Registryの復帰結果確認がHTMLへ接続されていない

**重要度: medium、ブラウザーでの発生条件は未確認。** 場所: `modules/ui-engineering-design-system/examples/booking-controls.html:67–70`。関連する要求: `registry/C/skills/C-UI-004.json` のdecision_rules第5・6項、`references/component-contracts.md` の第4節。

Registryは実際のactiveElementで復帰結果を確かめると指示しているが、HTMLは起動元の接続・disabled・hidden/inert・矩形だけを判定する。起動元がそれらを通過すれば、ブラウザーが目的の復帰を達成していなくても処理が終わる。Nodeプローブでは、bodyにfocusがある状態を供給するとfallback呼出しが0だった。

この証拠は**アプリの分岐不足**を示す。特定のブラウザーや入力方式でこの失敗状態が起きることは示していないため、アクセシビリティ不適合の実証として扱わない。

**修正:** close後の実際のfocusを観測し、目的の復帰が成立済みなら動かさず、必要な場合だけ担当レイヤーが利用可能な起動元または指定fallbackへ移す。フォーカス対象の変更を無条件に追加しない。native復帰とのタイミング、別モーダル、非モーダルの外部作業は引き続き実ブラウザーで確認する。

## 出典と指示の整合性

保存済み原典readerの次の範囲を直接確認した。

- Researcher-1の `sources/chase-response-01-web-excerpt.txt`、HTML closeアルゴリズムL889〜L917。modalまたは内部focusという復帰条件、closeイベントのtask化の記述は分析と整合する。
- Researcher-2の `reader-open-3.txt`、APG L32〜L73。初期focusは内容に依存し、起動元消滅や次の作業への移動という例外がある。候補は「常に先頭button」と一般化していない。
- Researcher-2の `reader-open-4.txt`、USWDS #6786 L156〜L175、#6703 L165〜L186、Adobe #2763 L153〜L171。背景復旧と起動元lookupの分離、focus担当の重複、focusableとtabbableの違いは分析の提案と対応する。

これらは保存済み部分抜粋であり、原典全文の取得成功や、第三者の追試成功を主張しない。本文は規範の事実、非規範の助言、独自実装提案をおおむね分けており、この限定レビューでは重大な出典の逆転を見つけなかった。すべての規範文の全文監査ではない。

## Art Directionとの重複・複雑さ・層間影響

Art Directionの `g-state-forms.md` のG4-17、G6-12/24、G7-05/14/25、G9-01/03/04、G10-13、`e-accessibility.md` のE2-01〜06、`i-components.md` のI-09〜11は実在し、参照内容は一致する。Cの追加は、状態・ガード・送信・cleanupとfocusの担当を反証可能な契約へまとめた部分であり、独立した配色や一般的なWCAG一覧の再実装は見つけなかった。

3つの小さい純粋helperと宣言検査は、この範囲では過度な新規フレームワークではない。ただし `needsFallback` はHTMLに接続されていないため、helperの成功を試作の復帰検証へ転記してはならない。F3の表示同期はBの新規業務ポリシーを創作せずに修正できる。F2はDへ渡す採否証拠の分類に影響する。

## 残る検証範囲

ブラウザーとATはBLOCKED／NOT_RUNのまま。独立プローブはnative key activation、FormData、focus containment、レイアウト、AT発話、実イベント順序を証明しない。作者のbrowser suiteにも、成功時のEnterとpointer確定、Shift+Tab、起動元削除後のEscapeの直接ケースがない。初回は背景復旧を `#outside.is_enabled()` だけで検査していた。最終修正で実入力と値の照合が加わったが未実行であり、AT公開状態も未確認。手動確認表に書かれている項目も、実行して初めて証拠になる。

全件の判断は `critic.json` に保存した。修正後も、純粋テストの成功だけを根拠にC-UI-001〜004のブラウザー／AT挙動をACCEPTへ変更しない。

## 作者修正後の限定再検査

作者が送信方針の型・列挙値チェック、確定済み日時からの再描画、close後のactiveElement確認を追加した後、同じPythonプローブを再実行した。Node側は、新たな `#before` の実際のtextContentを読むように更新し、外部の有効なfocusを維持する対照例も追加した。初回の結果ファイルは上書きしていない。

```sh
python3 campaigns/C/rounds/01/critic-probes.py > campaigns/C/rounds/01/recheck.json
```

終了 **0**。不正な6方針をすべて拒否し、include+別送信計画の有無の対照結果は維持した。再表示後の「変更前」と現在値は双方12月10日だった。供給したbody-focus状態からの救済、削除された起動元のfallback、有効な外部focusの維持もアプリハンドラの範囲で確認した。F1とF3はこの再現範囲で修正確認、F4は分岐追加を確認したがUA挙動は未確認。

続いて作者がF2を修正した。`browser_contracts.py` をmainを呼ばずにimportし、setupはBLOCKED、navigation・interaction・unknownはERROR_TEST_EXECUTIONとなることを独立確認した。phase/case設定と例外処理への接続、実行エラーの終了1もコード上で確認した。新たなサーバーやブラウザーの起動は一切行っていない。この結果を `recheck.json` のbrowser_reporting_recheckへ追記した。
