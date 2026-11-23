# 設計判断の入出力契約

この契約は画面へ機能を配置する前の設計を検査する。JSON は設計の正しさそのものを保証しない。文章だけの依頼では最初に同じ項目を表にしてよい。自動検査を使うときだけ JSON にする。

## 入力 brief.json

必須: `case_id`, `roles`, `goals`, `requirements`, `feature_requests`, `visual_intent`。

- `roles`: `{id, label}`。匿名利用者や管理者も別の role として登録する。
- `goals`: `{id, role, outcome, priority, needed_information}`。priority は `must|should|could`。needed_information は判断に不可欠な情報の ID 配列。文言の好みは含めない。
- `requirements`: `{id, goal_ids, mandatory, statement}`。mandatory は依頼で確定した要件。推定値を勝手に mandatory にしない。
- `feature_requests`: `{id, label, object, outcome, roles, goal_ids, requirement_ids, dependencies, mandatory}`。機能名の数で目標を代用しない。重複・過剰な要求も入力から消さず残す。
- `visual_intent`: `{id, constraints}`。既存 Art Direction が決めた配色・書体・構図等。A は ID をそのまま引き継ぐ。
- 任意の `content` / `contexts` / `constraints`: 実際の表示データ、利用頻度、件数、端末、権限、業務条件。観測か仮定かを書き分ける。

不足情報は仮定として置き、判断への影響を明記する。既存機能の削除に不可欠な事実が不明なら、機能を保持して `unresolved` に残す。

## 出力 plan.json

トップレベルに `schema_version: "1.1"`, `case_id`, `visual_intent_id`, `features`, `screens`, `navigation`, `goal_routes`, `unresolved`, `decision_notes` を置く。

### features

入力の各 feature ID を一度ずつ含める。足りない機能を提案するときは `add_` で始まる新しい ID にし、根拠を記録する。

```json
{"id":"f_queue","label":"対応一覧","disposition":"keep","target":null,
 "object":"ticket","outcome":"select-ticket","roles":["operator"],
 "goal_ids":["g_triage"],"requirement_ids":["r_triage"],"dependencies":[],
 "reason":"未対応の対象を選ぶため。担当別の表示は同じ集合のビューにする。",
 "priority":"required","priority_basis":"未対応の見落としが当日の対応期限に影響する。"}
```

`disposition` は `keep|merge|defer|remove`。merge は入力IDを廃止せず `target` に循環なくkeep正本へ解決する feature ID を指定する。remove/defer/keep の target は null。merge では object/outcome/roles と必要情報・権限を保つ。異なる対象や権限は同じ画面へまとめても同じ機能とは数えない。

priority は `required|high|medium|low`。数値の根拠がなければスコアを捏造せず、頻度・失敗影響・期限・依存関係による比較理由を priority_basis に書く。変更した outcome 等は decision_notes で理由を示す。mandatory な機能を黙って落とさない。

### screens

```json
{"id":"s_queue","title":"対応一覧","purpose":"着手する問い合わせを選ぶ",
 "goal_ids":["g_triage"],"feature_ids":["f_queue"],"roles":["operator"],
 "entry_for":["operator"],
 "information":[{"id":"severity","visibility":"primary","reason":"優先順位判断に必要"}]}
```

primary はその画面で展開操作をせず参照できる情報。スクロールが不要、常に above-the-fold という意味ではない。secondary は詳細展開・別領域で参照する補足。各画面の purpose は一つの判断を表す。複数の比較対象・一括操作等、同時参照が必要なら複数機能を同居させる。feature_ids は keep の正本だけを参照する。entry_for はこの画面が入口になる role の配列。

### navigation / goal_routes

```json
{"from":"s_queue","to":"s_detail","label":"問い合わせの詳細",
 "roles":["operator"],"kind":"contextual","rationale":"選択した同一対象の情報へ進む"}
```

kind は `global|local|contextual`。検索・絞込・設定の表示を無条件に global にしない。ここでは情報上の到達関係だけを扱い、保存/送信等の状態遷移は B に渡す。正当な戻りリンクや巡回を不具合扱いしない。

同じ短いlabelが異なる行先へ向かう場合、checkerは`AMBIGUOUS_SIBLING_LABEL`でHOLDにする。選択時に使える行見出し・対象名等の関連文脈を、この契約だけでは検査できないためである。HOLDは曖昧さの確定でも合格でもない。実際の表示と文脈をrationale/decision_notesへ記録して確認する。確認できた文脈を含む識別表記をlabelに使う場合も、実UIの短文言との対応を残す。存在しない文脈やラベルで検査を回避しない。プログラム上の関連付けと規格適合はCが確認する。

```json
{"goal_id":"g_triage","start_screen":"s_queue","target_screen":"s_queue",
 "notes":"重要度・期限・担当の一覧比較で着手対象を決める"}
```

must の目標は認可された入口から target へ辿れ、target が goal を担当し、needed_information を primary で提供する。should/could の延期は decision_notes と unresolved で理由を明記する。検査は role ごとの到達性を確認するが、ラベルを人が理解できるとは証明しない。

### unresolved / decision_notes

```json
{"id":"u_volume","category":"information_architecture","owner":"A",
 "impact":"件数不明のため分類数の妥当性は未確認","blocking":false,
 "question":"実データの上位分類と件数分布を観察する"}
```

category は `function|information_architecture|interaction|visual|implementation`。owner は `A|B|C|D|product`。blocking=true の残件があれば自動検査は HOLD。状態遷移・ARIA・描画など担当外の問題もこの形式で引き渡す。

decision_notes は判断理由の文字列配列。仮定、採用しなかった案、分類の多重所属、維持すべき視覚意図、利用者検証の未実施を記録する。

## 検査の範囲

```bash
python3 checks/validate_plan.py --brief brief.json --plan plan.json --output result.json
```

exit 0 = 構造的違反を検出せず、exit 1 = 検出、exit 2 = 入力不正。`PASS` はこの検査の結果だけで、Skill昇格や人のタスク完了率ではない。見た目・自然なラベル・実際の業務適合は別途評価する。

## 1.1 追加データフィールド

入力の各feature_requestは scope（対象範囲ID）、lifecycle（existing/proposed）、availability（available/partial/planned/unknown）、context_constraints（端末・契約等の条件ID配列）、evidence_refs（入力evidenceのID）を持つ。evidence各件はid/kind/statement/coverage/coverage_statusを持つ。kindはrequirement/observation/assumption/unknown、coverage_statusはverified/partial/unknown。

出力の全featureにはscope、context_constraints、evidence_refsを追加する。既存の機能をremove/deferする場合は retirement:{need_status, replacement, legacy_entry_action, data_handling, revisit} を追加する。need_statusはended/continued_elsewhere/scope_change/unknown。replacementはfeature IDかnull。それ以外の欄は文字列。新規機能のdeferにはrevisitを文字列で付ける。小変更ではこの全形式でなく、同じ判断を短い表で記録してよい。

既存機能のcontinued_elsewhereではreplacementがkeepの正本へ解決し、元の対象・成果・role・scope・関係する利用条件を保持する。入力のavailabilityがplanned/unknownなら現在の代替としてはHOLD。partialなら出力正本にverified_outcomes（確認済み成果ID配列）を付け、その確認根拠をevidence_refsとreasonに記す。全能力の同等性を主張せず、必要範囲だけを検証する。

既存機能のremove/deferにunknownなneed_status、または未確認・部分的な観測しかない場合はHOLD。検査がverifiedな証拠IDを認識しても、その記述が削除を意味的に正当化するかは別に読む。仕様の必須条件も証拠として扱えるが、利用ログの観測とは区別する。

1.0の入力は従来検査として扱い、結果のchecks_available.context_and_retirement=falseを残す。新規判断の検証は1.1を使う。

必須goalのtarget_screenには、そのgoalとroleを満たすkeep機能をfeature_idsで割り当てる。画面にgoal IDと情報IDだけを記載しても、別の孤立画面に機能を置く案は到達済みにならない。既存機能のmergeでも、removeと同じく正本が現在提供されるかを入力から確認する。別名の連鎖は循環なくkeepに解決する場合に許容し、公開する入口は必要に応じ正本へ整理する。

この契約ではscreens.rolesの全役割へ、その画面の全feature_idsが提示される。部品ごとの権限分岐は未モデル化なので、role限定機能を共用画面へ無条件配置しない。同じ実URLでも役割別の画面ビューとして分けるか、設計未決として引き渡す。認可処理が実装済みであるとは証明しない。
