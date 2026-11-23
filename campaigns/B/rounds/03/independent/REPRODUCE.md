# R03 Critic 実行の再現

このディレクトリには、初期評価の証跡と、公開コピー用に環境依存pathを除いた再実行コードがある。原本captureを公開する必要はない。

## 環境

- Node v24.22.3で実行済み。
- DOM検証はjsdom 26.1.0。実ブラウザ・レイアウト・支援技術の試験ではない。
- `B_REPO_ROOT`: repository root。省略時はcwd。
- `B_CRITIC_OUTPUT_DIR`: 試験結果の出力先。省略時はcwd基準の `artifacts/critic-r03`。
- `B_DOM_JSDOM_PATH`: 利用可能なjsdom package directory。省略時は通常の `require('jsdom')`。

```bash
node modules/interaction-ux-flow/tests/test_resume_conflict.mjs modules/interaction-ux-flow/examples/resume-and-conflict.mjs /absolute/output/frozen-suite.json
node /path/to/reproduce-dom-events.mjs
node /path/to/reproduce-edge-probes.mjs
python /path/to/reproduce-negative-controls.py
node /path/to/recheck-focused.mjs
```

各コマンドはrepository rootをcwdにするか、`B_REPO_ROOT`を指定する。DOMの2スクリプトでは必要なら `B_DOM_JSDOM_PATH` を指定する。出力先を先に用意する必要があるのは固定suiteの第3引数だけ。他のコードは `B_CRITIC_OUTPUT_DIR` を作成する。

DOM再現コードは候補HTML自身のclick/change handlerを実行する。jsdomがES module scriptを直接実行しないため、単一import文だけを実moduleのfactory参照へ置換する。モデル関数のみの検証ではないが、native browser検証でもない。

`reproduce-dom-events.mjs` は引数でmodule path、HTML path、出力JSONを指定できる。`reproduce-edge-probes.mjs` はmodule path、出力JSONを指定できる。初期候補に対して再実行する場合は `campaigns/B/rounds/03/artifacts/initial` 内のmodule/HTMLを渡す。

負例スクリプトは必ず初期snapshotを読み、固定suiteで4つの意図的故障の検出を確認する。現行候補を変異・編集しない。回帰と探索の結果は固定13ケースへ合算しない。

## 記録の区別

- `report-initial.md` / `verdict-initial.json`: 初期候補のREVISE判定。
- `dom-events.json` / `edge-probes.json` / `frozen-suite.json`: 初期候補。
- `revised1/`: 最初の修正後。F2の照会例外経路がまだ残る。
- `report.md` / `verdict.json`: 最終判断が更新されるファイル。
- `dom-events.mjs` / `edge-probes.mjs`: private checkpointに保持した初期評価の元コード。公開コピーには含めず、reproduce版を使用する。
- `reproduce-*.mjs` / `reproduce-negative-controls.py` / `recheck-focused.mjs`: 共有可能な再実行コード。

原文captureを読みhash照合する `independent-checks.py` はprivate研究archiveへのpathを必要とするため、公開再現コードには含めない。source→claim判断は報告に記録した原典位置とclaim scopeで確認する。
