# 予約変更の入口を比較した結果

2026年11月23日、Python 3.11.9 / Windows で[共通課題](../../tests/fixtures/booking-change.md)を試した。対象は同じディレクトリの履歴にある[予約変更試作](../../modules/product-information-architecture/examples/booking_choice.py)。試作に架空の予約を読み込み、操作のたびに表示と変更履歴を記録した。再表示は同じプロセスで一覧を初期状態に戻して行った。

通常の課題は12月8日14:00の工作室を12月10日14:00に変更して再確認すること。両案で同一データ、行の項目と文言、候補枠、後続操作、成功条件を使った。状態別と部屋別で分類軸と分類名が異なる。正しい対象を開いたことを `booking-change-find`、指定枠への変更が一度だけ行われ、他の予約が維持され、再表示後に新日時を確認できたことを `booking-change-confirm` で判定した。

| 操作した条件 | 状態別 | 部屋別 | 観察した結果 |
| --- | --- | --- | --- |
| 通常 | 確定・変更可に1件 | 工作室に2件 | 両案で R-204 を変更し、再表示後に新日時を確認。R-205 は不変。 |
| 同室・同日・同状態を追加 | 確定・変更可に2件 | 工作室に3件 | 先頭の R-206 は10:00、対象の R-204 は14:00。両案で日時を照合して R-204 だけを変更。 |
| 利用済みの予約を開いて戻る | 利用済みの R-205 を開き変更を試した | — | 枠選択は拒否され、戻って R-204 の変更と再確認を完了。 |
| 確定前に一覧を再表示 | — | R-204 で12月10日を選択直後に再表示 | R-204 は元の日時を保持。確定の受入条件は未達。 |
| 別の変更可能な予約を誤って確定 | — | R-206 を確定し再表示後に R-204 を確認 | R-206 だけが変更された。後で対象を開いても確定の受入条件は未達。 |
| 変更元の時刻と予約番号が不明 | 同室・同日・同状態の二件を閲覧して終了 | 同じ条件で推測して確定 | 状態別で変更せず保留した場合は両予約を保持。部屋別で推測により変更した場合は、正答と同じ予約を変更しても課題未達。 |

変更可と分かっている利用者に状態別の入口を用意すると、通常例では照合対象を絞れる。同じ部屋の変更可能な予約が複数あるときは、時刻など既知の識別情報が必要になる。変更可否も調べたい場合は部屋別で履歴ごと照合できる。同室・同日しか分からず二件とも当てはまる場合は、予約通知などの照合手段が得られるまで判断を保留する。

## 再現

リポジトリのルートで実行する。終了コードは `0` が課題達成、`1` が課題未達、`2` が引数エラー。保留は期待どおりの結果であっても予約変更を完了していないため `1` となる。最終の `RESULT` 行で経路、開いた対象、変更履歴、残った予約を確認できる。

```powershell
$example = 'modules/product-information-architecture/examples/booking_choice.py'
py -3.11 -X utf8 $example --variant status --steps 'group changeable' 'open R-204' 'slot 12-10' confirm reopen 'group changeable' 'open R-204'
py -3.11 -X utf8 $example --variant room --steps 'group workshop' 'open R-204' 'slot 12-10' confirm reopen 'group workshop' 'open R-204'
py -3.11 -X utf8 $example --variant status --scenario unknown-time --steps 'group changeable' 'open R-206' back 'open R-204' quit
py -3.11 -B -m unittest discover -s tests -p test_product_information_architecture.py -v
```

担当の標準ライブラリテスト10件とSkillの書式検証が通った。[操作ログ](execution-traces.json)に各コマンドの引数、表示、最終判定を収録した。Windowsで `python` がアプリ実行エイリアスの場合は上記のPython Launcherを使う。

発見率、分類の選好、実サービスの権限・予約通知・プロセスをまたぐ保存、競合や応答喪失は今回の試作から判断できない。実利用者に対するカードソート、ツリーテスト、実画面での完了観察は未実施。[独立評価](independent-evaluation.md)
