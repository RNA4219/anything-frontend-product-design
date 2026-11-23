# SESSION B Round 02 独立Critic — 修正版判定

## 結論：ACCEPT（明記したfixtureと原典境界に限定）

初回は **REVISE** とした。非該当になった配送先エラーが確認到達を妨げるE01と、3.3.7の実行用文言E02は親が修正し、独立Criticが同じDOM経路と文言を限定再確認して解消した。B-IU-004/005/006は、この検証scopeで採用できる。

**固定16ケースの初回結果は16/16のまま保存。探索欠陥を後付けの第17ケースとして採点していない。** 今回は候補と意図的な故障注入コピーの比較であり、LLM生成baseline比較、Skillの因果的改善率、客観的UX優位を示すものではない。

## 独立に実施した試験と結果

| 検証 | 対象 | 結果 | 証拠 |
|---|---|---|---|
| 事前固定F01–F07/U01–U09 | 初回候補 | 16/16合格、freeze hash一致 | frozen-suite.json |
| 独立故障注入16種 | 初回候補から作成した負例 | 対応する16ケースが16/16検出 | independent-checks.json、negative-controls/ |
| Registry checker | 初回Registry | エラー0 | registry-checker.json |
| 原典capture整合 | 研究者の10capture | SHA-256 10/10一致 | independent-checks.json |
| jsdom実イベント代表経路 | 初回HTMLと実module | 8/8合格 | dom-events.json |
| 探索E01 | 初回HTMLと実module | 非表示addressエラーが残り確認不可 | dom-events.json:exploratory[0] |
| E01限定再確認 | 修正版HTMLと実module | 確認へ進み、非該当エラーなし | recheck-identified-defect.json |
| E02文言照合 | 修正版reference/Registry | 3.3.7の要件と3例外を保持 | recheck-identified-defect.json |

代表DOM経路は、拒否→修正→確認→完了、配送分岐、応答喪失から同一操作照会、補償pending→failed、pending→restoredと残存影響、期限切れ、revision競合、局所Undo。jsdom 26.1.0で同じHTMLのclick/changeハンドラを実行し、ESM importだけを実moduleのexport注入へ置換した。

親が報告した修正版固定16/16、探索回帰3/3（保存初回版2/3）は独立再実行数に含めない。親の依頼に従い再確認は既知E01のDOM経路と文言差分に限定した。親の追加回帰コードと結果は読み、固定16ケースと別suiteであることを確認した。

## E01：非該当addressエラーの残留 — 修正確認済み

**初回位置：** `task-flows.mjs:14,17–22`、`repair-and-undo.html:30–31`。

**再現：** shippingのaddressを空にする→「内容を確認する」で住所必須エラー→deliveryをpickupへ変更→再び「内容を確認する」。初回はaddress欄がhidden、実効回答にaddressなしにもかかわらず`errors.address`が残り、`phase=editing`で確認panelへ進めなかった。

**影響：** 不要な住所を入力する迂回か分岐を戻す操作が必要になる。通常の完了経路を止めるため修正対象とした。今回データ損失・誤送信は観測していない。taskの住所条件とreferenceの不要な再入力を求めない方針、およびB-S205:L417,L424–L429に対応する探索所見。

**原因と修正：** `set`が変更fieldのエラーだけを削除し、`review`は古い非該当エラーを残していた。修正版`set`は現在の`effective()`に存在しない項目のエラーだけを除く。初回とのmodule差分がこの変更だけであることをbytes比較で確認した。有効項目のエラーを一律初期化する修正ではない。

**修正版の同一DOM観測：** `phase=review`、住所はhidden、review panelは表示、`errors.address`なし、実効回答にaddressなし、draftの空住所と既存氏名/emailを保持、提出呼出し0。再現コード`recheck-identified-defect.mjs`、結果`recheck-identified-defect.json`はexit 0。

## E02：3.3.7の指示の強さ — 修正確認済み

`forms-and-review.md:25`の「検討する」は「3.3.7に従い、自動入力または選択手段を備える」へ変更された。直後のessential・security・情報無効という3例外を保持し、Registry B-IU-005とnormative B-S201:L1373–L1381に揃った。B-IU-006への非該当エラー規則は`campaign_inference`で、探索ケースIDも固定16件と分けられている。

## 原典の照合結果

| 論点 | 独立に確認した境界 | 原典位置 |
|---|---|---|
| 3.3.4 | AAの対象列挙と3代替の少なくとも1つ。不可逆限定・3手段全部・毎操作モーダルの強制なし。3.3.6 AAAと区別 | B-S201:L1328–L1341,L1350–L1363 |
| 3.3.7 | 同一process、既入力/既提示情報、自動入力/選択、3例外、essential/processの定義を保持 | B-S201:L1373–L1381,L1945,L2277 |
| 3.3.1/3.3.3 | 項目識別・テキスト説明と修正案を分け、修正案の例外で3.3.1全体を免除しない | B-S201:L1311,L1327 |
| 規範/解説 | Understandingをinformativeと区別。技法を唯一手段にせず、セッション間保存義務やPIIの包括例外を作らない | B-S201:L1464; B-S202:L2,L42,L55; B-S203:L2,L47–L64 |
| GOV.UK | 正常/誤入力の保持、入力で直せない問題の分離、既入力で変更して確認へ復帰は政府サービス向け設計ガイド。WCAGそのものとはしていない | B-S204:L137–L155; B-S205:L415–L430 |
| 補償/局所Undo | 補償の業務依存性、同時更新、失敗、全状態復帰非保証を保持。単純局所編集に期限/revision/分散照会を無条件要求しない | B-T301:L41,L53–L58,L64–L91 |
| Win7旧資料 | 未更新の歴史的参考に限定。現行rule、98%採用閾値、人間の効果量へ転用なし | B-T302:L31–L35,L69,L80–L90,L156 |
| Cloud Storage | 新世代、IAM/通知等の残存効果、非同期受付後失敗を製品固有の反例として扱う。不整合箇所を採用根拠から除外 | B-T303:L235–L243,L314–L315; B-T304:L344–L345,L402,L406,L426; B-T305:L302,L318–L336,L360–L361 |

保存した原典captureを直接読み、findingsのhashとも照合した。raw HTML全文の完全性、未取得の個別技法、現在のAPI実行を確認したとは扱わない。

## 未検証と比較の限界

実ブラウザ、視覚/レイアウト、実キーボード、支援技術、WCAG全体適合、人間の理解・誤操作率・所要時間、実backend・永続化・権限・料金、原子的revision防止、全before-stateの完全性、補償の実際の部分結果は未検証。jsdomの状態/イベント確認をそれらの試験と呼ばない。

同一モデルの別文脈による独立Critic。異なるモデルや人間の評価としていない。16故障の検出はその具体的故障への感度であり、全故障の網羅性や実利用での優位性ではない。R01ブラウザ制約を回避せず、候補変更・子agent・公開・実API呼出しは行っていない。

必要な差分と再現が確認できたため、任意網羅試験を増やさず終了する。

## 保存した判断とhash

- 初回REVISE：`review-initial.json` / `review-initial.md`
- 修正版ACCEPT：`review.json` / `review.md`
- 限定再確認：`recheck-identified-defect.mjs` / `recheck-identified-defect.json`
- 初回試験・故障注入再現：`run_independent_checks.py`
- 全成果物hash：`artifact-hashes.json`

初回module SHA-256：`3c38c312ce87e6b5ac84d532042344744737792fe4775cd6d9744ac597105c07`

修正版module SHA-256：`668a67ab761a2c021a8ea3d1afb51c134a8a350a8e135fe1dd8f9743be8b5b40`

HTML SHA-256（初回と同一）：`d93571557e22bb4742cc743b4ad2a3fb8d319393cfbfdf451f48601a328ce1a4`

固定test SHA-256（初回と同一）：`804a03de301db48aaaad3100c162cfdb7171cc0781c73fc1f8d03b99c7538957`
