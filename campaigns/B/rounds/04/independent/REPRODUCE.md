# B-R04 Critic 再現手順

リポジトリrootをcwdにするか、`B_REPO_ROOT` に指定する。script自身の配置は任意。原典capture、元環境の絶対パス、privateなbrowser制御情報は不要。

## 固定された二つのsuite

```bash
node modules/interaction-ux-flow/tests/test_batch_flow.mjs
node modules/interaction-ux-flow/tests/test_batch_boundaries.mjs
```

前者は元の13ケース、後者は候補作成前に別枠で固定した3基準。実装モジュールは各suiteの第1引数でも指定できる。

## 実HTMLのイベント

Nodeとjsdom 26.1.0を使用した。既存のjsdomを `B_DOM_JSDOM_PATH` に指定するか、再現スクリプトから `jsdom` として解決できるようにする。このスクリプトは依存をインストールしない。

```bash
export B_REPO_ROOT="$PWD"
export B_DOM_JSDOM_PATH="/absolute/path/to/node_modules/jsdom"
export B_CRITIC_OUTPUT_DIR="/absolute/path/to/reproduction-output"
node /path/to/reproduce-dom-events.mjs
```

`B_CRITIC_OUTPUT_DIR` を省略するとOSのtemporary directoryに新しい出力フォルダを作る。`B_REPO_ROOT` を省略するとcwdを使う。module/HTMLのパスを第1・第2引数で指定できる。

実HTMLのsingle ESM importだけを、同じ候補モジュールからimportしたfactoryへの参照に置換する。イベントハンドラ、fixture service、renderのコードは書き換えない。`.click()` とchangeイベントを実行し、DOM文言・calls・effects・server・viewを記録する。

初期REVISEの表示欠陥を再現する場合：

```bash
node /path/to/reproduce-dom-events.mjs campaigns/B/rounds/04/artifacts/initial/batch-flow.mjs campaigns/B/rounds/04/artifacts/initial/batch-flow.html
```

期待結果は代表7/7、探索1/3。EDOM02/EDOM03は終端後の追加確認案内で失敗する。これは初期欠陥を検出した正常な負の結果で、固定13の失敗ではない。

修正後に実行した限定再確認：

```bash
export B_CRITIC_CASE_IDS="DOM03-LOST-RESPONSE-LOOKUP-CANCEL,DOM05-CANCEL-ALREADY-APPLIED-UNKNOWN,EDOM02-SUCCESS-AFTER-CANCEL-HAS-TERMINAL-COPY,EDOM03-CANCELLED-HAS-TERMINAL-COPY"
node /path/to/reproduce-dom-events.mjs
```

4件PASSを確認した。全DOMを実行するときは `B_CRITIC_CASE_IDS` を解除する。

## module探索と選択した故障対照

```bash
node /path/to/reproduce-edge-probes.mjs
python /path/to/reproduce-fault-controls.py
```

どちらも `B_REPO_ROOT` と `B_CRITIC_OUTPUT_DIR` を利用する。出力先省略時は新規temporary directory。fault controlは候補のコピーへ4種類の故障を入れ、未変更の固定／補足suiteで想定したassertion failureが出るかを確認する。元候補を変更しない。意味のある4つの欠陥検出の確認であり、網羅的mutation評価や生成baseline比較ではない。

## 原典照合の再現範囲

公開リポジトリではsource registryのlocator、hash、要約と `source-checks.json` の確認内容を参照できる。exact byte比較の再実行には保持されたprivate研究captureとraw receiptが必要であり、公開harnessへそれらを埋め込んでいない。`source-check-attempts.json` は比較手順の失敗と訂正を保存するが、原典本文を含まない。

jsdomは実ブラウザ、視覚確認、AT、人間評価ではない。独立とは担当コンテキストと実行の分離を意味し、別モデルまたは人の客観評価という意味ではない。
