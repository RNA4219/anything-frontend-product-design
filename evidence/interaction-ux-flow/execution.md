# 予約変更の実行記録

2026年11月23日、Windows / Python 3.11.9。ケースごとに同じ予約データから開始した。実サービスへの接続なし。

CLIの実行は `py -3.11 -X utf8 modules/interaction-ux-flow/scripts/booking_flow.py`。試した CLI の SHA-256 は `052355463dc0975d5e2bb88ee8931023290ac7c423777667d719ac626454307a`。

入力は左から順にコマンドとして渡した。出力から状態IDとケース固有の文言を照合し、最後に表示された予約の確定日時を確認した。

| ケース | 入力順 | 観察した状態と最終日時 |
| --- | --- | --- |
| 正常 | `open R-205` → `change` → `back` → `open R-204` → `change` → `select 12-10` → `submit` → `process` → `deliver` → `reopen` | list → detail → list → detail → choose → review → pending → complete。12月10日 14:00 |
| 競合後に代替枠 | `open R-204` → `change` → `select 12-10` → `take 12-10` → `submit` → `process` → `deliver` → `change` → `select 12-11` → `submit` → `deliver op-1` → `process` → `deliver` → `reopen` | list → detail → choose → review → pending → conflict → choose → review → pending → complete。12月11日 14:00 |
| 更新済みで応答なし | `open R-204` → `change` → `select 12-10` → `submit` → `process` → `timeout` → `leave` → `reopen` → `deliver op-1` | list → detail → choose → review → pending → unknown → suspended → complete。12月10日 14:00 |
| 未検出から同じ操作を再送 | `open R-204` → `change` → `select 12-10` → `submit` → `leave` → `reopen` → `check` → `retry` → `process` → `deliver` → `process` → `deliver` → `reopen` | list → detail → choose → review → pending → suspended → unknown → pending → complete。12月10日 14:00 |
| 終端未適用から代替枠 | `open R-204` → `change` → `select 12-10` → `submit` → `process reject` → `deliver` → `change` → `select 12-11` → `submit` → `process` → `deliver` → `reopen` | list → detail → choose → review → pending → failed → choose → review → pending → complete。12月11日 14:00 |
| 全候補満枠から詳細に戻る | `open R-204` → `change` → `select 12-10` → `take 12-10` → `take 12-11` → `submit` → `process` → `deliver` → `change` → `back` | list → detail → choose → review → pending → conflict → choose → detail。12月8日 14:00 |

## 自動テスト

`py -3.11 -X utf8 -m unittest discover -s tests -v` で13件成功。通常確定、下書き保存、二重送信、同一操作の重複処理で予約版が1回だけ進むこと、古い応答、別の操作による予約変更、結果未検出からの再送、終端未適用、再表示、全枠競合、利用済みの状態を確認した。

共有初期化コミットに操作可能な現行版はなかった。初回試作と修正版は [独立操作](independent.md) で同じ入力を用いて比較した。試作のデータは同じプロセス内に保持される。実ネットワーク、ブラウザーの再起動と支援技術、利用者による評価は今回の検証範囲外。
