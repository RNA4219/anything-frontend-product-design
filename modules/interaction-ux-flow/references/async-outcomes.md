# 非同期処理・再試行・取消

ここにあるUI手順は、以下の一次資料から組み立てた設計上の推論である。
HTTPや製品APIの事実を、別製品の既存保証へ読み替えない。

## B-IU-001 — 何が確定したかを分ける

副作用のある送信では、次の情報を別に持つ。

| 情報 | 例 | 単独では証明できないこと |
| --- | --- | --- |
| 通信の観測 | 応答受信、タイムアウト | 業務処理の成功／不成立 |
| 要求の受付 | 202、操作トークン | 処理完了 |
| 操作の終端 | done、成功／エラーの結果 | 終端フラグだけでの成功 |
| 業務結果 | 確定した予約・出力 | 返金や通知など別処理の完了 |
| 画面が知る値 | 最後に確認した日付、希望日付 | 現在も旧予約が有効であること |

1. 完了を示す正本の応答・リソースをAPI契約から選ぶ。
2. 応答が失われた場合は、対象・希望内容・操作IDを保って結果未確認を表示する。
3. 正本へ照合し、成功・失敗・取消を区別して表示する。照会失敗は元処理の失敗に変えない。
4. 照会手段がない場合は参照番号、利用できる確認先、次にできることを残す。
5. 同期応答が最終結果を保証するなら、その場で完了してよい。余分なpollを追加しない。

**例：** 変更送信の応答が消えたときは「変更結果はまだ確認できません。最後に確認した予約：
12月8日／変更希望：12月10日」と表現する。「変更に失敗しました」「元の予約は変更されていません」
は、その事実が確認できた場合に限定する。実際に照会しているときだけ「確認中」とする。

RFC 9110 §15.3.3は202を処理受付として定義する。Googleのcanonical Codeは、状態変更済みでも
deadlineを超える場合を示す。Google LROでは終端のerror/responseも読む必要がある。
[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.3.3) ·
[Code](https://github.com/googleapis/googleapis/blob/master/google/rpc/code.proto) ·
[AIP-151](https://google.aip.dev/151) ·
[Operation](https://github.com/googleapis/googleapis/blob/master/google/longrunning/operations.proto)

## B-IU-002 — 再試行を同じ意図へ結び付ける

再送の前に、APIの版、対象範囲、同一操作の識別方法、内容一致、保持期限、エラー別の条件を確認する。
キーが不明、期限外、内容が変化、保証が未確認なら、自動的に別の副作用を発生させず結果照合へ戻す。
ボタンの無効化は連打への対処であり、サーバー側の重複防止を代替しない。

| 入力条件 | 選ぶ経路 |
| --- | --- |
| 完了結果が確認できた | その結果を示す |
| 元要求が未適用と確実に分かる | 契約に従い再試行・入力修正へ |
| 同じ意図・対象・内容で、再送の安全契約が有効 | 同じ操作として回復する |
| キー喪失、期限外、内容変更、非冪等で保証なし | 正本との照合。自動的な新規操作を作らない |
| 同じ内容でも利用者が新しい処理を明示した | 別の意図として新規操作を作る |

再読込や再接続をまたぐ操作記録は、データの寿命と機密性に合う場所へ保持する。
同じキーを永久に安全と扱わない。冪等なHTTPメソッドに不要なキー方式を強制しない。
Stripe v1の保持窓・固定応答再生は製品と版に固有であり、v2や別APIへ移植しない。
同じ入力で別の成果物を作りたい意図もあるため、入力一致だけを重複判定にしない。
[HTTPの冪等性](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2) ·
[Stripeのエラー契約](https://docs.stripe.com/error-low-level) ·
[Stripeの冪等性契約](https://docs.stripe.com/api/idempotent_requests) ·
[AWSの実装者解説](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

## B-IU-003 — 取消を別の操作として設計する

取消前に、対象が画面、通信、進行中の処理、業務リソースのどれかを定める。
取消可能な状態・期限・権限・終端を示す証拠を読む。未対応の取消を実行可能として表示しない。

| 観測 | 表示と次の動作 |
| --- | --- |
| 取消要求を受け付けた | 取消要求済み。元の操作IDで結果を確認できる状態を保つ |
| 取消が確定した | 契約で取り消された対象を明示する |
| 元の処理の成功が確認された | 成功した事実と結果への経路を示す |
| 拒否・未対応・通信断 | 取消完了とせず、理由または不確実性と確認手段を示す |

成功を確認したという事実だけから、取消要求の送信と変更完了の時刻の前後を推測しない。
「変更完了を確認。取消完了は未確認」のように観測を述べる。時系列や原因を説明するには、
それを示す別の証拠が必要になる。バナーだけでなく、旧値のバッジや見出しも結果未確認と矛盾させない。

同期的に取消結果を保証するAPIなら、その応答で確定できる。
Google LROのCancelOperationはbest effortで、DeleteOperationは取消ではない。
これは全DELETEの意味を規定するルールではない。BigQueryの取消APIは状態確認を要求する一方、
応答のjobフィールドにfinal-stateという記述もある。HTTP成功だけで取消確定せず、返された状態を解釈する。
[Google LRO](https://github.com/googleapis/googleapis/blob/master/google/longrunning/operations.proto) ·
[BigQuery jobs.cancel](https://docs.cloud.google.com/bigquery/docs/reference/rest/v2/jobs/cancel) ·
[BigQueryジョブ管理](https://docs.cloud.google.com/bigquery/docs/managing-jobs)

取消確定は全影響の復元を意味しない。完了後の返金等は別の業務であり、pendingやfailedになる場合もある。
通常のローカル編集Undoと分ける。専用契約・専用試験がない補償案はHOLDに残す。
[補償の反例：Stripe](https://docs.stripe.com/refunds)

完了通知には、完了した対象、確認できる結果、次に起こること、必要なら参照番号を含める。
申請送信と審査・登録完了など、別の段階を一つの「完了」に含めない。
これは各業務への適用が必要なガイドであり、日本語文言の効果を実証するものではない。
[GOV.UKの確認ページ](https://design-system.service.gov.uk/patterns/confirmation-pages/)
