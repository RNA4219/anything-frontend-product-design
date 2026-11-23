# 一括操作の部分結果を、対象ごとの次の行動へつなぐ

B-IU-009。複数項目への同じ確認済み変更で、部分成功・未処理・結果欠落・回復を扱う。
最初に原子性と完了の契約を確認する。項目単位の回復は、その契約が許す範囲で使う。
この手順は、API固有のwire形式やSDKのschedulerを実装する指示ではない。

## 1. 結果を分類する前に契約を分類する

| 契約 | 判断と次の手順 |
| --- | --- |
| 全件一体の原子的処理 | 全体の成否と診断を分ける。全体失敗内の「項目エラーなし」を個別commit成功にせず、勝手に一部だけを再送しない。応答喪失なら全未適用とも断定しない。 |
| 非原子的・部分成功が許される | 元の選択集合を保ち、項目別結果と回復subsetを作る。成功済み項目を回復の新規送信へ混ぜない。 |
| 非同期受付 | 受付と終端を分ける。まだ終端でないOperationの失敗mapが空でも全変更成功ではない。 |
| 契約が分からない | 原子性・成功・未適用・回復能力を確認する。その確認なしに安全な一括再送や部分成功を保証しない。 |

AIP-233は同期／非同期のbatch create、DynamoDBは非原子的BatchWriteItemと原子的TransactWriteItemsをそれぞれ規定する。
これらを同じ一括処理として扱わない。上表のUI判断は、それらの契約を組み合わせたCampaignの推論である。[S1][S2][S3]

## 2. 利用者の選択と、識別子の役割を固定する

最初に選択した集合S、確認した変更内容、表示名、安定した対象IDを保持する。
返信数、filter、並べ替え、transport分割数から選択totalを作り直さない。空なら送信せず、成功した変更も作らない。

| 役割 | 確認すること |
| --- | --- |
| 選択したrecord ID | どの対象の変更か |
| response correlation key／元request index | どの送信要素に対する返信か |
| attempt ID | 今回の送信試行か、古い試行か |
| idempotency key | 同一意図のどの内容・範囲・保持窓を重複抑止するか |
| durable operation reference | どの操作を後から照会・取消できるか |
| diagnostic Request ID | 支援・診断の参照であり、照会endpointの存在まで示すか |

同じ文字列でも、同じ役割とは限らない。Graphのbatch idはbatch内の相関値であり、AIPのrequest_idの
冪等性目的や、DynamoDBの診断Request IDと混同しない。[S4][S5][S6]

順不同replyを到着位置で対象へ割り当てない。一方、AIP-233の元requests配列indexは明示された相関契約なので、
送信時のindex→選択ID対応を使える。UIの現在の並べ替え位置へ付け替えない。[S1][S4]

## 3. 返信を、証拠のある結果にだけ変換する

1. envelope受付と項目の業務結果を分ける。外側200／acceptedだけで全成功にしない。
2. 項目と該当試行の相関を確認する。未選択ID、相関不一致、同じ返信内の矛盾を別項目へ転記しない。
3. 成功、確定未適用、取消、前提未成立の未実行、処理中、結果未確認を区別する。
4. 欠落や通信喪失は、[B-IU-001](async-outcomes.md)へ元操作参照と内容を渡す。照会missは未適用の証拠にしない。
5. 正しく確認した結果は保持する。[B-IU-007/008](resume-and-conflict.md)に従って、旧試行の証拠を残すことと、
   現在の試行・viewへ反映することを分ける。遅いpendingや照会例外で既知終端を取り消さない。

完全で有効なUnprocessedItems応答から処理済み集合を導けるAPIでは、その契約を利用できる。
個別成功行のない全APIへ「返信欠落だからunknown」を強制しない。応答そのものを失った場合には、空集合を補わない。[S2]

HTTPの失敗分類だけから未適用を作らない。Graphには特定endpointの503後に作成済みになる既知問題があり、
DynamoDBもwriteの500で成功／失敗の両方があり得ると説明する。これは全503/500の結果を一律に決める規則でもない。[S6][S7]

## 4. 回復を選ぶ時点で、対象を再評価する

今回のfixtureで新しいattemptを送るretryは、指定されたS内の項目について次をすべて確認する。

- 権威ある未適用が分かっている。
- 再試行可能な理由である。
- 必要な最小待機時間を満たす。
- 宣言された前提項目が成功している。
- 現在の権限・内容・対象が、この操作を許している。
- 同じ項目が、別の重なる呼出しで既に送信開始されていない。

表示済みの候補一覧だけを許可証にしない。実行時の適格subsetを作り、成功済み、恒久失敗、待機中、unknownへ新しい
操作を送らない。unknownの安全な**同一key・同一意図**のreplayは、[B-IU-002](async-outcomes.md)の条件で別途判断する。
fixtureの新attempt IDを、本番APIの論理要求の冪等性キー変更へ読み替えない。

既承認の意図を安全に継続するSDK/transportのretryには、毎回のUI確認を一律に追加しない。
API・SDK・clientごとの違いはCと確認する。GraphのRetry-Afterは最小待機条件として扱い、成功予定時刻にはしない。
再送対象を同じbatchへまとめる場合の最長delayも、その対象群と契約に従う。[S6][S8]

blockedは成功でも補償待ちでもない。fixtureでは先行項目が成功した後に明示retryを許す。初回batch内の依存処理は
別のsubmit契約であり、この手順から任意DAGのschedulerを導かない。Graphの依存制限を他のAPIへ一般化しない。[S4][S7]

## 5. 取消と、タスク全体の終わりを扱う

取消は実在する能力がある、指定された未確定項目だけへ限定する。受付は終端ではない。
元の成功が確定した場合はその成功を保つ。成功済み効果を戻す必要は[B-IU-004](undo-and-compensation.md)へ渡す。
lookup／cancelが未提供なら、その操作をUIに発明せず、確認できた照合・支援経路と未解決の状態を示す。
同期応答だけで必要な終端が確認できる契約なら、追加pollは不要である。

集約では、元Sの各項目を一度だけ数える。たとえば成功1、確定未適用1、取消1なら、
「今回の処理結果がそろった」と「3件すべての変更が成功した」は別である。unknownが残れば、その項目の結果は未解決である。
途中のfilterや欠落行を除いて成功率を100%にしない。終端失敗から再試行できる場合も、元の全変更成功とは表示しない。

内容・対象・actor・版が変わった場合は、既存005〜008の必要な修正・review・復帰条件へ渡す。
元の成功履歴と無関係な入力を残し、変更後の内容を旧承認へ黙って付け替えない。

## 実行例と検証範囲

`examples/batch-flow.mjs` / `batch-flow.html` は、宣言した非原子的サービスを使う一括アーカイブの例。
requestIdが相関とdurable lookupを兼ね、現在権限があり、lookup/cancelも存在するという限定契約である。
Graph、AWS、AIPのadapterではない。原子的API、永続復帰、SDK自動retry、実認可、任意依存graphを検証していない。

- `tests/test_batch_flow.mjs`：候補作成前に固定した13ケース。
- `tests/test_batch_boundaries.mjs`：分析時に見つけ、候補作成前に別枠で固定した3ケース。
- DOM、故障注入、追加の探索は独立検証の記録で確認する。固定suiteと混ぜて効果の点数を作らない。
- source-to-ruleはRegistry B-IU-009、研究からの適用制約はR04 `protocol-notes.md` を参照する。

## 原典

- [S1 AIP-233](https://google.aip.dev/233) — atomic/partial batch、元request index。B-T501。
- [S2 DynamoDB BatchWriteItem](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_BatchWriteItem.html) — non-atomic batch、UnprocessedItems。B-T502。
- [S3 DynamoDB TransactWriteItems](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html) — 原子的処理と取消理由。B-T503。
- [S4 Microsoft Graph JSON batching](https://learn.microsoft.com/en-us/graph/json-batching) — 相関、envelope、依存。B-S401。
- [S5 AIP-155](https://google.aip.dev/155) — request identificationと冪等性。B-T504。
- [S6 DynamoDB error handling](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Programming.Errors.html) — writeの不確定性、診断ID、SDK。B-T505。
- [S7 Microsoft Graph known issues](https://learn.microsoft.com/en-us/graph/known-issues?view=graph-rest-1.0) — JSON batchingの依存制限、externalConnectionの503例。B-S403。
- [S8 Microsoft Graph throttling](https://learn.microsoft.com/en-us/graph/throttling) — 項目別429、Retry-After、再試行。B-S402。

取消・補償の原典は既存B-S104/B-T301と参照先の条件を再利用する。上記APIの資料から、このfixture独自のlookup/cancelを導いていない。
