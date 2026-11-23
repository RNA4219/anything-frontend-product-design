# R03 匿名2案の評価（割当手掛かり漏洩あり）

## 結論

**Wは6/6、Zも6/6。得点差は0、hard failureは両案とも0件。** 固定したD1–D6を変更せず採点した。この課題のHTMLソース・設計・JSONでは、両案が必要情報、shouldの提供作業、未知値、補足開示を保持していた。

完全な盲検は成立していない。baseline/candidateのフォルダーやunblinding.jsonは開いていないが、Z/design.md:136にbaseline/input/product-ia/SKILL.mdというパスがあり、割当の手掛かりが漏れていた。親へ採点確定前に報告し、同じ資料と基準を保持した。

## 固定基準の採点

| 基準 | W | Z | 確認根拠 |
|---|---:|---:|---|
| D1 判断場所に必要条件・比較情報を展開なしで置く | 1 | 1 | 両HTMLの比較表で全3候補、上限、総額、期間と比較基準を保持。必要情報はdetails外。 |
| D2 should/couldでも提供する作業の情報を保つ | 1 | 1 | 両案ともCT-75の通知日数・未知の更新日・返金条件を別領域で展開不要にする。 |
| D3 未知状態を確定値へ変換しない | 1 | 1 | P-100不適合、P-200保留、P-300適合が事前oracleと一致。期限日付を創作しない。 |
| D4 作業に応じて密度・開示を決める | 1 | 1 | 初回説明と反復比較を分けて説明し、同じ候補集合・属性を比較表へ保つ。万能上限なし。 |
| D5 非該当・不要な補足は開示候補にできる | 1 | 1 | 適否に関係しない2補足題名だけがdetails内。全情報の常時表示は強制しない。 |
| D6 検証範囲を分け、visual_intentを維持する | 1 | 1 | existing-team-adminと標準HTML制約を保持。構造・ソースと描画・人・実APIを分けて報告する。 |
| **計** | **6** | **6** | **差0** |

## 具体的な場所

### W

- **D1 = 1** — P-100/P-200/P-300の候補ID、人数上限、年間上限、年総額、契約期間と基準を同じ表のdetails外に置く。各必要IDはprimary。 参照: W/preview.html:17-70; W/plan.json:screens[s_compare].information。
- **D2 = 1** — shouldの解約条件確認を今回提供する作業として保持し、CT-75・30日・次回更新日未確認・返金なしを展開不要の領域に置く。延期と混同しない。 参照: W/preview.html:86-105; W/design.md:26-33; W/plan.json:goal_routes[g_review_cancel]。
- **D3 = 1** — P-100不適合、P-200未確認ゆえ判断保留、P-300適合が事前oracleと一致。次回更新日を作らず期限日付は未確定。未知原因も推測していない。 参照: W/preview.html:41-46,62-74,91-104; W/design.md:44-65; W/plan.json:unresolved[u_p200_quota,u_contract_renewal]。
- **D4 = 1** — 初回向け用語説明と同時比較表を組み合わせ、反復での候補別往復を避ける意図を説明。3候補と必要属性を保持し、要素数・カード数の万能上限を作らない。 参照: W/design.md:20,67-78,90-100; W/preview.html:20-70。
- **D5 = 1** — 今回の選択条件を変えない2つの補足題名だけを内容の分かるsummaryから開示。本文未提供を明記し、必要値や全情報の一律開示を強制しない。 参照: W/preview.html:76-83; W/design.md:67-78。
- **D6 = 1** — existing-team-adminを維持し、標準HTMLのみ。自作の構造・ソース照合を公式checker、ブラウザー描画、実操作、アクセシビリティ、実利用と分け、未実施を明記する。 参照: W/design.md:102-145; W/preview.html:8,110; W/plan.json:visual_intent_id,decision_notes。

### Z

- **D1 = 1** — P-100/P-200/P-300と必要な人数・年間上限・年総額・期間・比較基準を同じ表のdetails外へ配置。必要IDもprimaryで保持する。 参照: Z/preview.html:17-82; Z/plan.json:screens[s_plan_compare].information。
- **D2 = 1** — shouldの現契約条件確認を提供する。CT-75・30日・未確認の更新日・返金なし・期限判定に不足する情報を常時展開の領域に置き、deferしていない。 参照: Z/preview.html:96-112; Z/design.md:5-11,24-36; Z/plan.json:goal_routes[g_review_cancel]。
- **D3 = 1** — oracleの不適合／未確認／適合の区別と一致。P-200の上限をゼロや無制限にせず、CT-75の期限を創作しない。既知条件を捏造・改変しない。 参照: Z/preview.html:24,44-49,72-82,101-112; Z/design.md:38-64; Z/plan.json:unresolved[u_p200_quota,u_ct75_renewal]。
- **D4 = 1** — 初回説明、反復比較、同時参照を別に扱い、比較表を選んだ理由と未測定の効果を明記。全3候補と属性を維持し、普遍的要素数制限は置かない。 参照: Z/design.md:66-75,86-94; Z/preview.html:24-81。
- **D5 = 1** — 比較条件に影響しない補足2件をdetailsに置き、本文・リンク先未提供を保持する。必要条件は開示内へ移さず、全情報常時表示の規則を課していない。 参照: Z/preview.html:86-93; Z/design.md:66-75。
- **D6 = 1** — 視覚意図existing-team-adminと標準HTML制約を保持。自作チェック・ソース確認、公式checker、描画、操作、認可、アクセシビリティ、人の評価の範囲を分ける。 参照: Z/design.md:21,96-125; Z/plan.json:visual_intent_id,decision_notes; Z/preview.html:1-122。

## 独立の静的確認

共通briefのSHA-256は事前oracleと一致し、両案のplan/design/previewの全6ファイルもsnapshotと一致した。独立のHTMLParserで、各goalの必要情報IDが宣言targetにあり、details外であること、アンカー先が存在すること、外部資産・script・form等を含まないことを確認した。これはソースの検査であり、ブラウザーを開いた確認ではない。詳細はblind-source-check.json。

## 限界と解釈

- 各armは1回、同じモデル系列の独立スレッドによる合成課題。反復試行・人による評価ではない。
- HTMLソースの静的確認だけであり、描画、スクロール時の収まり、操作、読み上げ、認可、実APIは未実行。
- 独立にJSON/HTMLのハッシュ・情報ID・details祖先・アンカーを照合したが、arm自身が申告する過去の自作チェックの実行ログはこの匿名資料に含まれない。
- baseline/candidateのフォルダーとunblinding.jsonは開いていない。ただしZ/design.md:136のbaseline/input/product-ia/SKILL.mdが割当手掛かりを漏らし、完全な盲検は成立していない。Wの追加reference名からも推測が可能。
- この固定briefには確認済みゼロ、未計測の確定理由、条件成立が変化する別場面のデータはない。D3/D5の点は今回の未知値と補足開示での充足に限り、全境界の実証を意味しない。
- 両案6点は固定D1–D6で差を観測しなかったことを示す。実用上の完全同等、一般的な品質PASS、Skillの改善効果または無効果を証明しない。
- 共通の詳細なbrief・契約が両案へ与えられているため今回の課題は差を検出しにくい可能性があるが、これは推測であり測定された感度ではない。

D1–D6の点差を得るために基準を追加・変更せず、曖昧な見栄えの好みで欠陥を作らなかった。未知と既知ゼロ、共有enabler、条件分岐等の広い境界は別の独立fixtureとSkill手順レビューで確認し、この2案の点数へ重複加算しない。
