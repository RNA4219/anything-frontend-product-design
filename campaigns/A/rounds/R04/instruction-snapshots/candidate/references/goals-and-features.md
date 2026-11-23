# 目標・要件・機能の設計

[入出力契約](plan-contract.md)のIDと列挙値を使う。以下の表は作業用であり、plan.jsonに未定義のトップレベル項目を追加しない。
観測・依頼で確定した事項・仮定を区別する。既存のvisual_intentは参照IDを維持し、配色・書体・構図の再設計は行わない。
Aは提供する機能と情報の構造を扱う。保存・送信・失敗・待機等の状態設計はB、部品・描画・アクセシビリティ実装はCへ引き渡す。

## A01 達成内容を先に定義する

### Trigger

新規設計、機能追加、機能整理、画面分割の依頼で、誰が何を達成するかが曖昧なとき。既存計画を変更するときも、影響を受ける目標に適用する。

### Inputs

- `roles`、`goals`、`requirements`、`feature_requests`、`visual_intent`。
- `contexts`等にある対象、業務条件、期限、権限、利用場面。記載がなければ「未確認」とする。
- 具体例があれば成功例だけでなく、例外・やり直し・他者への受渡しも読む。

### Decision Rules

- 目標は「roleが、対象について、どの結果を得るか」で記述する。「ダッシュボードを使う」「ボタンを押す」は達成内容の代用にしない。
- 入力で確定した目標・必須条件を、実装しやすい内容へ書き換えない。言い換える場合は同一性を確認し、原文と変更理由を残す。
- 「何を達成するか」と「今回の設計でどう達成するか」を分ける。先に画面・部品・操作回数を固定しない。
- 役割、対象、達成内容が不明で判断が逆転しうる場合は、削除・統合を確定せず保持案を作る。

### Procedure

1. 各goal IDについて、role、対象、達成結果、必要情報、成功を判断する事実を作業表に並べる。
2. 「この機能がなくても同じ結果に到達できるか」を問い、機能名を目標から分離する。代替案の存在はまだ削除理由にしない。
3. 各目標について具体的な一件を選び、開始時に分かる情報、判断、必要な結果、例外を記述する。実例か仮例かを明記する。
4. 依頼から確定できない事項は仮定として列挙する。必須達成や権限の不明点は、`unresolved`に質問・影響・担当を置く。
5. 入力自体に欠落がある場合は入力補完案を示す。未合意の仮目標を、既存goal IDやmandatoryの確定値として黙って注入しない。
6. 目標と必要情報が整理できた範囲からA02へ進む。全件の調査完了を待つ必要はないが、未確認点を完了扱いしない。

### Output Contract

- `features[*].goal_ids/object/outcome/roles/reason`に達成内容との関係を保持する。
- `goal_routes`は後続の画面設計で具体化する。意味上の目標整理だけで到達可能と記録しない。
- 仮定と変更理由は`decision_notes`に「A01: goal ID、仮定、影響」の形で記録する。
- `visual_intent_id`は入力のIDを引き継ぐ。達成内容を美的な統一へ置き換えない。

### Failure Modes

- 曖昧な「管理」「確認」を、そのまま全利用者共通の目標にする。
- 一つの便利な事例を処理できたので、他の利用者・例外も満たせると推定する。
- ユーザーが挙げた機能を、そのまま独立した目標として数える。
- 仮定の業務ルールをmandatoryに昇格する。

### Verification

各goalについて「誰が、何を判断・達成し、何を見れば成功と分かるか」を一文で説明する。説明できない目標と、実例で確認していない条件を明示する。
必要情報が具体的なIDになっているか確認する。目標を読むだけで特定の画面形式に拘束されていれば、達成内容と設計案を再分離する。

### Sources

- S12 [Lewis / Rieman, Chapter 2](https://hcibib.org/tcuid/chap-2.html)：設計に依存しない代表タスクと、特定設計に依存するシナリオを区別する。
- S11 [Kieras, Task Analysis and the Design of Functionality](https://web.eecs.umich.edu/~kieras/docs/TA_Modeling/TaskAnalysisV2.pdf)：仕事の達成と機能選定をUI詳細より前に扱う。
- S02 [18F User stories](https://guides.18f.org/methods/decide/user-stories/)：保存された方法資料。現行の政府指針として扱わない。

### Confidence / Limits

原典の方法論を根拠にしている。本Skillの作業表・IDへの転記手順は導出した運用で、効果検証済みの規格ではない。
実作業や対象者へ接触していない場合、目標の妥当性は仮説のまま。必須達成の内容が未確定ならproduct担当のblocking残件にする。

## A02 goal → requirement → featureを双方向に追跡する

### Trigger

機能を追加・統合・延期・削除する前、および画面へ配置する前。入力の対応IDが与えられている場合も、参照があるだけで整合しているとはみなさない。

### Inputs

- goal ID、requirement ID、feature IDと各記述、mandatory、dependencies。
- A01で整理した達成内容・必要情報・例外。
- 既存の対応関係と、その根拠。単に同じ単語を含むことは根拠にしない。

### Decision Rules

- 一つの目標に複数要件・複数機能が対応してよい。一対一対応へ無理に変換しない。
- 前向きには「この要件をどの利用可能な機能が満たすか」、逆向きには「この機能を何の要件・目標のために残すか」を説明する。
- IDの存在確認と、実際に要件を満たす意味上の確認を分ける。
- 統合元の入力IDを消さず、循環なしでkeepの正本へ解決できる対応を残す。循環・行方不明・defer/removeへの統合は認めない。
- 必要な機能がない場合は追加候補を作る。根拠のない機能を発明して空欄を埋めない。

### Procedure

1. 作業表に「goal ID → requirement ID → feature ID → 提案disposition → 正本ID → 充足理由」を作る。
2. 全goal・全requirementを前向きにたどる。必須要件を実現する機能と、その成立条件を記す。
3. 全featureを逆向きにたどる。未対応を見つけたら、不要と即断せず入力漏れ・独立した業務目的・重複の可能性を確認する。
4. A03で統合を認めた場合、正本へgoal_idsとrequirement_idsの対応を保存する。誤った対応まで無条件に合算しない。
5. 必要な依存関係をkeepの正本へ解決する。利用中の機能がdefer/removeに依存する案は修正するかblocking残件にする。
6. 不足機能には`add_`で始まるIDを付け、既存機能で満たせない理由と対応要件を書く。
7. A06・A08の後に、必須目標の経路と必要情報まで追跡を延ばす。表の対応だけでタスク完了を宣言しない。

### Output Contract

入力feature IDは`features`に一度ずつ出す。`goal_ids`、`requirement_ids`、`dependencies`、`disposition`、`target`、`reason`を整合させる。
作業表の判断理由は`decision_notes`へ保存する。欠落の影響は`unresolved`に記録し、担当をAまたはproductにする。
追跡表自体をplan.jsonの未定義キーとして追加しない。必要なら別の説明表として添える。

### Failure Modes

- 機能名を似た要件へ機械的につなぎ、充足理由を省略する。
- 統合後に元のgoalやrequirementが消える。
- 低頻度の依存機能を削除し、上位の必須機能だけを残す。
- 必須要件の空白を、存在しない追加機能の実装済み扱いで埋める。

### Verification

全入力featureの出現回数、全参照ID、統合先のkeep、依存の利用可能性を確認する。
次に必須要件ごとに、具体的な一件を対応する機能で処理できる説明を確認する。説明できない場合は「追跡IDはあるが充足未確認」と記録する。

### Sources

- S01 [NASA 6.2 Requirements Management](https://www.nasa.gov/reference/6-2-requirements-management/)：システム工学の要求管理。UI用の列や判定への転用は本Skillの導出。
- S12 [Lewis / Rieman, Chapter 2](https://hcibib.org/tcuid/chap-2.html)：抽象的要件と、機能を一体として使う代表タスクの相互補完。
- S04 [18F Make research actionable](https://guides.18f.org/ux-guide/research/make-research-actionable/)：保存版の研究運用資料。現行政府方針の証拠にはしない。

### Confidence / Limits

双方向追跡の考え方と、このJSON形式が有効であることは別問題。この契約・手順そのものの使いやすさは未検証。
対応IDが完全でも要件の正しさ、実装、業務適合は証明できない。削除に必要な充足事実が不明ならkeepを維持する。

## A03 統合・削除・延期・非表示を区別する

### Trigger

「重複を減らす」「シンプルにする」「画面をまとめる」「使われない機能を消す」という要求、またはA02で重複・孤立候補が見つかったとき。

### Inputs

各featureのobject、outcome、roles、必要情報、権限、業務条件、依存、必須性、利用の根拠。画面の見た目やラベルの類似だけでは足りない。

### Decision Rules

- object、outcome、rolesのいずれかが異なればmergeしない。同画面への配置は別判断として許容する。
- 三項目が同じでも、必要情報・権限・業務条件が異なる場合は統合を確定しない。
- `merge`は同じ機能の正本化、`remove`は提供の廃止、`defer`は提供の延期、`keep`は提供の維持。
- 非表示・折りたたみ・二次画面への移動は提供の廃止ではない。keepを維持し、A06・A08で到達性と情報開示を設計する。
- 利用者ごとの未使用部分、低頻度、表示面積の大きさだけでは削除しない。
- 必須機能を統合する場合も、同一性・充足・依存を正本へ維持する。必須性を消す操作としてmergeを使わない。

### Procedure

1. 候補ペアごとにobject、outcome、rolesを比較する。rolesは順序を無視したID集合として比較し、異なる役割を一括化しない。
2. 一致したペアのみ、必要情報・権限・業務条件・例外の一致を確認する。不明なら独立keepとする。
3. merge可能なら既存IDから安定した正本を一つ選ぶ。元IDを残してtargetを循環なくkeep正本へ解決させ、別名と対応要件を失わない。
4. remove候補は、必須でないこと、必要依存がないこと、目標・要件・経路を失わないこと、業務上不要とする根拠を確認する。
5. 上記が不足する場合はkeepとunresolvedに戻す。could/shouldを延期する場合は延期理由・影響・再検討条件を記録する。
6. 「一覧から目立たせない」が目的ならremove/deferにしない。必要な入口を残し、表示の挙動はB/Cへ渡す。
7. 画面の同居だけを行う場合、元の複数featureをkeepで保持する。機能削減数として数えない。

### Output Contract

- merge: `target`は循環なくkeep正本へ解決するfeature ID。他のdisposition: `target:null`。
- `screens.feature_ids`はkeep正本だけを参照する。共有画面でも異なる機能IDを残す。
- `screens.information.visibility`は情報の開示属性であり、機能の廃止を表すフィールドではない。
- 統合・廃止・延期の根拠を`reason`に、非表示の目的と未設計の挙動を`decision_notes/unresolved`に置く。

### Failure Modes

- 「担当者向け」「申請者向け」を同じ画面名だから統合する。
- 比較、閲覧、編集を同じ対象への操作だから同一機能にする。
- deferを「今は閉じている」の意味で使う。
- 現在使わない機能を、将来や別役割でも不要と推定する。

### Verification

merge全件で三項目と権限等を再比較し、正本まで循環なく解決できるか確認する。
remove/defer全件で、必須性・依存・残る経路・必要情報を逆引きする。欠落理由が低頻度だけなら採用しない。

### Sources

- S14 [McGrenere / Moore, Are We All In the Same “Bloat”?](https://www.dgp.toronto.edu/~joanna/papers/gi_2000_bloat.pdf)：未使用と望まれない機能、利用者差を調査。
- S15 [McGrenere et al., Multiple Interface Design](https://www.dgp.toronto.edu/~joanna/papers/JMcGrenere_CHI_2002.pdf)：個人用UIと全機能UIを評価。個人化の費用にも制約がある。
- S11 [Kieras](https://web.eecs.umich.edu/~kieras/docs/TA_Modeling/TaskAnalysisV2.pdf)：機能が共同で実作業を支えるかを検討する。

### Confidence / Limits

三項目一致を統合の前提とする規則は、本Skillの保守的な導出であり、原論文がこのJSON判定を実証したものではない。
論文の対象製品・利用者と今回の業務は異なる。利用記録や権限の証拠がなければ、統合・削除を「検証済み」としない。

## A04 必須条件を守って優先順位を付ける

### Trigger

機能・画面の数、開発量、初期表示の負担を減らす必要があるとき。A03の変更を採用する前にも適用する。

### Inputs

目標のmust/should/could、依頼で確定したmandatory、依存関係、頻度、失敗影響、期限、代替手段。観測値と仮定を分ける。

### Decision Rules

- 優先順位付けに先立ち、必須条件を満たす案を維持する。低頻度の必須機能も残す。
- mandatoryな機能、その正本、必須達成に選択した機能と成立に必要な依存はrequiredとして扱う。
- 頻度だけで順位を決めない。失敗影響、期限、他の必須達成を支える依存を併せて比較する。
- 根拠のない点数・重み・利用率を作らない。外見上の単純さを必須達成より優先しない。
- 要件に代替案がある場合、全候補を必須とするのではなく、選択案で充足できる根拠を残す。不明なら既存の提供を保つ。

### Procedure

1. mandatory機能と必須要件・must目標を列挙し、A02でその実現経路と依存を確認する。
2. required集合を守ったうえで、残る候補を失敗影響・期限・頻度・依存・代替可能性で比較する。
3. high/medium/lowの理由を一件ずつ書く。「便利」「一般的」だけでは順位を付けない。
4. mustやmandatoryを満たせない資源制約がある場合、黙って格下げせずproduct担当のblocking残件にする。
5. should/couldの延期には、失われる結果と再検討条件を記す。単に低順位というだけでremoveにしない。
6. 変更後に依存を再確認し、必要な低頻度機能が残っているか点検する。

### Output Contract

`priority`は`required|high|medium|low`。`priority_basis`には判断に使った事実と仮定を書く。
入力にないmandatoryを作らず、必須条件の変更要求は`unresolved`へ残す。延期の理由は`decision_notes`にも記録する。

### Failure Modes

必須の復旧・取消・期限対応を利用率だけで落とす。依頼のmustを見た目の都合でshouldへ変える。要望調査の人気順を利用後の有用性と同一視する。

### Verification

必須要件・must目標を起点にkeep正本、依存、経路、primary情報を再確認する。required以外へ分類した必須機能があれば理由を再審査する。
順位の根拠が推定だけのものを一覧化し、実測したように表現していないか確認する。

### Sources

- S01 [NASA Requirements Management](https://www.nasa.gov/reference/6-2-requirements-management/)：要求の管理と変更の考え方。UIの順位規則は本Skillの導出。
- S13 [Thompson et al., Feature Fatigue（MSI working paper）](https://thearf-org-unified-admin.s3.amazonaws.com/MSI/2020/06/MSI_Report_05-101.pdf)：利用前後の評価を区別する。短期実験であり普遍的な最適機能数は与えない。
- S11 [Kieras](https://web.eecs.umich.edu/~kieras/docs/TA_Modeling/TaskAnalysisV2.pdf)：頻度だけでなく仕事・依存・誤りの影響を分析する入口。

### Confidence / Limits

required保護と順位理由の記録は本Skillの運用規則で、順位スコアの実証モデルではない。
失敗影響や期限が不明な必須経路は、低順位へ仮置きせず保持して確認する。資源制約を解消したと主張できるのは合意された条件がある場合だけ。

## R03補足：明示必須機能の到達性

宣言した経路を持つgoalについて、入力でmandatory=trueかつ同goal・同roleに結び付けられた各機能は、正本解決後の所有画面が、そのgoalの認可された宣言入口の少なくとも一つから到達できることを確認する。targetに一つ対応機能があれば残りも利用可能とは扱わない。

必要な機能をすべてtargetへ同居させる必要はなく、別段階の画面でも到達できればよい。依存機能を一律mandatoryへ昇格せず、別roleの支援、経路を提供しない任意goal、宣言されていない状態条件の成立を推測しない。これは画面間の構造検査で、利用順序や実行成功は別途B/Cで検証する。

検証：同じgoalを支える明示必須機能の一つだけを孤立画面に置く反例をFAILとして検出し、認可入口から別段階の画面へ辿れる正常例と正本への統合をPASSとして保つ。
