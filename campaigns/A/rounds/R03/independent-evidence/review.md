# SESSION A — R03 独立レビュー

## 最終判定

**修正確認済み。レビューした範囲で残る阻害的指摘はない。** 親によるC01–C03修正後、独立8ケースと正本aliasの正負pairを限定再実行し、全て期待どおりだった。明示必須能力の孤立だけを検出し、別段階配置・should/couldの提供・明示deferと共有支援を維持する。旧A08のblocking条件と点検範囲も整合した。修正前の結果は上書きせず保存した。詳細はcorrection-check.json。

匿名2案はW=6/6、Z=6/6、差0で、割当手掛かり漏洩がある。構造・手順の修正確認をSkillの実利用効果の証明とはしない。

## 修正前の結論と記録

R03の狭い変更である「宣言したgoal_routesのtargetは、priorityにかかわらず対応keep能力とneeded_informationを持つ」は、独立fixtureで意図どおりに動いた。should/couldの未宣言経路を一律に追加する過剰制約は見つからなかった。

ただし、明示必須の複数能力の一部が孤立画面にあると通る**既存の検出範囲の穴**を確認した。また、旧A08と追加条件のblocking判定、must限定の点検文を揃える文書修正を推奨する。個別の再現・影響・修正案はfindings.jsonのR03-C01〜C03。

## 独立性と実行範囲

- 題材は架空の共同窯の焼成予約・釉薬比較・台帳書き出し。評価briefの契約プラン比較とは異なる。
- 最初の11例は親のtest_information_obligations.pyを読む前に作成し実行した。実装と入出力契約は先に読んだため、ブラックボックス独立性までは主張しない。
- その後、親のコード読解による仮説に対して別の必須能力と段階別正例を2例追加した。親起点の仮説と独立発見を混同しない。
- baselineとcandidateを同じJSONへ実行した。55 unittest methodsも再実行しOKだった。
- 公開repo編集・子エージェント起動・ブラウザー再試行は行っていない。

## 正負例と範囲

| ケース | baseline | candidate | 解釈 |
|---|---:|---:|---|
| 全priorityで提供し、能力と情報が揃う | PASS | PASS | 正例 |
| 提供するshouldの必要情報をsecondaryへ | PASS | FAIL | R03で検出 |
| 提供するcouldの必要情報が欠落 | PASS | FAIL | R03で検出 |
| should判断先に能力がなく別画面に置く | PASS | FAIL | R03で検出 |
| 任意作業は明示defer、共有enablerだけkeep | PASS | PASS | 過剰制約なし |
| 条件が非該当と明記した別場面 | PASS | PASS | 条件の意味は手動照合 |
| 情報IDを保って値を未確認と記録 | PASS | PASS | 値が既知という意味ではない |
| 一つのgoalに複数の補助能力、target別配置 | PASS | PASS | 全能力のtarget同居を強制しない |
| mustの必要情報をsecondaryへ | FAIL | FAIL | 既存検査を維持 |
| 文章だけの任意提供宣言でroute省略 | PASS | PASS | optional_goal_delivery=falseの限界 |
| 未測定をゼロとする説明 | PASS | PASS | information_values=falseの限界 |
| 明示必須2能力が別段階で到達可能 | PASS | PASS | 別段階正例 |
| 明示必須2能力の一方だけ孤立 | PASS | PASS | 既存検出範囲の穴、意味上は不成立 |

実行スクリプトはcounterexamples/run_independent.py、追加仮説はrun_mandatory_reachability.py。各caseのbrief、plan、両checker結果を保存した。

## 原典と導出の照合

6件の新規資料の必要箇所だけを直接再確認した。原responseはこのprivateフォルダーに保存し、公開資料へ全文は複製していない。

| 原典 | 確認箇所 | レビュー判断 |
|---|---|---|
| DWP What a component means | Content the user can skip / Answering the user's question | 非該当の利用者が省略できる補足と、その時点の問いを扱う。全利用者の全値を隠してよい根拠にはしていない。 |
| GOV.UK Details | When to use / When not to use / 明瞭なラベル | 一部向けの情報にDetailsを許容する助言。現Skillは全面禁止とせず、primaryを独自契約と明示する。 |
| DWP How to choose components | 5 steps / Where this guidance comes from | 作業・必要情報・見落としの結果を考える出発点。固定規則または独立した効果実験として扱っていない。 |
| Chernevほか2015 | Abstract / Preference uncertainty / Prior meta-analytic research | 候補数の条件差と、知識・選好の違い。画面密度の万能上限を導出していない。訂正本文の取得制約を保持し、詳細効果量は再利用しない。 |
| Scheibehenneほか2010 | Abstract | 平均と研究間のばらつきを区別する。2015研究と元研究が重なり、独立した二回の再現とは数えない。 |
| HL7 DataAbsentReason | unknown / not-applicable / not-performed / masked | 未知・非該当・未実施・秘匿の語義。一般UIへ医療コードの採用、全欠測理由の公開、HL7適合を要求していない。 |

政府ガイド3件は関連系列であり、メタ分析2件も元研究が重複する。これにHL7の語義資料を合わせた「6件」は、6件の独立実証を意味しない。候補数研究から今回の業務UIの速度や誤り改善を主張する記述も確認しなかった。

## 意味照合と自動検査を分ける

自動検査はID・配置・宣言した経路を扱う。値の真偽、条件成立、文章だけの提供宣言を推定しないことは新falseフラグと資料に明示されている。独立の意図的な誤り（未知をゼロと記述）でPASSになることを確認したが、これはR03が自動解決した欠陥として数えない。

手動のSkill手順では、条件が有効な判断時点、未知値の影響範囲、具体値と補助説明、明示延期、共有支援を別に照合する。この区別は新refに揃っている。旧A08のblocking文言とverification範囲は統合が必要だった。

## 評価の限界

匿名2案を固定D1–D6で採点し、W=6/6、Z=6/6、hard failureは双方0件、得点差0だった。Z成果物中のbaseline入力パスにより割当手掛かりが漏れており、完全な盲検とは主張しない。詳細はblind-evaluation.json/md。各arm1回・同系モデルの合成課題であり、人の操作・実API・描画・アクセシビリティは未確認。HTMLソースの照合を実ブラウザーの観察や人の効果に置き換えない。

## 照合に用いた原典リンク

- [R03-R1-S01](https://design-system.dwp.gov.uk/choose-a-component/how-to-choose-components/what-a-component-means) — L320-328, L363-380。
- [R03-R1-S02](https://design-system.service.gov.uk/components/details/) — L90-103, L141-143。
- [R03-R1-S03](https://design-system.dwp.gov.uk/choose-a-component/how-to-choose-components) — L286-312, L335-340。
- [R03-R2-S01](https://chernev.com/wp-content/uploads/2017/02/ChoiceOverload_JCP_2015.pdf) — Abstract, Preference uncertainty, Prior meta-analytic research。
- [R03-R2-S02](https://bear.warrington.ufl.edu/brenner/mar7588/Papers/scheibehenne-jcr2010.pdf) — Abstract。
- [R03-R2-S03](https://terminology.hl7.org/en/CodeSystem-data-absent-reason.html) — L42-55。
