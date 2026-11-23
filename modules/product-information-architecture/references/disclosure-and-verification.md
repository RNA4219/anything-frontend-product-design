# 情報の開示・密度・検証報告

任意タスク、条件付きの情報、不明値を扱うときは、[判断情報の条件](decision-information.md)も適用する。情報の必要性をpriorityだけで判定せず、原典の助言と本Skillの契約を分ける。

[入出力契約](plan-contract.md)を使い、A01〜A07で定めた目標・機能・画面・経路を点検する。
primary/secondaryは情報を必要とする場面との関係で決める。画面の見た目を均一にするための値として使わない。
部品の展開動作、フォーカス、読み上げ、保存等の状態はB/Cへ渡す。既存Art Directionの配色・書体・構図を本資料で置き換えない。

## A08 判断必須情報を隠さず、補足を段階的に開示する

### Trigger

折りたたみ、詳細ページ、別タブ、ウィザード、hover表示、初期表示の削減を提案するとき。提供する作業のtargetを決めた後は、優先度にかかわらず必ず点検する。

### Inputs

- 各goalのneeded_informationと、target画面で行う判断。
- 情報の実例、条件による必要性、利用頻度、役割・権限。
- secondaryへ移したい理由と、その情報へ到達する手段。

### Decision Rules

- その画面での判断・達成に必要な情報はprimaryにする。クリック・展開・hover・別画面への移動なしで参照できることを求める。
- primaryはスクロールを許容する。全情報が常に最初の表示範囲へ収まることや、固定表示を意味しない。
- 補足であり、その判断に使わなくても達成できる情報だけをsecondary候補にする。
- 低頻度の情報でも、必要な場面では判断必須ならその場面のtargetでprimaryにする。
- 後の作業で初めて必要な情報を後の段階へ置くことと、任意の補足を隠すことを区別する。
- 機能が存在すると気づくための入口を隠す案は、情報量削減と別に発見可能性を検討する。hoverすれば分かると仮定しない。

### Procedure

1. 各target画面について「必要情報ID／判断との関係／現在のvisibility／参照に必要な操作」を作業表にする。
2. goalのneeded_informationを表へ突き合わせ、欠落またはsecondaryのものを特定する。
3. 必須情報が別画面にしかない場合は、その場へ提示するか、比較等を担当する適切なtargetを作り、経路も更新する。
4. secondary候補ごとに、その情報を読まずに判断できる具体例を検討する。判断が変わりうるならprimaryへ戻す。
5. 補足への入口に内容が分かるラベルを提案する。展開UIの挙動・キーボード操作等はB/Cへ引き渡す。
6. 初期／二次の区分が多段化した場合、役割・判断・分類を再点検する。段数を固定上限へ合わせるために必要情報を削らない。
7. A06で宣言した全goal_routesの経路を再確認し、A09でprimaryに残す情報の構造を整理する。

### Output Contract

`screens.information`に`id/visibility/reason`を記録し、visibilityはprimaryまたはsecondaryを使う。
宣言したgoal_routesのtargetは、must/should/couldにかかわらず、そのgoalのneeded_informationをprimaryとして提供する。別targetで必要な情報まで全画面へ複製する必要はない。
根拠不明の必要性はdecision_notesに仮説として書く。必要情報の入手・権限が未解決なら、影響・取得先・担当をunresolvedへ記す。必須達成を妨げる場合にblockingにし、別の確認済み候補で判断を進められる場合はその範囲を明記する。

### Failure Modes

見た目が込み合うという理由で期限・互換性・比較属性を折りたたむ。スクロールするprimaryを「隠れている」と誤判定する。
補足の区分を利用者の熟練度だけで決める。機能の入口まで消してから「探せば使える」と判断する。

### Verification

宣言した各goal_routeについてtargetの情報ID集合とgoalのneeded_informationを照合し、優先度にかかわらず必要なすべてがprimaryであることを確認する。作業自体を明示的に延期した任意goalには経路を一律要求しない。
次に実際の参照条件を確認する。属性だけprimaryでも展開操作が必要なら契約と実装が不一致。実装を見ていない場合は構造上の確認までと報告する。

### Sources

- S16 [Nielsen, Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/)：初期／二次の切分けと、重要度による開示・手順による段階化の区別。専門家の助言。
- S19 [Baymard, Comparison features](https://baymard.com/research-articles/provide-comparison-features)：比較機能の入口をhover時のみから常時表示へ変更した推奨の経緯を報告。
- S20 [Baymard, Product listing information](https://baymard.com/research-articles/product-listing-information)：一覧情報の欠落による見落としと往復を観察。

### Confidence / Limits

needed_informationをtargetのprimaryに要求するのは本Skillの契約上の導出で、論文に同じJSON規則があるわけではない。
「補足」の判定は実タスクで変わる。利用者・業務の確認なしに最適な開示を断定しない。Nielsen記事の段数助言を普遍的上限に変換しない。

## A09 密度を要素数ではなく判断材料で評価する

### Trigger

「情報が多い」「カードを減らす」「余白を増やす」「シンプルにする」という依頼、一覧・比較表・ダッシュボードの情報選定を行うとき。

### Inputs

画面のpurpose、必要な判断、候補集合、needed_information、カテゴリ固有の判断条件、実データ量、制約、visual_intent。
情報を削る理由が混雑感だけか、判断を妨げる具体的な事実があるかを確認する。

### Decision Rules

- 同じ判断に要る比較材料を減らして成立する「簡潔さ」を、改善とみなさない。
- 情報を「判断必須／判断補助／別の判断で必要／根拠不明」に分ける。要素数の目標値を先に置かない。
- 共通属性だけでなく、今回の対象や条件に固有の判断材料を残す。
- 比較対象を揃える、同じ意味の情報を揃える、無関係な重複を避ける等、情報の関係から整理する。
- 情報が多い場合は目的別のまとまり、一覧と比較の役割分担、スクロール可能なprimary等を検討する。見えないところへ移すことだけを解決にしない。
- 色・書体・装飾の変更で情報不足を補ったことにしない。見せ方の実装はCへ渡す。

### Procedure

1. 画面の判断を一つ書き、そのために候補を選ぶ・棄却する条件を列挙する。
2. 各条件に必要な情報IDと、入力データの有無を対応させる。値がない場合は捏造せずデータ取得の残件にする。
3. 現在の情報を四区分へ置く。根拠不明は削除候補ではなく確認候補として扱う。
4. 判断必須はprimaryへ残す。補助情報はA08で開示を決め、別の判断で必要な情報はそのtargetへ配置する。
5. 同時比較が必要なら候補と属性の対応を保つ。表・一覧等の情報関係は提案できるが、部品の外観や挙動をAで実装しない。
6. 省略する情報は、どの目標・要件にも必要でない根拠を書く。既存機能の提供を変えるならA03・A04へ戻る。
7. 実データと端末で未確認なら、収まり・読み取りやすさ・処理時間について未検証と記録する。

### Output Contract

`screens.information`のreasonに、その情報が支える判断を記録する。
decision_notesに「A09: 画面ID、残した判断材料、補足へ移した情報、移動先または理由、未確認条件」を記録する。
実データ不足はproduct、情報構造はA、表現・部品の問題はC担当のunresolvedにする。新しい密度スコアや件数制限を契約へ追加しない。

### Failure Modes

カードを少なくしただけで比較性能が上がったと報告する。業界固有の決定的属性を共通テンプレートにないから落とす。
同じ対象の別名・重複と、別候補・別属性を同じ冗長性として扱う。商品一覧の属性を別業務へそのまま必須化する。

### Verification

「この情報だけで候補を選べる／棄却できるか」を具体例で点検する。必要なら比較対象を並べ、属性対応が失われていないか確認する。
これは机上の照合であり、実ユーザーの正答率・作業時間の測定とは区別する。要素数の減少だけを合格根拠にしない。

### Sources

- S20 [Baymard, Product listing information](https://baymard.com/research-articles/product-listing-information)：共通属性とカテゴリ固有属性を分け、必要情報の欠落を扱う本人研究。
- S19 [Baymard, Comparison features](https://baymard.com/research-articles/provide-comparison-features)：多数の属性を比較する場面。商品探索の文脈に限定して読む。
- S12 [Lewis / Rieman, Chapter 2](https://hcibib.org/tcuid/chap-2.html)：抽象的な見た目の議論を具体的タスクで検討する方法論。

### Confidence / Limits

四区分と出力形式は本Skillの導出で、密度を測る標準尺度ではない。情報が多いことも少ないことも単独では良否を決めない。
対象・条件・データが異なる場合は必要属性を調べ直す。Baymardの記事中の属性数や実装比率を普遍的な上限・成功率として使わない。

## A10 検査できた範囲だけを報告する

### Trigger

planの引渡し、レビュー、修正後の報告、構造チェックの実行後。「完了」「検証済み」「使いやすい」等を述べる前。

### Inputs

入力brief、出力plan、実際に実行したコマンドと結果、実際に読んだ資料、実施した机上確認・ユーザー確認の記録、残件。
実行記録や観測がなければ「未実施」とする。予定した確認を実施済みにしない。

### Decision Rules

- 入力整合、構造的参照、意味上の充足、実ユーザーの達成、実装、視覚結果を別の検証範囲として扱う。
- スクリプトのPASSは、その検査で構造的違反を検出しなかったという意味に限定する。業務適合やラベル理解を証明しない。
- blocking=trueの残件があればHOLDとして扱う。検査結果と残件の食い違いは隠さず記録する。
- 手動確認しか行っていなければ実行PASSを名乗らない。コマンドの終了コードだけから、出力にない結果を創作しない。
- visual_intent_idの一致は参照先の維持を示すだけで、実装の見た目が維持された証拠にはならない。
- 出典に基づく主張、著者の助言、本Skillの導出、今回の実測を区別する。

### Procedure

1. 今回確認した範囲を「入力／参照構造／機能充足／経路・情報／利用者／実装・視覚」に分け、実施・未実施・保留を記す。
2. 入力featureの一意性、正本、参照ID、必須条件、role別経路、targetのprimary情報を確認する。
3. 自動検査が必要で実行環境がある場合だけ、契約のコマンドを実行し、対象ファイルと実際の結果を保存・参照する。
4. 結果が構造上PASSでも、ラベル・業務適合・実データ・端末・権限実装の未検証を残す。
5. 未解決を契約の形式へ整理する。A外の状態はB、部品・実装上の表現はC、業務上の必須性や許可はproductへ渡す。
6. blocking残件がある場合は何が決まれば進めるかを書く。任意の改善案と必須達成を阻む事項を混ぜない。
7. 最終報告では変更内容、採用理由、確認した範囲、未確認・HOLDを具体的に述べる。機能数や画面数だけを成果にしない。

### Output Contract

- planのトップレベルは契約に定義された項目を使い、verification等の独自キーを追加しない。
- 実施範囲と未実施事項はdecision_notesへ、解消が必要な問いはunresolvedへ記録する。
- unresolvedには`id/category/owner/impact/blocking/question`を揃える。
- 自動検査を実行するときは次を用いる。結果ファイルの生成・内容を観測してから報告する。

~~~bash
python3 checks/validate_plan.py --brief brief.json --plan plan.json --output result.json
~~~

exit 0/1/2の意味は契約どおりに読む。返された状態と残件を記録し、未実施をPASSへ変換しない。
このコマンドの記載は実行済みの証拠ではない。

### Failure Modes

JSONが読めるだけで設計全体を検証済みとする。機械的到達性を、利用者が迷わず発見できることと同一視する。
資料の推奨を今回の利用者試験結果として書く。B/Cへ残した実装課題を解決済みとする。問題を見つけなかったことを問題がない証拠にする。

### Verification

報告の各「確認した」「実行した」「改善した」に対応する記録・観測を指せるか点検する。指せない文は未検証・提案へ書き直す。
全blocking残件を読み、最終状態がHOLDと整合するか確認する。ユーザー検証未実施を明記しても、実施済みの構造確認は正確に報告する。

### Sources

- S01 [NASA Requirements Management](https://www.nasa.gov/reference/6-2-requirements-management/)：要求の追跡・変更管理の原典。検査スクリプトの効力を保証する資料ではない。
- S03 [18F Design hypothesis](https://guides.18f.org/methods/decide/design-hypothesis/)：仮説として扱うための保存版資料。
- S04 [18F Make research actionable](https://guides.18f.org/ux-guide/research/make-research-actionable/)：研究と判断の接続を扱う保存版資料。
- S12 [Lewis / Rieman, Chapter 2](https://hcibib.org/tcuid/chap-2.html)：代表例を満たしても他のタスクを検討する責任は残るという方法論。

### Confidence / Limits

検証範囲を分けて記録する規則は、本Skillと契約の導出であり、外部規格の適合証明ではない。18F資料は現行政府方針として扱わない。
構造検査が成功しても本Skillの効果は未実証。実ユーザーの作業、実装、表示を観測していない範囲は未検証のまま引き渡す。
