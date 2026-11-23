# 予約変更の評価

[共通課題](../../../tests/fixtures/booking-change.md)と[受入計画](../../../tests/fixtures/design-qa-evaluation/plan.json)を使う。試作の A・B は同じデータ、画面、日時の選択と成功条件を持つ。障害後の表示と再確定の処理が異なる。試作はブラウザーのセッション内で予約を保持する。

## 手動で操作する

リポジトリのルートで次を実行する。

```text
python -m http.server 43917 --bind 127.0.0.1 --directory tests/fixtures/design-qa-evaluation
```

ブラウザーで `http://127.0.0.1:43917/booking.html?variant=b&scenario=normal&run=01` を開く。ポートを変更した場合は URL にも反映する。`variant` は `a` または `b`、`scenario` は `normal`、`conflict`、`lost-reply`。各試行で `run` を変えるか新しいブラウザーコンテキストを使う。再表示の確認中は URL を保つ。

1. 正常。工作室の2件から R-204 をたどる。12月10日を選び、確定前の日時の差、確定後の予約、再表示後の予約と確定回数を確認する。
2. 競合。同じ入力で競合を起こし、何が起きたか、元の予約が保たれているか、画面から何ができるかを観察する。12月11日を選び、確定と再表示まで確認する。
3. 応答消失。12月10日の送信直後、画面が示す次の行動と現在の予約を調べる。古い表示を確定結果と誤認する表示があるか、照会を飛ばして変更に入れるかを確かめる。状態確認のあと、同じ変更をもう一度たどって確定回数を読む。別試行では、応答消失直後に再表示して現在状態を照合する。実サービスでは更新履歴や取引IDなど要求に合う観測先を使い、未確定のまま応答を失った場合も試す。

両案を比べるときは端末、表示幅、入力方法、開始状態をそろえる。競合後は選べる空き枠、応答消失後は予約照会にキー操作で進めるか、フォーカス先と画面表示を記録する。

## 自動観察と判定

Python 3.11、Playwright 1.65.2、Microsoft Edge がある場合、次で自動観察を再現できる。出力ファイルには対象 HTML の SHA-256、ブラウザー版と幅、自動ケースの観測値が入る。手動の結果を加えるときは、同じ案・同じ HTML のハッシュを記録した手動証跡を用いる。

```text
uv run --with playwright==1.65.2 --python 3.11 python tests/fixtures/design-qa-evaluation/observe_booking.py b observations.json
python modules/design-qa-evaluation/scripts/check_evidence.py tests/fixtures/design-qa-evaluation/plan.json observations.json
```

計画には `task_id` と `cases` を置く。各ケースには `id`、`requirement_id`、`path`（`normal`、`failure`、`recovery`）、`priority`（`required`、`advisory`）、`method`（`automated`、`manual`）、`expected`（項目IDと期待値）を置く。観察ログには同じ `task_id`、版を示す `build`、`observations` を置く。各観察はケースごとに1行とし、`case_id`、`method`、`actual`（実際に得た項目IDと値）、`evidence`（再現可能な証跡への参照）を記録する。期待・観測の値は JSON スカラーを使う。

判定ツールは各ケースを `pass`、`fail`、`insufficient_evidence`、`not_run` で返す。`normal_only` は観測範囲が正常経路に限られる場合。必須の3経路すべてがそろった計画を対象に、`go` は終了コード0、`no_go` または `pending` は1、入力の契約違反は2。CLI が照合できるのは指定された観測値・手法・証拠参照の記載。参照先が対象版の観察を裏付けるかは判定前に確認する。

[実行記録](../../../evidence/design-qa-evaluation/execution.md)で、版、操作環境、結果と確認範囲をたどれる。
