# 予約変更を操作して確かめる

共通課題 `booking-change` の利用者は、確定済みの工作室 R-204 を12月8日14時から12月10日14時へ移し、開き直して日時を確かめます。12月10日の枠が取れなくなった場合は、12月11日の代替枠を選べます。R-205は利用済みです。[共通課題](../../../tests/fixtures/booking-change.md)

## 状態とイベント

同じプロセス内で画面とサービスを模擬します。利用者側は予約ID、最後に確認した日時と版、下書き、送信した操作の内容を保持します。サービス側は確定済み予約、占有された枠、操作IDごとの終端結果を持ちます。新枠と元予約の版を実行時に検査し、成立した場合だけ版と日時を更新します。

| 現在の状態 | イベント・遷移条件 | 次の状態と保持・更新するデータ | 受入条件ID |
| --- | --- | --- | --- |
| `list` | 予約を開く | `detail`。予約IDとサービス側の日時・利用状態を読む | `booking-change-find` |
| `detail` | 変更可の場合に変更する | `choose`。確定日時と版を保持し、空き枠を読む。利用済みの予約では詳細に変更不可を示す | `booking-change-find` |
| `choose` | 空いている候補を選択する | `review`。確認済みの元予約と変更候補を比較できる | `booking-change-confirm` |
| `choose` | 空いている候補がない。利用者が戻る | 元の確定日時と空き枠がないことを示す。戻ると `detail` | `booking-change-conflict` |
| `review` | 戻る、または確定操作を実行する | 戻る場合は `choose`。送信時は `pending`。対象、版、候補、操作IDを固定する | `booking-change-confirm` |
| `pending` | 対応する応答で確定。枠や版が競合。終端未適用。応答期限超過 | 順に `complete`、`conflict`、`failed`、`unknown`。確定応答は新しい予約を表示する。終端未適用では確定値の変更を加えない。期限超過では最後に確認した日時を保持する | `booking-change-confirm` ・ `booking-change-conflict` ・ `booking-change-retry` |
| `conflict`、`failed` | 再度変更する | `choose`。現在の日時・版と空き枠を使い、確認後に新しい操作IDで送信する | `booking-change-conflict` |
| `unknown` | 照会または対応する遅延応答 | 終端結果が分かれば該当状態へ。照会で操作が見つからなければ `unknown` を維持する。同じ操作の再送時は `pending` に戻り、入力と操作IDを維持する | `booking-change-retry` |
| `pending`、`unknown` | 別の確定操作、入力への戻り、他の操作IDの応答 | 状態と操作IDを維持する。反復した確定操作で新しい変更を作らない | `booking-change-retry` |
| 操作中 | 離脱、再表示 | 離脱時は `suspended`。再表示で保存済みの下書きと確定予約を読み、未解決の操作IDがあれば終端結果を照会する。見つかった終端結果へ進み、未検出なら `unknown` を維持する | `booking-change-retry` |
| `complete` | 再表示、予約一覧へ戻る | 現在の確定日時と、その依頼で確定した日時を確認できる。その後に別の変更がある場合は両方を示す。完了済みの応答で画面を戻さない | `booking-change-confirm` |

BからCへは状態ごとの表示、操作可否、状態通知、復帰先を渡します。たとえば `unknown` には最後に確認した日時と結果確認の操作を出し、候補を変える操作は終端確定まで出しません。Dへは下の入力列と受入条件IDを渡します。

## 実行方法

リポジトリのルートで `py -3.11 modules/interaction-ux-flow/scripts/booking_flow.py` を実行します。Windows以外では `python3` を使えます。最初に `help` を入力すると、利用者操作と故障注入のコマンドを確認できます。ケースごとに新しく起動し、下の行を左から一つずつ入力します。各ケースの `process` はサービスによる実行、`deliver` は画面への応答を表します。

| ケース | 再現操作 | 観察する結果 |
| --- | --- | --- |
| 変更対象を見つけて確定 | `open R-205` → `change` → `back` → `open R-204` → `change` → `select 12-10` → `submit` → `process` → `deliver` → `reopen` | 変更可能な予約を識別でき、確認画面に8日と10日が出る。確定後と再表示後に10日が出る |
| 競合から代替枠へ | `open R-204` → `change` → `select 12-10` → `take 12-10` → `submit` → `process` → `deliver` → `change` → `select 12-11` → `submit` → `deliver op-1` → `process` → `deliver` → `reopen` | 競合では8日を維持し、11日を選べる。古い競合応答は後の操作を変えず、11日に確定する |
| 更新済みだが応答なし | `open R-204` → `change` → `select 12-10` → `submit` → `process` → `timeout` → `leave` → `reopen` → `deliver op-1` | タイムアウトでは結果不明。再表示で10日の確定を照会し、遅延応答が来ても結果は同じ |
| 書き込まれる前に画面を閉じる | `open R-204` → `change` → `select 12-10` → `submit` → `leave` → `reopen` → `check` → `retry` → `process` → `deliver` → `process` → `deliver` → `reopen` | 結果未検出時は8日を表示する。同一IDを再送し、重複した処理でも予約版は1回分だけ増える |
| 終端未適用から再選択 | `open R-204` → `change` → `select 12-10` → `submit` → `process reject` → `deliver` → `change` → `select 12-11` → `submit` → `process` → `deliver` → `reopen` | 未適用では8日を確認できる。新しく確認した変更だけが11日に確定する |
| 全候補が満枠 | `open R-204` → `change` → `select 12-10` → `take 12-10` → `take 12-11` → `submit` → `process` → `deliver` → `change` → `back` | 満枠の理由が分かり、8日14:00の予約詳細へ戻れる |

模擬サービスは同一プロセス中にデータを保持します。プロセスを終了して再起動すると新しいシナリオになります。実サービスへの適用では、対象APIの原子的な変更、操作結果の保持期間、照会の整合性を確認します。
