# 予約変更の部品契約

利用課題IDは `booking-change`。[共通の試作課題](../../../tests/fixtures/booking-change.md) の R-204 を、利用者が空き枠へ変更して確定を確認する。R-205 は利用済みとして見分けられる。選択は未確定の間、現在の予約を書き換えない。

## 部品と採用理由

| 部品ID | 選択 | 契約と適用条件 |
| --- | --- | --- |
| `reservation-list` / `open-change` | 見出し付きの予約一覧とネイティブボタン | 部屋、予約番号、日時と状態を表示。変更できる予約だけに対象の分かる操作を付ける。候補画面から一覧へ戻ると操作にフォーカスを戻す。 |
| `slot-form` / `slot-10` / `slot-11` | ラベル付き radio を `fieldset` と `legend` で合成 | 一度に一つの短い候補を選ぶ。ラベル全体がタップ領域。Tab で入り、Space・矢印で選ぶ。未選択ではネイティブ検証で止める。競合した枠は理由付きで無効表示。長い一覧で探索が必要なら別の選択モデルを比較する。 |
| `confirm-section` / `submit-change` | 同じページ内の比較とボタン | 現在と変更先をラベル付きで示す。選び直しでは有効な選択とフォーカスを復帰する。利用者が比較と確定を同じ領域で行えるため専用のダイアログは設けない。 |
| `booking-status` | 常設の `role="status"` | 送信中・照合中の更新を同じ領域のまま通知する。領域が切り替わる結果では、表示した見出しにフォーカスを置き、説明テキストで事実と復旧方法を伝える。 |
| `unknown-section` / `unchanged-section` / `success-section` | 既存の見出し、テキスト、ボタンの合成 | 照合を経て、確定日時または未適用を示す。日時と次の操作の意味が色や形に依存しない。 |

この作例は共有UIライブラリを持たない。入力契約はネイティブ部品に適合し、予約固有の復旧はページの状態と部品の合成で表現できる。予約向けの新しい共通部品を採用する根拠は、他の画面やサービスでも同じ契約が必要だと確認できたときに追加する。 [GOV-1・GOV-2・HTML-1・HTML-2](../../../research/ui-engineering-design-system/sources.md)

## 状態と受入条件

| 状態ID | 入口と操作 | 更新、通知、フォーカス | 受入条件 |
| --- | --- | --- | --- |
| `list` | 開く、完了後に戻る、再表示 | 確定日時と利用済み予約を表示。操作から戻った時は変更ボタンに復帰。 | `booking-change-find` |
| `choose` | 予約選択、確認画面から選び直す | 初回は見出し、選び直し時は有効な選択へ。候補操作で確定日時を変えない。 | `booking-change-find`、`booking-change-confirm` |
| `confirm` | 候補の選択後に確認、未適用が判明してから再確認 | 変更前と変更先を表示し見出しにフォーカス。明示操作で送信。 | `booking-change-confirm` |
| `pending` | 確定 | フォーカスを保持し送信中を通知。確定・選び直し・試作初期化を無効と伝え、押しても実処理をしない。 | `booking-change-confirm`、`booking-change-retry` |
| `conflict` | 送信で枠の競合を検知 | 元の確定日時、埋まった理由、使用可能な候補。見出しへ移し、候補を選び直せる。 | `booking-change-conflict` |
| `unknown` → `checking` | 応答が途切れたら現在予約を照合 | 希望日時と照合操作を表示。照合中はフォーカスを保ち、進捗を通知。再読込で未照合の操作を復帰。 | `booking-change-retry` |
| `unchanged` | 照合で未適用が判明 | 元の確定日時と希望日時を表示し見出しに移す。同じ内容の再送は再確認後に同じ操作IDで行う。別候補には新しいID。 | `booking-change-retry` |
| `success` | 処理の応答か照合で確定を確認 | 新日時を見出しに続く説明で示す。同一オリジン・同一シナリオで再読込しても新日時を一覧から確認できる。 | `booking-change-confirm`、`booking-change-retry` |
| `storage-error` | 模擬ストアの読込・保存・照合に失敗 | 新しい確定は表示せず、読み直しへ案内。未照合の操作が残っている場合はそこから再開。 | 保存失敗時の回帰 |

サンプル内の模擬記録は、現在日時・使用不可になった枠・処理中の操作IDと更新回数をシナリオ別に保持する。実サービスでは、受け付けた操作の状態を確認するAPI、予約と枠の原子的な更新、競合と再送時の整合、照合を継続できる期間をサービス側と契約する。同じ日時でも別の操作で変更された可能性があれば、操作IDや版と照合する。 [STR-1・STR-2・AWS-1](../../../research/ui-engineering-design-system/sources.md)

## 視覚方針の適用点

| 用途 | 作例のトークン | 差し替え後に再確認する箇所 |
| --- | --- | --- |
| 面と文字 | `--booking-surface` / `--booking-text` | 一覧、エラー、結果。画面の面とその上の文字を対で確認。 |
| 操作と文字 | `--booking-control` / `--booking-on-control`、`--booking-action` / `--booking-on-action` | 通常ボタン、主要操作、送信中と空候補。文字と境界から無効状態を判別できること。 |
| フォーカスと境界 | `--booking-focus`、`--booking-line` | ボタン、radioのラベル、切り替えた領域の見出し。隣接面との区別と見切れ。 |
| 書体・密度 | `--booking-font`、`--booking-padding`、`--booking-gap`、`--booking-measure`、`--booking-target-size` | 長いラベル、狭幅での現在・変更先・操作の順序、タップ領域と間隔。 |

初期値にはブラウザーのシステム色とシステムフォントを使う。Art Direction に渡す優先情報は、工作室・予約ID・確定日時、比較ペア、現在の状態と次に可能な操作。CSS変数を差し替えた場合は、各行の利用箇所を同じ利用課題で再確認する。 [USW-1・DTCG-1・AD-1](../../../research/ui-engineering-design-system/sources.md)

## 起動と再現

リポジトリルートから次を実行する。

```sh
python -m http.server 8765 --bind 127.0.0.1 --directory modules/ui-engineering-design-system/examples/booking-change
```

ブラウザーで `http://127.0.0.1:8765/` を開く。シナリオ名は画面下に表示される。同じシナリオを最初から試す場合は「このモードの試作データを初期化する」を押す。

| URL の末尾 | R-204 に対して試すこと |
| --- | --- |
| `/` | 12月10日 14:00 を選び、変更前後を確認して確定する。再読込して確定日時を見る。 |
| `/?scenario=conflict` | 12月10日を確定しようとし、元の予約を確認する。12月11日に選び直し、確定する。 |
| `/?scenario=unknown-applied` | 12月10日を確定しようとする。結果不明を表示したら再読込し、現在の予約を照合して完了を確認する。 |
| `/?scenario=unknown-unapplied` | 同様に現在の予約を照合する。未適用を確認し、比較と確定をやり直す。 |

自動試験は Playwright が必要。Chromium を取得して実行する例を示す。Edge が導入済みなら、PowerShell で `$env:BOOKING_BROWSER_CHANNEL='msedge'` を指定してブラウザー取得を省ける。

```sh
uv run --with playwright==1.65.2 playwright install chromium
uv run --with playwright==1.65.2 python -m unittest discover -s tests -p test_ui_engineering_design_system.py -v
```

[今回の実行・独立評価](../../../evidence/ui-engineering-design-system/README.md)
