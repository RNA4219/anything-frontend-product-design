# UI実装・デザインシステムの実行証跡

2026-11-23（JST）。対象は [担当Skill](../../modules/ui-engineering-design-system/SKILL.md) の予約変更。入力は [共通課題](../../tests/fixtures/booking-change.md)。作例ファイルの版は LF のバイト列で求めた SHA-256 の先頭 `d7cdae5d4ad0`（HTML）、`3eaf923d7511`（JS）、`795c73cf01be`（CSS）。

## ブラウザーテスト

Windows、Edge 158.0.4370.33、Playwright 1.65.2。既定 1024×768、タッチの競合ケースは320×700 CSS px。ローカル HTTP の別コンテキストで各シナリオを実行した。6件成功、38.368秒、ページ例外なし。

```powershell
$env:BOOKING_BROWSER_CHANNEL='msedge'
uv run --with playwright==1.65.2 python -m unittest discover -s tests -p test_ui_engineering_design_system.py -v
node --check modules/ui-engineering-design-system/examples/booking-change/booking.js
```

| テスト | 確認した結果 |
| --- | --- |
| R-204をキーボードで変更 | R-205と見分ける。Tab・Space・矢印・Enterで候補を選び、変更前後を比較。新日時12月10日を確定・再表示した。 |
| 候補を選び直す | 12月10日の選択とフォーカスが復帰。12月11日に選び直して確定した。 |
| 競合からタッチで復帰 | 320 CSS pxで横あふれなし。12月10日の競合後に元の確定日時を表示し、利用可能な12月11日へ変更した。 |
| 結果不明・適用済み | 確定を連打しても保留中はフォーカスが残り、進捗を通知。結果不明の再読込後に照合し、適用1回と確定日時を確認した。 |
| 結果不明・未適用 | 照合すると元の日時が表示され、比較画面を経て明示的に再確定。適用1回を確認した。 |
| 保存失敗 | 模擬ストアの書込みを失敗させると保存エラーになる。再読込で元の日時を表示した。 |

初回は6件中2件が、表示中の画面と同じ日時を持つ非表示要素を拾い失敗した。表示中の状態に対応する要素を特定するようテストを修正し、6件成功に戻った。初回53.540秒と修正後44.016秒の主な差に、失敗した2件の各5秒の表示待ちがある。挙動と待機条件を照合し、作例の処理速度を問題とする変更は加えていない。

Skill Creator の `quick_validate.py modules/ui-engineering-design-system` と `node --check` は成功。Python標準環境での `unittest discover` は Playwright を使う6件をスキップするため、上記のブラウザー付き実行を判定に使った。

## コントラストの修正と再確認

Edge、320×700 CSS px で axe-core 4.14.1 の `wcag2a`、`wcag2aa`、`wcag21a`、`wcag21aa`、`wcag22aa` タグを実行。初回のライト設定では、候補・確認・競合・結果不明・未適用の5状態で主要ボタンの `color-contrast` が指摘された。

主要ボタンの背景・文字トークンの既定値を `Highlight`/`HighlightText` から `CanvasText`/`Canvas` に変更。同じ作例と320 CSS pxで、一覧・候補・確認・完了・競合・結果不明・未適用をライトとダークで検査した。14画面状態で検出違反0・追加判定対象0。候補の主要ボタンで測定した比はライト21.00:1、ダーク18.73:1。

再現では、[作例の操作](../../modules/ui-engineering-design-system/references/booking-change.md#起動と再現) で各状態を表示し、Playwright から `axe.min.js` を読み込み `axe.run({runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']}})` を実行する。アプリの実行時依存は不要。

## 独立評価

- [独立評価](independent.md) は実装担当以外が8経路を完了。照合前の再読込、連打、古い別タブでの送信も確認した。本番の排他処理、支援技術による実際の読み上げ、実機タッチ、Edge以外での同一試験一式は未確認。
