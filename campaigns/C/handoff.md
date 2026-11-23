# SESSION C — 実装・検証・再開の引き継ぎ

## 現在の結論

3ラウンドを完了し、9 Instruction Unitを登録した。**ACCEPT 3 / HOLD 6 / REVISE 0 / REJECT 0 / DRAFT 0**。ACCEPTはC-UI-005〜007の限定トークン処理に限る。C-UI-001〜004、008〜009は実ブラウザ/AT等の必要証拠が不足しておりHOLDである。モデル検査器が通ったことと、画面が使えることを区別する。

このチェックポイントは12ラウンド到達でも飽和判定でもない。次のround 04は登録のみで未実行。完了済みの研究・分析・初回失敗・再検証を上書きせず、続きから開始する。

## Gitと共通入口

- ブランチ: `session-c/ui-engineering-20261123`
- Draft PR: https://github.com/RNA4219/anything-frontend-product-design/pull/1
- 起動時main: `3d02174a69676afa8e0b02f4062cc6ecb636d300`
- 現行公開base: `4333d097b5699528b5554434b494d8079126ba0f`
- 実行中の公開履歴更新後は、現行Cブランチに検証済みC差分だけを移し、削除済み履歴・記録を復元していない。詳細は `publication.json`。
- 変更範囲は `modules/ui-engineering-design-system/`、`registry/C/`、`research/ui-engineering-design-system/`、`campaigns/C/`。
- 既存のルート入口は既にCモジュールを指しているため、共通README・ルートSKILLの変更は不要。統合時に全体の成熟度表を更新する場合は統合担当が上の限定ACCEPT/HOLDを反映する。mainへ自動マージしない。
- 既存の予約変更一連の試作と過去の証跡を保持している。過去のブラウザ結果を今回の追加試作へ流用していない。

## 完了した循環

| Round | 研究・実装対象 | 実行結果と採否 |
| --- | --- | --- |
| 01 | 標準部品、利用不可/読取専用、dialog cleanupとfocus | Python16件/Node6件。独立評価で送信policy、例外分類、再表示値、focus fallbackを修正。4 Unit HOLD |
| 02 | 型付き別名グラフ、テーマ合成、必須ロール、CSS変数名/出力 | トークン19件、独立再検証125/125。深いJSON、大整数、CLI入力例外を修正。3 Unitを限定ACCEPT |
| 03 | 必要情報・操作保持、二次元例外、実効矩形とspacing | 追加32件を含むPython67件、同じ独立127ケースを初回118/127→修正後127/127。2 Unit HOLD、モデルprecheckのみ採用 |

各ラウンドは実際のResearcher-1/2を並列起動し、別のAnalystとCriticを使用した。計12タスクを回収済み。同時稼働は親を含め最大3。Criticは同一モデルの別タスクであり、外部評価・盲検・異なるモデルの結果とはしない。

初回失敗、修正対象のハッシュ、同じ期待値の再実行は各 `rounds/NN/` に残している。round03の独立127ケースはCritic作成124件と親発見の巨大指数の再現3件である。追加18件の保存結果assertionは別カウントであり、独立した新UIケースに加算しない。

## 再現できる純検査

リポジトリルートで実行する。Python標準ライブラリとNodeを使う。実行環境の版は `rounds/03/runtime-environment.json`。

```sh
python3 campaigns/C/check_registry.py
python3 -m unittest discover -s modules/ui-engineering-design-system/tests -p 'test_*.py' -v
node --test modules/ui-engineering-design-system/tests/test_runtime.mjs
python3 modules/ui-engineering-design-system/checks/contracts.py modules/ui-engineering-design-system/examples/component-contracts.json
python3 modules/ui-engineering-design-system/checks/layout.py modules/ui-engineering-design-system/examples/booking-reflow-model.json
python3 modules/ui-engineering-design-system/checks/layout.py modules/ui-engineering-design-system/examples/toolbar-target-model.json
```

トークンCLIは `references/token-contracts.md`、独立反証の再実行は各recheck.mdに従う。初回結果ファイルへ書き戻さない。手作りの不十分な対照実装との比較を、生成品質の改善率・実利用者の成功率として報告しない。

## 未実行の検証と採用ゲート

実ブラウザ、AT、CIは今回の追加候補について成功証拠がない。ブラウザ実行は環境/承認制約で停止し、別経路で回避していない。同じセッションで代替サーフェスを起動して再試行しない。許可された検証環境が用意された後に、対象ブラウザ/OS/AT/入力と版を固定し、`checks/browser-checks.md` と `checks/layout-observation-protocol.md` の実観測を実施する。

特に、dialogのEnter/Space/Escapeと起点削除、実送信値、320/256境界、長ラベル、表の例外と隣接本文、clip/overlay下の実hit領域、focus、AT順、機器切替を確認する。JSONのsynthetic値はHTMLから抽出されておらず、CSSの寸法宣言も実測値ではない。持込証拠の内容・真偽・一覧完全性を検査器は認証しない。

## 原典・登録・役割の境界

`registry/C/skills/`からsource_refs→研究JSON→canonical sourceへ追跡できる。46資料記録を44文書へ重複排除した。imozuruの実fetch失敗と部分取得を保持し、追加で公式repoの固定ファイル3点を取得・Git blob照合した。詳細は `source-provenance.md`。完全なlive Webページとのbyte同一性は主張しない。第三者原文と非公開制御記録は公開repoに収めない。

Art Directionの配色・書体・余白・構図、既存の基本アクセシビリティ原則を新設しない。Cは状態→DOM/属性/event、トークン変換、layout/targetの適用条件と観測契約を担当する。Aは必要機能とIA、Bは業務遷移・取消・再試行・競合、Dは評価・実画面の採否と生成効果測定を担当する。

## 次に行うこと

1. `manifest.json`、この文書、各roundのdecision/recheck、追記型 `registry/C/backlog.jsonl` の各issue最新行を読む。ブランチとmainの現在SHAを確認し、新しい専用worktreeを作る。
2. 最優先の未取得証拠はC-005/C-008/C-011の実画面・ATである。環境が未解決ならHOLDを維持する。
3. 次の研究ラウンドは `rounds/04/plan.json`、C-004「非同期更新時の部品identity・入力値・focus・通知」。2 Researcher→sankai Analyst→親実装→別Criticの順を守り、既存44資料を先に照合する。
4. C-009はDTCGの未対応機能、C-010は実テーマconsumer/forced-colors等、C-012はreading-flowと複合入力の実観測。IME/hydrationと複合widgetはC-006/007に残す。
5. Bへ業務再試行・結果不明の判定方針、Dへ実利用者/盲検・繰返し生成の効果検証を渡す。未定方針をC側で発明しない。

金額・token費用は計測APIがなく不明であり、0としていない。実行状態と未知費用をラウンドごとに記録している。制御基盤の登録・整合性検査と、実験の成功・昇格は別に管理する。
