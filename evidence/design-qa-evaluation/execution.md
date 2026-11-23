# 予約変更の実行記録

2026年11月23日。対象は架空の工作室予約 `booking-change`。R-204 は12月8日 14:00の確定済みで、変更対象は12月10日 14:00。競合時は12月11日 14:00を使った。A と B は同じ HTML にある比較案。対象ファイルの SHA-256 は `5015c191680f3ee7b6ad7726a5d60c2cd2e642d5b252534f4fd2cbcd0a323de1`。

[受入計画](../../tests/fixtures/design-qa-evaluation/plan.json) · [操作手順](../../modules/design-qa-evaluation/references/booking-example.md) · [Aの観測値](observations-a.json) · [Bの観測値](observations-b.json)

<a id="automated"></a>
## 自動観察

Microsoft Edge 158.0.4370.33、1280×800 CSS px、Playwright 1.65.2。両案は新しいブラウザーで開始した。正常、競合、応答消失でセッション内の試験データを分け、再表示は同じ試行内で行った。

| ケース | AとBの観察 |
| --- | --- |
| `confirm` | 変更前は12月8日。確認画面は12月8日から12月10日。確定と再表示のあとも12月10日、確定回数1。 |
| `conflict-state` | 競合直後はどちらも元の12月8日、確定回数0。 |
| `conflict-recover` | どちらも別枠の12月11日に復帰。確定と再表示のあとも12月11日、確定回数1。 |
| `lost-reply-retry` | Aは画面の確定ボタンを再度押すと12月10日、確定回数2。Bは照会後に同じ枠を再度指定すると12月10日、確定回数1。再表示後も各案同じ。 |

<a id="manual-find"></a>
## 手動での対象選択

Chromium 157、1440×888 CSS px。ブラウザーを操作して Tab、Enter、矢印キーを用いた。各シナリオを別の試行として開いた。両案で Tab が「R-204 の日時を変更」に到達し、一覧の12月8日の確定済み R-204 と11月10日の利用済み R-205 を見分けられた。12月10日の確定後に一覧と完了通知の新日時、確定回数1を読んだ。

<a id="manual-conflict"></a>
## 手動での競合と復帰

A は12月8日を一覧に表示し、通知は「変更できませんでした。」、フォーカスは変更入口だった。枠が埋まったことと別枠を選ぶことは通知から読み取れなかった。変更入口を開き直し、矢印キーで12月11日を選ぶと完了できた。

B は12月10日が埋まったこと、元の予約が12月8日のままであること、別の枠を選ぶことを通知した。フォーカスは「工作室の空き枠」に移り、12月11日を選択した状態だった。両案とも12月11日に確定でき、表示上の確定回数は1だった。

<a id="manual-lost-reply"></a>
## 手動での応答消失と復帰

A は「応答がありません。もう一度確定してください。」を表示し、フォーカスは確定ボタン、照会ボタンは表示されなかった。Enterで再確定したところ、12月10日、確定回数2になり、再表示後も2だった。

B は「応答がありません。現在の予約を確認してください。」を表示し、フォーカスは照会ボタンになった。旧日時の横に「応答を確認中」と表示され、変更ボタンは無効で、Shift+Tab と Tab で移動しても再編集に入れなかった。照会で新日時の12月10日と確定回数1が表示された。同じ日時を改めて選び確定すると「同じ日時のため変更はありません。」が表示され、再表示後も12月10日、確定回数1だった。

## 判定と再現

リポジトリのルートで以下を実行した。

```powershell
py -3.11 -m unittest discover -s tests -v
uv run --with playwright==1.65.2 --python 3.11 python tests/fixtures/design-qa-evaluation/observe_booking.py a observations-a-auto.json
uv run --with playwright==1.65.2 --python 3.11 python tests/fixtures/design-qa-evaluation/observe_booking.py b observations-b-auto.json
py -3.11 modules/design-qa-evaluation/scripts/check_evidence.py tests/fixtures/design-qa-evaluation/plan.json evidence/design-qa-evaluation/observations-a.json
py -3.11 modules/design-qa-evaluation/scripts/check_evidence.py tests/fixtures/design-qa-evaluation/plan.json evidence/design-qa-evaluation/observations-b.json
```

- 標準ライブラリの単体・CLI回帰テストは12件合格。自動観察は両案で4ケースを実行し、判定時に手動3ケースの観察を加えた。
- Aは `no_go`、終了コード1。競合案内、応答消失後の案内、重複確定の3件が失敗。Bは7件合格で `go`、終了コード0。両案の `all_paths_observed` は全3経路に観察があることを表す。
- Bの記録を `find` と `confirm` のみにした入力は、5件が `not_run`、`normal_only`、`pending`、終了コード1。別の入力で `conflict-state` の回数と `lost-reply-guidance` の証拠参照を外すと、2件が `insufficient_evidence`、`pending`、終了コード1だった。

試作の採用案はB。試作で模擬したのは、確定後に返答が消失した場合と単一セッション内の履歴。本番のリリース判断には、確定前の応答消失、実際の競合と更新履歴、再送や並行操作での副作用、別セッションでの永続化が残る。実利用者の達成率、実端末・他ブラウザーの互換性、支援技術の通知、WCAG適合は未評価。 [独立評価](independent.md)
