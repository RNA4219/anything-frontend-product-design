# R03 初回修正版の限定再確認

**REVISEを継続。F1・F3とF2のpending分岐は解消したが、F2と同じ終端結果保持の例外経路に不整合が残る。**

評価module SHA-256: `8a08e09d10659e436e2425d698e103c851a5880ed31d686856a411204882e716`。
HTML: `84a92808062a8f903e2a64a9cb33041b367f9fcaff0102297cf6ce3f39779a9f`。

| 再確認 | 結果 |
| --- | --- |
| 固定13 | 13/13 |
| 初期の代表DOM | 8/8 |
| 初期の探索DOM | 2/2 |
| 初期の追加状態 | 6/6 |
| 修正箇所に限定した追加確認 | 2/3 |

RC02では復帰証拠のowner/resource/operationの各不一致を拒否することを確認。RC03では実DOMイベントで未送信復帰、応答喪失後の送信済み、成功確認済み、別accountでの説明除去を確認した。

## 残るF2の例外経路

`resume-and-conflict.mjs` 68行のresume catchが、保持済みoutcomesを確認せずunknownへ戻す。再現は初期X03と同じ同一operationの並行update/lookupだが、終わりに古いpending応答でなく照会transportエラーを返す。

1. commit応答を保留する。
2. resumeから同じoperationのlookupを開始し、その応答を保留する。
3. updateの成功応答を先に返す。旧epochのためviewへは直適用せず、outcomesに保持される。
4. lookupを通信エラーでrejectする。
5. `phase=unknown`、`operationOutcome=null`、`operationResult=null`になる。

修正後も求める条件は初期F2と同じであり、新しい固定criterionを追加したわけではない。修正が入ったacceptの隣接catchに終端優先が及ぶかという具体的な残リスクを確認した。成功を受信していない通常のlookup失敗は、引き続き正しくunknownであるべき。

実行証拠は `focused-recheck.json:RC01-TERMINAL-SUCCESS-BEFORE-LOOKUP-REJECTION`。修正はこのcatchでも同じ相関済みのterminalを優先し、current-view guardを維持すること。

追加の全般探索、source再取得、実ブラウザ起動は行っていない。
