# Round 02 critic — 修正後の独立再検査

**判定: ACCEPT（実行したgraph / contract範囲に限定）。** 初回のR02-CR-01〜03は、同じ反例で通常の診断が返ることを確認した。元の73ケース相当と追加52ケース、**合計125/125 pass**。既存token unitも再実行し、**19/19 pass**。ブラウザー、描画コントラスト、forced-colors、入れ子テーマ、AT、WCAGは引き続き **HOLD / NOT_TESTED**。

## 証拠の分離と再現

初回 `independent-probes.py`、`initial-results.json`、`candidate-snapshot.json`、`critic.md/json` を保持した。plan/evaluation-planも含め、再検査の前後でSHA-256一致を確認した。初回判定REVISEを変更せず、後続の修正と結果をこのファイル、`recheck.json`、`recheck-results.json` に分けた。

初回は73件中67 pass / 6 raw fail、裁定後68正常 / 5実失敗だった。`cli-deep-json`の初回oracle誤りは、修正実装の受領前にcritic.mdへ記録済み。今回もケースIDと順序を維持し、その訂正を明示的に適用した。v2 sourceと実行対象候補のハッシュはrecheck.jsonに保存している。

```sh
python3 campaigns/C/rounds/02/independent-probes-v2.py --out /tmp/c-round02-recheck-replay.json
python3 -m unittest discover -s modules/ui-engineering-design-system/tests -p test_tokens.py -v
```

出力先は未作成のファイルを指定する。probeは既存の結果ファイルを上書きしない。

## 元の欠陥の再現結果

| 指摘 | 元の反例 | 修正後の観測 | 判定 |
| --- | --- | --- | --- |
| CR-01: copy前の深さ制限欠落 | 1200段group / 1200段の不正$value | `build()`からFAIL、`LIMIT/JSON_DEPTH`、入力パス、CSS null、themes空。`resolve()`も同じ構造化例外を返す | 解消 |
| CR-02: 巨大int文字列化例外 | `10**5000` | 文字列化前に`LIMIT/INTEGER_SIZE`。正負1,024bit上限内は成功、1,025bitは拒否 | 解消 |
| CR-03: CLI decode/parse例外 | 無効UTF-8 / 5001桁JSON整数 | exit 2、JSON diagnostic、CSS null。tracebackなし。入力と既存CSSを保持 | 解消 |

**JSON_DEPTHを許容した理由:** 親実装は入力全体の深さ64を明示的な局所上限として追加したため、1200段入力はgroup検査より前に止まる。初回の`GROUP_DEPTH`という特定codeから`JSON_DEPTH`に変わっても、LIMITとして拒否し、path付き診断を返し、CSSを出さないという反証条件は維持している。未捕捉例外、成功、CSS出力、未知の分類を許す変更は行っていない。

`cli-deep-json`の1200段arrayはJSON parserが解析できるため、解析後の`LIMIT/JSON_DEPTH`によるexit 1が文書の契約に合う。解析器自体の再帰限界を超える10,000段arrayは別に実行し、exit 2 / IO_OR_PARSE / RecursionErrorの診断を確認した。どちらも成功にはならず、既存CSSを保持した。

## 追加した境界と正常対照

| 対象 | 境界内の確認 | 境界外の確認 |
| --- | --- | --- |
| JSON深さ | resourcesの63・64は通過。build内の深さ64不正numberは通常のNUMBER_VALUEへ進む | 65はLIMIT/JSON_DEPTH。buildとCLIでも同じ分類 |
| JSONノード数 | resources 249,999・250,000を通過。250,000ノードの有効token文書はbuild/CLIとも成功 | 250,001はLIMIT/JSON_NODES。CSSなし、既存出力保持 |
| 整数bit長 | `±(2**1024-1)`をnumber / dimension / durationで成功。resolveとCLIでも確認 | `±2**1024`をLIMIT/INTEGER_SIZE。CLIはparse前段拒否のexit 2 |
| 浮動小数 | 正負最大有限値、正負最小subnormal、負ゼロを受理 | 元ケースのboolean・NaN・無限大・1e999は引き続き拒否 |
| JSON解析 | 正常JSON、最大整数境界、最大有限float、最小subnormalからCSSを生成 | 不正構文、重複key、NaN/±Infinity、巨大整数、切れたUTF-8、不正な先頭ゼロ、parser深度超過は通常診断 |
| ファイル | 正常時のCSS置換、入力JSONのbyte一致 | 失敗時の既存CSSのbyte一致と入力JSONのbyte一致。CRLFを含む既存出力でも保持 |

JSONの深さ64を通過するresource対照は、DTCG token文書全体の受理を意味しない。groupの深さ32や各型の形状制約が別に存在するため、resource検査後に通常のINVALIDとなる対照も含む。25万ノードの成功例は、正常なnumber roleに合法な空groupを加えた文書であり、roleやtoken数の上限を変えていない。

元ケースの型・parent alias矛盾、合法な未対応構文、負duration、theme別のrole/型、A/a、名前注入、空group、metadata、衝突、全テーマ成功時だけの出力、別用途への転用は維持できた。bookingのchecked-in CSSとの完全一致も再確認した。

## 原典と局所policy、未確認範囲

`token-contracts.md` の上限表はJSON深さ64、ノード数250,000、整数絶対値のbit長1,024を**規格上の上限ではなく実装契約**と明記している。拒否結果も`LIMIT`であり、合法なDTCG構文の一般的な不正とは扱っていない。CLIのparse前段と解析後でexit codeが異なることも文書化された。

`dtcg_conformance: NOT_CLAIMED` とvisual各欄の`NOT_TESTED`を維持している。完全原文を独立再取得したという主張は追加していない。初回研究記録のreader断片、Color rewritten summary、原文fetch失敗、Style Dictionary現行版の未確認はそのまま留保する。

これは同一モデルの別タスクによる独立再検査であり、人・異モデル・秘匿holdoutではない。費用unknown。125件の合格を網羅的証明、デザイン品質向上、generation uplift、ブラウザーやアクセシビリティ適合へ拡張しない。今回のcriticは実装・registry・commitを変更しておらず、browser/server/保護設定変更も行っていない。
