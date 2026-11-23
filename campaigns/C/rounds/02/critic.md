# Round 02 independent critic — initial review

**判定: REVISE。** 通常の型付き参照、テーマ合成、必須role、名前衝突、限定literal CSS出力は確認できた。ただし、深い入力と数値/文字コードの境界で、候補が約束する通常の診断結果から外れる例外経路を再現した。ブラウザー、AT、描画コントラスト、forced-colors、WCAGは引き続き **HOLD / NOT_TESTED**。

## 方法と証拠

- 同一モデルの別タスクで実施した独立レビュー。人、異モデル、秘匿holdoutではない。費用unknown。
- `plan.json` と `evaluation-plan.md` を変更せず、候補snapshotの5ファイルのハッシュ一致を実行後にも確認した。実装、registry、git commitは変更していない。
- `independent-probes.py` は親のunit testをimportせず、正常対照と反例を生成して実際の `build()` とPython subprocessのCLIを呼ぶ。R1の44 vectorsのうち親testで使われなかった境界を優先し、独自の深さ、件数、CLI入力、転用例を加えた。browser、server、保護設定変更、別環境再試行は行っていない。
- 初回 `initial-results.json` は排他的作成で保存。**73 cases: 生集計67 pass / 6 fail**。うち `cli-deep-json` はcriticのoracleが厳しすぎたため欠陥から除外する。1200段arrayを当該JSON parserが受理した後、`CONFIG_SHAPE`、exit 1、CSS nullを正常返却しており、parse error exit 2を要求する根拠がなかった。**裁定後は68正常 / 5実失敗（3欠陥群）**。初回値は修正・上書きしていない。
- 親の既存token unitもこのタスクで再実行し、17/17 pass。checked-in `booking-tokens.css` と候補が生成した文字列は完全一致。
- 親から報告された総Python33、Node6、人工的な浅いcontrolのfalse accept 7→0は別の証拠。ここではgeneration uplift、設計品質向上率、前production版との差とは解釈しない。

再現コマンド（新しい出力名を指定する。初回ファイルは保持される）:

```sh
python3 campaigns/C/rounds/02/independent-probes.py --out /tmp/c-round02-critic-replay.json
python3 -m unittest discover -s modules/ui-engineering-design-system/tests -p test_tokens.py -v
```

## R02-CR-01 — group深さ制限より前のcopyが再帰例外を漏らす

- **重要度:** medium / acceptance blocking。実装が宣言した資源上限と失敗診断の問題。
- **位置:** `modules/ui-engineering-design-system/checks/tokens.py:194–209` (`merge`、特に204の`deepcopy(base)`)、59–67 (`reject_value_constructs`)、231–297 (`build`はTokenErrorのみ捕捉)。
- **入力:** `group-depth-1200`。正常なnumber role `reading` に加え、`base.deep` の下を1200個の `g` objectで包み、その末端へnumber tokenを置く。追加対照 `deep-malformed-value` はnumberの$value内に1200個のnested objectを置く。
- **症状:** いずれも `build()` が `RecursionError: maximum recursion depth exceeded` を外へ送出。通常のFAIL report、theme/path、宣言済み `LIMIT/GROUP_DEPTH` を得られない。31/32段側の超過はGROUP_DEPTHとして処理され、浅い正常対照も通るため、特定の未対応型を要求した結果ではない。
- **根拠:** `token-contracts.md` の上限表と22行のLIMIT診断方針、analysis U1の「資源上限を区別、例外落ちを成功として返さない」、`build()`自身の「all themes or diagnostics」という公開契約。DTCGの普遍要件ではない。
- **影響:** `build()`を組み込むconsumerは、一律のstructured reportを前提にできない。CLIではRecursionErrorを捕捉する経路もあるが、group limitのtheme/path診断が消える。偽PASSやCSSの破壊は観測していない。
- **修正案:** deepcopy/merge前にiterativeな入力構造・深さの検査を行うか、深さを明示的に持つbounded copy/mergeにする。$valueの不正深さにも安定したLIMITまたは型形状診断を返し、buildの境界で最終的な資源例外を診断へ変換する。Pythonの再帰上限を緩める解決は不要。
- **再現:** 上記probe commandの `group-depth-1200` と `deep-malformed-value`。詳細結果は `initial-results.json` の同ID。

## R02-CR-02 — 有限整数の文字列化に未宣言の上限がある

- **重要度:** medium / acceptance blocking。
- **位置:** `tokens.py:40–41` (`finite`は全intを受理)、213–218 (`number_text`)、278–297 (serialization中のValueError非捕捉)。
- **入力:** `large-integer-serializer`。numberの$valueに `10**5000` を与えるPython build API入力。これは有限intであり、現在の文書には数値桁数の上限がない。
- **症状:** `str(int(value))` がPythonの4300桁変換上限に達し、ValueErrorを外へ送出する。初回probeは安全なFAILを期待したが、本来は「この大きさをサポートして成功」または「明示された局所上限によりstructured LIMIT」のどちらも選べる。**特定の値を拒否すべきというDTCG判断はしていない**。欠陥は宣言・通常診断なしの例外である。
- **根拠:** 文書のnumber有限数値契約と明記済み実装上限表、U1の数値範囲/資源制限を明記する指示。
- **影響:** 有限数値の妥当性判定を通った後にcompilerが落ちる。CLIでは同規模のJSON整数がそれ以前のparse段階で別途落ちる（CR-03）。
- **修正案:** bounded digit/magnitude policyを値検証と文書に加え、number/dimension/durationへ一貫して適用する。または安全にserializationできる実装を用いる。既定セキュリティ制限の解除は不要。限界付近の正常値と超過値を分けて再試験する。
- **再現:** 上記probe commandの `large-integer-serializer`。

## R02-CR-03 — CLIの文字コード/整数parse失敗がJSON診断を返さない

- **重要度:** medium / acceptance blocking。
- **位置:** `tokens.py:309–312` (`load`)、315–338 (`main`のexcept tuple)。文書のCLI終了コード契約は `token-contracts.md:65`。
- **入力:** `cli-invalid-utf8` は `ff fe ff` の3byte。`cli-oversized-json-integer` は `{"n":` + 5001個の`9` + `}`。いずれも事前に既存CSSへ `PREVIOUS VALID CSS` を書く。
- **症状:** 前者はUnicodeDecodeError、後者はValueError。ともに **exit 1、stdoutなし、stderrにtraceback**。文書で入力解析/I/O失敗に指定したexit 2 + JSON diagnosticにならない。前のCSSは両方で保持される。
- **根拠:** 候補自身のCLI契約。これはDTCG conformanceやブラウザーの動作とは無関係。
- **影響:** CIがexit codeとJSON diagnosticsで「検査拒否」と「入力解析失敗」を区別できない。エラーは成功には見えていないが、通常のreport schemaが壊れる。
- **修正案:** UTF-8を明示し、decode failure、JSON parse時のinteger-limit ValueErrorを適切なIO_OR_PARSE/LIMIT diagnosticへ正規化する。例外を無差別に握り潰すより、load境界で原因を分類する。既存CSS保持とexit 2も再検証する。
- **再現:** 上記probe commandの `cli-invalid-utf8` と `cli-oversized-json-integer`。初回stderr末尾とreturncodeをJSONに保存済み。

## 通過した判断と正常対照

| 領域 | 確認した挙動 |
| --- | --- |
| 型・alias | 未明示aliasの親/参照型矛盾はCONTRACT。明示型で同一対象へ解決した対照は成功。group/property参照、self-cycle、未使用でも壊れたtokenは拒否。 |
| 未対応構文 | $root/$ref/$extends/$extensions/$deprecated/$schema、P3、sRGBのnoneをUNSUPPORTEDとして拒否。DTCG一般の不正にはしていない。 |
| 値の境界 | boolean、非有限数、sRGB範囲外、alpha、4/8桁hexを拒否。負duration/寸法、単位付きゼロ、sRGB正常値は成功。 |
| テーマ・role | baseからのrole継承成功。後半のthemeだけの型変化でも全体FAIL、themes空、CSS null。role欠落とtoken/group変換を拒否。 |
| 名前・metadata | A/aとDay/dayの区別を維持。名前/prefix/theme injectionとhyphen結合衝突を拒否。空group/文字列description正常、description型不正/未知wrapperを拒否。 |
| 明示上限 | alias 256ノード成功、257ノードLIMIT。token 10000成功、10001 LIMIT。浅いgroup超過はLIMIT。深い場合のみCR-01。 |
| CLI・出力 | syntax、duplicate JSON member、NaN、overflow float、後半theme失敗、output I/O失敗を失敗として扱う。既存CSS保持。正常時だけ置換。 |
| 転用 | booking以外のsensor/industrial consoleのmetric・settling time・grid寸法へ、既存paletteや普遍roleを作らず同じ仕組みを適用できた。 |

## 研究・登録文面と実装主張の照合

researcher-1/2のmd/json、analysisのmd/json、registry C-UI-005/006/007を照合した。参照先型と親型の文面差は局所policyとして残り、ASCII名、必須role、置換単位、single bundle、literal出力、実装上限も製品方針と明記される。registryのstatusはDRAFT、verificationはNOT_RUN、implementation/transfer confidenceはunverifiedのままであり、研究案の試験を実行済みへ書き換えていない。

原典factsと現実装policyの致命的な食い違いは今回の資料間比較では見つからなかった。ただし、これは全文の独立原典確認ではない。両Researcherが記録した取得失敗、reader断片、Colorのrewritten summary、Style Dictionary issueの歴史的性格と版未確認を維持する。現在の完全DTCG対応やlatest tooling supportへ一般化しない。

生成reportは `dtcg_conformance: NOT_CLAIMED`、visual各欄は `NOT_TESTED`。文書もCSS runtime aliasの追従、入れ子テーマ、描画コントラスト、forced-colors、AT、WCAGを検証済みと呼んでいない。見た目の好み、文体、特定の語の出現を欠陥判定に使用していない。

## 修正後に必要な限定再検証

CR-01〜03の反例を修正前のまま再実行し、初回結果と別ファイルへ保存する。deep JSONのoracle訂正は明記し、成功かstructured failureかを実際の契約に沿って判定する。数値桁数policyを新設する場合は境界内外の正常対照を追加する。これらが解消し、既存の正常値/全theme原子性を維持できた場合だけ、tested graph/contract範囲をACCEPT候補とする。visualのHOLDは残る。
