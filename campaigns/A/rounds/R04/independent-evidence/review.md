# R04 独立レビュー — 初回候補

## 結論

**初回候補は REVISE。比較ロジックの独立12ケースは全件期待と一致したが、CLIの出力先が入力と同じ実体の場合にsnapshotを上書きする1件を修正する必要がある。**

初回候補の13ファイルは `candidate-snapshot.json` のhashと一致した。確認した候補を `inspected-snapshot/` に保存している。本レビューは公開repoを変更していない。

採否は検証範囲を限定した実装・指示の評価であり、実データ移行の承認、実画面の成功、人の探索効率を意味しない。同系モデルの別スレッドによる評価であり、客観的な人間評価とは呼ばない。

## 独立検証の範囲

親側の `tests/test_inventory_comparison.py`、R04 inventory-cases、96件課題、rubric/oracle、匿名生成案を読む前に、植物標本庫を題材とする入力・期待結果を作成して保存し、その後にhelperを実行した。候補のコード・指示・研究者の原典整理は先に読んだ。研究者文書には提案テストの記述も含まれており、この既知情報をmanifestに記録した。

| ケース | 観測結果 |
|---|---|
| 行と集合値の順序変更 | 差分なし。期待一致 |
| 同数・同じ表示名で別の実IDへ入替 | removed/added IDを報告 |
| 分類別件数を保った所属交換 | 実レコード別の所属差分を報告 |
| 妥当な改名と入口移動 | 通常の差分。無条件拒否なし |
| 根拠を併記したID承継 | ID差分と未検査根拠欄を報告。同一性は推定しない |
| 正当な複数所属 | 受理して所属差分のみ報告 |
| 同一IDでrole/scope変更 | 両者を別の差分として報告 |
| 部分取得・集合外参照・未知メタデータ | 集合外と未検査欄を明示。意味的不備と断定しない |
| 明示的な空集合 | 受理。母集団の真偽は保証しない |
| 同一集合の重複ID | INVALID_INPUT / exit 2 |
| 型不正・必須値欠落・重複所属 | 具体箇所を返してINVALID_INPUT |
| case/revision/basisの不一致・任意値の欠落 | 警告と宣言値差分を返す |

初回入力は `fixtures-initial/`、事前登録hashは `fixtures-initial-manifest.json`、全実結果とstdout/stderrは `initial-results/`、照合結果は `initial-results-summary.json` に保存した。12件すべて期待と一致した。

## 修正が必要な1件

### R04-CR-001 — 出力先が入力snapshotを上書きする

- **場所:** `checks/compare_inventory.py` 初回候補145–147行、`main()` の出力処理。
- **症状:** `--output` に `--before` と同じpathを指定すると、入力が比較結果JSONに変わる。`--after` を指すsymlinkを出力先にしても再現した。いずれもexit 0 / COMPARED。
- **根拠:** module docstringはsource mutationなしと述べるが、実装は入力を読み込んだ後、出力と入力の同一実体を検査せず `write_text` する。
- **影響:** 取得時点の入力内容を失い、同じsnapshotによる再現・再比較ができなくなる。結果に残る入力hashから内容は復元できない。
- **修正案:** 書込み前に両入力との同一実体を判定し、同一なら入力を保持して非0終了する。通常の同一路径・解決済みpathだけでなく、既存ファイルのsymlink/hardlinkも `samefile` 等で扱う。衝突エラー自体をそのpathへ書かない。
- **再現:** 使い捨てコピーに対して `--before before.json --after after.json --output before.json`。別変形ではafterを指すsymlinkへ出力。`supplemental-initial/13_output_aliases_source/` に前後bytes・hash・実行コマンドを保存。

この仮説は親から初回12ケースの後に提示された。本担当が別環境コピーで再現したが、独立発見とは数えない。元の独立fixturesは保持している。重大度はmedium、helperの採用には修正を要する。

## 原典と設計上の導出

6資料の必要部分を原典で確認した。NISO PDFは直接openが一度失敗したが、公式掲載ページのリンクから取得でき、PDF index108 / 印刷p97を目視した。確認記録は `source-verification.json`。

| 原典 | 確認した範囲と候補への評価 |
|---|---|
| [SKOS Reference](https://www.w3.org/TR/skos-reference/) §10.6.3、10.6.7–8 | mappingと同一資源を分け、周辺関係の自動継承をしない境界は妥当。実レコード移行の成功条件そのものではない |
| [SKOS Primer](https://www.w3.org/TR/skos-primer/) §3.2–3.3 | 資源への付与と概念を分け、複数主題を認める説明を確認。同じW3C系統の非規範説明で独立実証には加算しない |
| [NISO Z39.19-2005(R2010)](https://groups.niso.org/higherlogic/ws/public/download/12591/z39-19-2005r2010.pdf) §11.3.1.2、11.3.2.1–2 | 過去の索引への変更影響と履歴、未付与語の例外、一対一置換と複雑な変更の区別を確認。現行版・有効性は未確認のまま |
| [GOV.UK Taxonomy principles](https://www.gov.uk/government/publications/govuk-topic-taxonomy-principles/govuk-taxonomy-principles) §2.1、3.2、3.5 | 主題分類の目的、標本点検、件数均等化の限界を確認。他の軸を禁止せず、GOV.UKの子分類数推奨も一般規範へ転用していない |
| [SharePoint managed metadata](https://learn.microsoft.com/en-us/sharepoint/managed-metadata) | term ID・複数ラベル・local/global利用範囲と管理権限の説明を確認。実レコードIDや閲覧認可成功とは別に扱う |
| [SharePoint term operations](https://learn.microsoft.com/en-us/sharepoint/create-and-manage-terms) | copy、reuse、delete、deprecate等の作用差を確認。製品固有仕様として限定されている |

これらは4つの出典系統であり、6本の独立実験ではない。候補はID・所属の残差照合とPython受渡し形式をSkill側の導出と明記している。原典の定めた同一JSONや全件人手検査として記述していない。

## 条件・例外と既存責務

**条件と例外の扱いは妥当。** 既存集合の再編時だけ比較範囲を固定し、部分集合を全体保証に変えない。妥当な改名・承継・分割・統合・追加・終了・複数所属を許し、差分の存在だけで不合格にしない。未使用語の扱いも実際のscope・所属・他参照への影響に限定される。新しい承認フローを一律に追加していない。

**既存A05–A07との重複はあるが、追加の責務は限定される。** 同名同一視の回避、正本と複数入口、role別到達、比較情報の保持は既存事項。R04の有用な追加は、概念・実レコード・所属・入口を分けた変更前後の照合と、件数が同じでも対象や所属を交換できる点の明示である。A06/A07はその差分を入口・判断場所へ戻す接続として読める。

registryの三unitに共通の例外・出典が反復されるため、将来の更新時には記述のずれに注意する余地はある。ただし今回の指示を矛盾させる重複は検出しておらず、新しい評価項目や必須ファイルを増やすほどの問題にはしない。

`plan-contract.md` と `validate_plan.py` は基準commitから変更されていない。任意snapshot形式はplan 1.1から分離されており、概念所属をfeatures.targetへ押し込まず、新トップレベル必須項目も追加していない。小変更は短い表、正規化できない場合も表で確認できるため、全件JSON作成や全role×全itemの人手試験を強制していない。

## 未確認と次の段階

source truth、全体完全性、意味同等性、変更承認、認可・索引、実探索、人の成果は、比較成功からは判定できないと出力と文書に明記されている。これらを検出しないこと自体をhelperの欠陥には数えない。

ブラウザー描画は実施していない。既知のsandbox起動制約を再試行せず、静的HTMLから実操作や利用者効果を宣言していない。親が報告した68-method suiteも、本担当が独立実行した成功件数には含めていない。

初回結果は保持し、修正後は別ファイルへ再検証結果を保存する。匿名2案の固定採点は未実施で、受領を待つ。
