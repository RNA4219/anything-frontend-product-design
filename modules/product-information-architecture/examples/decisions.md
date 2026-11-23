# 判断例：適用・反例・不適用

以下は架空の設計例であり、研究の観察結果や検証済み製品ではない。数値の実績・利用率は作らない。
JSONは[契約](../references/plan-contract.md)の部分抜粋。完全なbrief/planではないため、そのまま自動検査へ渡さない。
既存visual_intentのIDを保持する。ここで扱わない状態遷移・部品・見た目の実装はB/Cへ渡す。

## 例1：年に数回でも必須なら残す

対応：[A01・A02・A04](../references/goals-and-features.md)

### 入力

監査担当auditorは、指定期間の記録を監査資料として渡す必要がある。
g_auditはmust、r_auditはmandatory、f_audit_exportもmandatoryと依頼で確定している。
実行頻度は低い。必要情報はaudit_periodとrecord_scope。実行時の生成待ち・失敗・再試行はまだ設計していない。

### 適用する判断

頻度より先に必須達成を保護する。f_audit_exportをkeep/requiredにし、対象期間・出力範囲を判断する画面へ置く。
出力処理の状態をAで作り込まずBへ渡す。必須の依存が判明すればそれも保持する。

~~~json
{
  "id": "f_audit_export",
  "label": "監査資料の出力",
  "disposition": "keep",
  "target": null,
  "object": "audit-record",
  "outcome": "deliver-audit-package",
  "roles": ["auditor"],
  "goal_ids": ["g_audit"],
  "requirement_ids": ["r_audit"],
  "dependencies": [],
  "reason": "指定期間の記録を監査資料として渡す必須要件を満たす",
  "priority": "required",
  "priority_basis": "頻度は低いが、依頼で必須と確定した監査資料の提供を支える"
}
~~~

### 反例

「ほとんど使われないのでremove」「通常業務の画面から消したので機能もdefer」とする。
前者は必須達成を失い、後者は機能の提供と入口の配置を混同する。

### 不適用・確認点

依頼にmandatoryがなく、単に監査という語があるだけなら必須と推定しない。
必要性が未確定なら保持案とproductへの確認を残す。出力結果の確認方法が必須達成に影響するならBへのblocking残件にする。

## 例2：役割が違う機能を同じ画面に置く

対応：[A03](../references/goals-and-features.md)、[A05〜A07](../references/information-architecture.md)

### 入力

f_member_findとf_staff_findは対象directory-entry、成果choose-entryが同じ。
前者のrolesはmember、後者はstaff。両者が見るname/statusは共通公開情報であると確認済み。
各目標の必要情報もname/statusであり、選択後の作業は別に定義されている。

### 適用する判断

roleが異なるためmergeしない。共通情報から対象を選ぶ局面は同じ画面に同居できる。
featuresには両IDをkeepで残す。画面の共用を機能統合として数えない。

~~~json
{
  "id": "s_directory",
  "title": "対象一覧",
  "purpose": "次に扱う対象を選ぶ",
  "goal_ids": ["g_member_find", "g_staff_find"],
  "feature_ids": ["f_member_find", "f_staff_find"],
  "roles": ["member", "staff"],
  "entry_for": ["member", "staff"],
  "information": [
    {"id": "name", "visibility": "primary", "reason": "対象を識別する"},
    {"id": "status", "visibility": "primary", "reason": "対象が選択条件に合うか判断する"}
  ]
}
~~~

### 反例

「同じ一覧だからrolesを合算して一機能にする」。
対象が同じでも成果が閲覧と変更で違う場合、成果が同じでも対象が人と設備で違う場合もmergeしない。

### 不適用・確認点

staffだけが見られる情報が必要なら、上の共通画面案をそのまま適用しない。
情報権限を契約上表せない場合は画面分割かB/Cへのblocking残件を選び、すべての情報を全roleに許可したことにしない。

## 例3：同じ機能の別入口を正本化する

対応：[A02・A03](../references/goals-and-features.md)、[A05・A06](../references/information-architecture.md)

### 入力

f_searchとf_search_menuは同じ対象catalog、成果find-candidate、role buyer、要件r_findを支える。
検索対象、必要情報、権限、業務条件、例外も同じと確認済み。違いは入口の呼び名だけ。
g_findはmust、r_findはmandatoryと確定している。機能の正本は一つでよいが、必要な入口を一つに減らすという要求はない。

### 適用する判断

f_searchをkeep正本にし、f_search_menuをmergeする。入力IDを削除しない。
必要な複数入口から同じ正本を使う画面へ到達できるようにし、別名はdecision_notesへ残す。

~~~json
[
  {
    "id": "f_search",
    "label": "候補を検索",
    "disposition": "keep",
    "target": null,
    "object": "catalog",
    "outcome": "find-candidate",
    "roles": ["buyer"],
    "goal_ids": ["g_find"],
    "requirement_ids": ["r_find"],
    "dependencies": [],
    "reason": "同じ条件で候補を探す機能の正本",
    "priority": "required",
    "priority_basis": "must目標の候補探索を支える"
  },
  {
    "id": "f_search_menu",
    "label": "メニューから検索",
    "disposition": "merge",
    "target": "f_search",
    "object": "catalog",
    "outcome": "find-candidate",
    "roles": ["buyer"],
    "goal_ids": ["g_find"],
    "requirement_ids": ["r_find"],
    "dependencies": [],
    "reason": "入口名だけが異なり、対象・成果・役割・必要情報・権限・条件が一致",
    "priority": "required",
    "priority_basis": "必須達成の対応を正本f_searchへ保持する"
  }
]
~~~

### 反例

同じ「検索」という名称だけを根拠に、全件検索と閲覧許可済み対象の検索を統合する。
「最近使った対象」も一覧だから同じ成果と推定する。別の範囲・判断目的なら統合しない。

### 不適用・確認点

三項目や権限が不明な場合は両方keepで保持し、確認する。
正本化後も画面が統合元IDを参照する、targetがdeferを指す、統合先をさらに統合する案は修正する。

## 例4：比較材料をprimaryに残し、スクロールを許す

対応：[A05・A07](../references/information-architecture.md)、[A08・A09](../references/disclosure-and-verification.md)

### 入力

g_compareは複数の機器候補から調達対象を選ぶmust目標で、f_compareはkeepの正本として定義済み。
必要情報はcompatibility、lead_time、quantityで、各候補の値を同時に照合する必要がある。
値は入力データから用意する。以下は値や互換性の判定結果を発明する例ではない。

### 適用する判断

一つの比較責務を持つs_compareへ情報を揃える。primaryは展開不要であり、長い一覧のスクロールは許す。
候補が同じ属性で比較されるなら、それを別カテゴリへ閉じ込める案より、共通集合と絞込を検討する。

~~~json
{
  "id": "s_compare",
  "title": "候補比較",
  "purpose": "条件に合う調達候補を選ぶ",
  "goal_ids": ["g_compare"],
  "feature_ids": ["f_compare"],
  "roles": ["buyer"],
  "entry_for": [],
  "information": [
    {"id": "compatibility", "visibility": "primary", "reason": "各候補が必要条件に適合するか比較する"},
    {"id": "lead_time", "visibility": "primary", "reason": "各候補が必要な時期に間に合うか比較する"},
    {"id": "quantity", "visibility": "primary", "reason": "各候補で必要な数量を満たせるか比較する"},
    {"id": "optional_glossary", "visibility": "secondary", "reason": "今回の判断に必須でないと確認済みの用語補足"}
  ]
}
~~~

s_compareへの認可された入口とgoal_routeは別途必要。entry_forが空でも、正当な入口から辿れればよい。

### 反例

「一画面一話題」を適用し、互換性・納期・数量をそれぞれ別画面にする。
比較属性を閉じたパネルへ入れ、クリックすれば見られるからprimaryとする。
行数を減らすために候補や属性を落とす。これらは比較のための記憶・往復を増やす。

### 不適用・確認点

一つの対象へ順に入力するフォームでは、順序に沿った分割が適する場合がある。比較画面の同時参照と混同しない。
データがない、情報権限が不明、端末で同時参照できるか未確認なら、それぞれ残件として書く。
上のprimary指定だけで実際の描画・読み取りを検証したことにはならない。

## 例5：延期と折りたたみを混同しない

対応：[A03・A04](../references/goals-and-features.md)、[A08](../references/disclosure-and-verification.md)

### 入力

f_saved_filtersは個人用の絞込条件保存。g_personalizeはcould、mandatoryはfalse。
今回のmust目標は都度の絞込で成立し、他のkeep機能は条件保存に依存しないと確認済み。
提供時期を後へ回す案を検討している。

### 適用する判断

提供の延期ならf_saved_filtersをdefer、targetはnullとする。理由に失われる補助的成果とmustを保てる根拠を書く。
decision_notesとunresolvedに再検討条件を残す。入力feature IDは削除しない。

~~~json
{
  "id": "u_saved_filters",
  "category": "function",
  "owner": "product",
  "impact": "条件の再利用を延期するが、今回の必須探索は都度の絞込で維持する",
  "blocking": false,
  "question": "繰り返し作業の負担を確認し、条件保存の提供時期を再判断する"
}
~~~

### 反例

機能は提供したまま設定を閉じておきたいだけなのにdeferとする。
未使用というログだけでremoveにし、少数roleの要件や必須依存を調べない。

### 不適用・確認点

条件保存が必須業務やアクセシビリティ上の既知の必要条件なら、同じ延期案は使えない。
非表示の目的ならkeepを維持し、A06/A08で入口と情報を計画する。展開挙動はB/Cへ渡す。

## 例6：フォームの段階分けを作業全体の法則にしない

対応：[A07](../references/information-architecture.md)、[A08](../references/disclosure-and-verification.md)

### 適用

申請の入力順に独立した判断局面があるなら、必要な情報と前後関係を列挙して段階分けを検討する。
最終確認に複数項目が同時に必要なら、その確認局面には必要項目を揃える。前の入力画面を記憶する設計にしない。
保存・再開・戻る・入力エラーの状態はBへ渡す。

### 反例

フォーム向けの「進みやすさ」を理由に、一覧比較や監視対象を一つずつ別画面へ強制する。
逆に、画面を減らすために独立した認可条件や判断局面をすべて混ぜる。

### 不適用・確認点

段階分けを必要とする根拠がない短い作業へ、自動的にウィザードを追加しない。
[USWDSの複雑なフォームの資料](https://designsystem.digital.gov/patterns/complete-a-complex-form/progress-easily/)は、その文脈で読む。
[WAIのshort critical paths](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o5p02-short-paths/)は補足ガイダンスであり、規範的WCAG適合の判定材料として単独使用しない。

## 例7：構造確認、未実行、HOLDを区別して報告する

対応：[A10](../references/disclosure-and-verification.md)

### 入力と適用

手動で参照IDを点検したが、構造チェッカーと利用者テストは未実施。
必須操作の結果確認が未設計で、Bが判断する必要がある場合の記録例：

~~~json
{
  "decision_notes": [
    "A10: 参照IDと統合先は机上で照合。構造チェッカーは未実施。",
    "A10: ラベル理解、実作業、実装表示、視覚意図の実現は未検証。"
  ],
  "unresolved": [
    {
      "id": "u_result_confirmation",
      "category": "interaction",
      "owner": "B",
      "impact": "必須操作の結果を利用者が確認する方法が未確定",
      "blocking": true,
      "question": "成功・失敗を区別して結果確認できる状態設計を定義する"
    }
  ]
}
~~~

報告例：「機能と経路の設計案を作成し、参照を机上確認しました。自動検査と利用者検証は未実施です。必須の結果確認が未確定のためHOLDです。」

### 反例

「JSONが整っているのでPASS、使いやすさも検証済み」とする。
チェッカーを実行して構造上PASSが得られた場合も、利用者の理解・操作の成功まで証明したと書かない。

### 不適用・確認点

未実行のコマンドに結果を付けない。利用者テストを実施した場合は、対象・タスク・観察結果を記録して検証範囲を広げる。
この架空例の報告文を、今回実行した事実として転用しない。

## 例8：Aを起動しない範囲

既存情報と機能・経路を変えずに配色や書体だけを調整する依頼は、既存Art DirectionとC側の作業。Aの機能削減を追加しない。
送信中・失敗・再試行・フォーカス等だけを直す依頼はB/Cへ。Aは新しい目標・必須情報・経路への影響がある部分だけを受け取る。
原則の出典は各referenceのSourcesを読む。本SkillのID・JSON手順は導出した運用であり、上の架空例も効果検証には数えない。
