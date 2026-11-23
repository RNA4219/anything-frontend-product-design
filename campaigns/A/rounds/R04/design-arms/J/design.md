# 設備カタログの分類再編レビューと修正設計

## 1. 結論と成立範囲

**inventory-r17の96件を正本として保持し、用途・材質・保全の軸を分離する。採用するデータ変更は、task.heatの名称を「加熱」へ変更することと、空のlegacy.unusedを整理することだけとする。**

CH01・CH02・CH06は修正、CH03の材質確定は6件に限って保留、CH04・CH05は採用する。提案にある96件という件数だけでは同一性を満たさない。ITEM-073の欠落／ITEM-X73の追加、ITEM-088の拠点変更、ITEM-090のrole拡張も修正する。これらは変更一覧外の差分である。根拠は資料S1–S3、全件照合結果はreview.jsonのF01–F07とE01–E06に記録した。

成果は情報構造の設計、入力全件に対する集合・属性の照合、静的HTMLの抜粋である。実転送、移行先への登録、認可、絞込操作、実描画、利用者の探索成功は実施していない。**構造と入力値の照合済み・表示／操作／効果は未確認**とする。

## 2. 判断の資料と方法

| 記号 | 資料と版 | 今回使った範囲 |
|---|---|---|
| S1 | source-inventory.json — inventory-r17 | 現行の96件・9概念・2入口。全ID、全フィールド、所属の正本 |
| S2 | proposed-inventory.json — inventory-r18-proposed、basis_revision=inventory-r17 | 差分とCH01–CH06の主張。rationaleは承認や観測の証拠にしない |
| S3 | requirements.json — 版番号なし、case_id=R04-equipment-reclassification、current_source_revision=inventory-r17 | 必須保存条件、承認済み2変更、責務境界、visual_intent |
| S4 | output-contract.json／task.md — ともに版番号なし、提供された固定課題 | review.json・design.md・preview.htmlの出力と確認範囲 |
| M1 | SKILL.md — Product Design / Information Architecture、提供版・版番号なし | 正本、目標・要件、画面責務、限定した検証報告 |
| M2 | goals-and-features.md／feature-context.md — 提供版・版番号なし | 同名で統合しない、成果と利用条件を照合する、限定変更の承認根拠 |
| M3 | information-architecture.md／navigation-evidence.md — 提供版・版番号なし | 対象・属性・分類と入口の分離、旧入口の対象・role・scope・必要条件 |
| M4 | decision-information.md／disclosure-and-verification.md — 提供版・版番号なし | 未知値の保持、必要情報の同時参照、意味・構造・描画・利用者効果の区別 |

方法文書の原典リンクにはアクセスしていない。今回の採否はS1–S3の具体値を基準とし、方法の助言をこのカタログでの実測結果へ置き換えない。S4を優先して成果を作成し、一般的なbrief.json／plan.jsonは作成せず、その形式用のvalidate_plan.pyも実行していない。代わりに本課題の契約とinventoryに対応する自己確認を行った。入力ファイルのハッシュはverification.jsonに記録した。

## 3. 利用者の判断と、残す情報

| 対象roleと場面 | 達成する判断 | 保持する条件・機能 | 完了を確かめる材料 |
|---|---|---|---|
| staff／inventory_managerが設備を探す | 用途と材質から候補を区別する | 同じ正本集合への用途・材質フィルタ。各recordのroles・scopeを維持 | 設備ID・名称・用途・材質の対応。未知状態を明記 |
| staffが旧測定入口を使う | 従来の測定設備へ辿る | entry.measure、staff、all-sites、task.measureを保持 | r17の測定24 IDとの集合一致 |
| staffが加熱入口を使う | 加熱に用いる同じ設備へ辿る | entry.heat、staff、all-sites、task.heatを保持 | 同じ24 IDと、名称だけの変更 |
| 保全情報も確認する利用者 | 用途としての検査と保全の検査状態を取り違えない | task.inspectとmaintenance.inspectを別の軸・列・条件として保持 | 同じ設備に両タグがあることも見分けられる |
| inventory_manager等の確認担当 | 材質未確認設備をID単位で照会する | 未確認6件を正本に残し、照会対象を固定 | 対象ID、用途、site、roles、確認待ちという状態 |

入力にない予約・貸出・編集・送信等は追加しない。役割の継承関係も推測しない。inventory_managerが全96件に含まれるのはS1のroles配列を数えた結果であり、管理者という呼称から推測した権限ではない。確認担当の割当は提案であり、実担当が決定済みという記録ではない。

## 4. 修正後の対象・分類・所属

### 4.1 正本と属性

対象の正本は各record.id。名称が似ていても別IDを同一設備とみなさない。複数ビューに現れる同じITEM-IDは同じ正本を参照する。record.labelは全96件ともS1のまま。siteに対応する入力フィールドはscopeであり、rolesとともにID別に保持する。

concept.idは概念の安定した識別子、labelは表示名、axisは判断軸、record.concept_idsは所属として別々に扱う。名称変更、所属変更、概念統合、設備ID変更を一つの「整理」にまとめない。sourceには階層関係の定義がないため、新しい親子関係を確定済み事実として追加しない。

### 4.2 概念表

| 表示する判断軸 | 概念ID | 修正後ラベル | 所属件数（全96件内） | 扱い |
|---|---|---|---:|---|
| 用途 | task.measure | 測定 | 24 | 元のID・所属を保持 |
| 用途 | task.cut | 切断 | 24 | 元のID・所属を保持 |
| 用途 | task.heat | 加熱 | 24 | 元ラベル「温熱処理」から名称のみ変更 |
| 用途 | task.inspect | 検査 | 24 | 元のID・所属を保持 |
| 保全の検査状態 | maintenance.inspect | 検査 | 12 | 用途の検査と別列・別条件。詳細状態は未定義 |
| 材質 | material.metal | 金属 | 45 | 元のID・所属を保持 |
| 材質 | material.wood | 木材 | 45 | 元のID・所属を保持 |
| 材質 | material.unspecified | 材質未確認 | 6 | 確認状態を保持。木材／金属とはみなさない |

legacy.unusedはS1の全設備と全入口で参照が0件、S3に明示承認があるため廃止する。task.workによる所属置換は採用せず、修正概念表は8概念となる。材質の「未確認」は材質が木材・金属だと分かった状態ではなく、未確認という入力状態を維持する選択肢である。

### 4.3 所属を再構成する規則

1. S1のrevisionがinventory-r17であり、S3のcurrent_source_revisionと一致することを先に確認する。違えばこの差分手順を新しい母集団へそのまま適用しない。
2. S1の96レコードを、id・label・scope・roles・concept_idsを含む全フィールドごと複製した作業データから開始する。S2のtask.workから測定／切断を逆推定しない。
3. conceptsのtask.heat.labelだけを「加熱」にする。ID、axis、所属は変更しない。
4. legacy.unusedに所属するrecordとentryが0件であることを再確認して、その概念定義のみ除く。
5. entriesはS1の2件を全フィールド保持する。設備データの追加・削除、role・scope変更、材質確定、保全タグの除去は行わない。

この規則で、96件のID集合・各設備のすべての所属・scope・rolesをS1どおりに復元できる。今回の自己確認はこのモデルを作業メモリ上で構成して照合した。移行用データファイルやDBへ適用済みという意味ではない。

### 4.4 CH別の決定

| 変更ID | 決定 | 理由と必要な修正 |
|---|---|---|
| CH01 | revise | F01。broaderへの集約は測定・切断の同一概念化を許可しない。task.measure/task.cutと48件の元所属を保持し、task.workによる所属置換を撤回する。 |
| CH02 | revise | F02。表示名が同じでもaxisと判断目的が異なる。task.inspectとmaintenance.inspectを別概念として保持し、後者の12件の所属を復元する。 |
| CH03 | hold | F03。木材への確定変更は6件の個別確認まで保留する。修正案ではmaterial.unspecifiedを保持できるため、確認済み90件や他の分類修正は進める。未知状態を保持した移行まで停止する意味ではない。 |
| CH04 | keep | requirements.json（版番号なし、case_id=R04-equipment-reclassification） approved_changes[0]に名称変更の承認がある。task.heatの概念ID・axis=task、所属集合24件、entry.heatのID/path/role/scope/concept_idsはsourceと提案で一致し、ラベルだけが温熱処理から加熱へ変わる。ITEM-015/075の材質変更はCH03の問題として別に戻す。提案の自己評価を承認根拠にしない。 |
| CH05 | keep | requirements.json（版番号なし、case_id=R04-equipment-reclassification） approved_changes[1]に整理の承認がある。sourceの全96件と全2入口を照合し、legacy.unusedへの所属・参照がいずれも0件であるため、当該空概念の廃止を採用する。外部参照や利用ログの非利用を観測したという意味ではない。 |
| CH06 | revise | F04。旧URLを開けるという提案記述だけでは用途条件の保持を満たさない。entry.measureのstaff/all-sites/task.measureを維持した着地を設計し、r17の24正本ID集合と照合する。 |

### 4.5 変更一覧外の差分

| 対象ID | S1の値 | S2の値 | 修正 |
|---|---|---|---|
| ITEM-073／ITEM-X73 | ITEM-073、設備 073、site-A、staff/inventory_manager、task.measure＋material.wood | ITEM-073なし。ITEM-X73、設備 073（取込複製）、site-A、staff/inventory_manager、task.work＋material.wood | S1のITEM-073を全フィールドで採用し、ITEM-X73を修正96件へ含めない。両者を検証済み同一設備や別名としない |
| ITEM-088 | scope=site-B | scope=site-A | site-Bへ戻す。保全タグは別途F02の規則で保持 |
| ITEM-090 | roles=[inventory_manager] | roles=[staff, inventory_manager] | managerのみへ戻す。用途=切断、材質未確認も保持 |

件数一致、一意ID数一致、参照切れなしでもこの3種類の不一致は残り得るため、総数の検査だけで移行を承認しない。（根拠：S1/S2の全件差分、S3 must_preserve[0]・[2]）

## 5. 探索先・フィルタ・旧入口の対応

### 5.1 画面責務と必要情報

一つの論理一覧で、候補設備を用途と材質で比較する。別の用途ビューは同じ正本の絞込結果とし、設備を複製管理しない。比較行には設備ID、名称、用途、材質（未確認を含む）、保全の検査状態、siteを並べる。role条件は一覧の対象範囲として示し、認可の説明と実装を混同しない。静的見本ではレビュー用に元rolesも列で示す。

用途と保全の「検査」は見出し付きで分離する。保全タグがある行は「検査」、ない行は「登録なし（状態の判定なし）」とし、後者を未検査・検査済み・正常とは言い換えない。説明を開かないと材質未確認が分からない構造にしない。補足説明や移行の詳細だけを別節に置く。（方法M3/M4、値S1）

### 5.2 フィルタの条件

- 用途の選択肢：測定、切断、加熱、検査。比較する概念IDはそれぞれtask.measure、task.cut、task.heat、task.inspect。
- 材質の選択肢：金属、木材、材質未確認。確定材質を選んだときは未確認6件を一致に数えない。「材質条件なし」では未知の設備も、他の有効条件に従って残す。
- 保全は独立した条件とし、maintenance.inspectへの所属で絞る。用途の検査を自動選択しない。現データで全12件が用途検査にも属することから、両概念の意味上の同一性を導かない。
- 条件間はANDで照合する。roleは対象record.rolesへの包含、scopeは同一siteへの一致、all-sitesは入力内の全siteを対象とする。これは入力を検査するための論理条件で、認可実装の成立は別途確認する。
- フィルタを解除してもrecordの所属・scope・rolesを書き換えない。現在条件とその対象範囲を一覧の上に残す。操作時の更新・復帰・0件表示はB/Cへの引継ぎ事項とする。

複数選択・OR条件・ソート・検索索引の実装はこの静的見本に含めていない。

### 5.3 実在する入口の保存

| 入口ID | 既存path | role | scope | 着地で有効にする用途条件 | S1／修正案の対象 |
|---|---|---|---|---|---|
| entry.measure | /tools/measurement | staff | all-sites | task.measure（測定） | 同じ24 ID。材質未確認のITEM-045も条件なしでは含む |
| entry.heat | /tools/heat | staff | all-sites | task.heat（加熱） | 同じ24 ID。ITEM-015/075は材質未確認のまま含む |

旧入口はIDとpathを保持して、同じカタログの対応する用途ビューへ着く設計にする。転送が必要か、同じpathでビューを描画するかは未決の実装方式である。どちらでも、初期用途条件・staff・all-sites・対象の正本IDを満たすことを受入条件にする。

提案の測定入口では用途条件が空であり、論理対象は24件から88件へ変わる。共通する期待IDは23件で、65件が期待外、ITEM-073が欠落する。修正案では24件のID集合まで一致させる。表示成功という主張だけでは検査を代替しない。（S1/S2 entriesとrecords、E06）

入力に記載された既存入口は上の2件だけ。その他の旧メニュー・外部参照が存在しないと断定しない。inventory_manager向けURLも入力にないため、静的見本の管理側例はURL実装や既存入口の観測を表さない。新たな公開URLを創作せず、実装時の入口確認へ引き継ぐ。

### 5.4 role別の対象件数

次は全96件を入力条件で集計した値で、画面表示や認可の実測値ではない。軸どうしの件数は重なるため、縦方向に合計しない。

| 条件 | 全96件内 | staff | inventory_manager |
|---|---:|---:|---:|
| 測定 (task.measure) | 24 | 24 | 24 |
| 切断 (task.cut) | 24 | 19 | 24 |
| 加熱 (task.heat) | 24 | 24 | 24 |
| 検査 (task.inspect) | 24 | 20 | 24 |
| 検査 (maintenance.inspect) | 12 | 10 | 12 |
| 金属 (material.metal) | 45 | 39 | 45 |
| 木材 (material.wood) | 45 | 45 | 45 |
| 材質未確認 (material.unspecified) | 6 | 3 | 6 |

全件ではsite-A=48、site-B=48。staffを含む設備は87件、inventory_managerを含む設備は96件。ITEM-088はsite-B、ITEM-090はmanagerのみのまま扱う。（S1、E05/E06）

## 6. 材質未確認6件の照会

| 設備ID | 用途 | site（scope） | 元roles | 保持する所属 |
|---|---|---|---|---|
| ITEM-015 | 加熱 (task.heat) | site-A | staff / inventory_manager | material.unspecified |
| ITEM-030 | 切断 (task.cut) | site-B | inventory_manager | material.unspecified |
| ITEM-045 | 測定 (task.measure) | site-A | staff / inventory_manager | material.unspecified |
| ITEM-060 | 検査 (task.inspect) | site-B | inventory_manager | material.unspecified |
| ITEM-075 | 加熱 (task.heat) | site-A | staff / inventory_manager | material.unspecified |
| ITEM-090 | 切断 (task.cut) | site-B | inventory_manager | material.unspecified |

照会先はinventory_manager／設備データ管理担当を提案する。各IDの実材質と根拠を確認し、回答が得られた設備だけを後続の変更対象とする。確認日時・担当者・回答は未提供のため作成しない。回答前はmaterial.unspecifiedを維持し、木材・金属へ一括補完しない。

この6件の材質確定だけが保留である。未知状態を正しく表示して用途で探す設計や、確定済み90件の分類・探索、CH04/CH05を一律に停止しない。review.jsonのU-MATERIAL.blocking=falseは、未知状態を保持した今回の設計を完成できるという意味であり、材質を確定済みにする許可ではない。

## 7. 移行前照合と受入手順

以下は実装担当に渡す手順。今回実行した入力・メモリモデルの検査と、今後の移行先・実環境で必要な検査を分ける。

1. **入力固定**：source revision、requirementsのrevision、proposalのbasis_revisionを照合する。入力が更新された場合は差分を取り直す。今回3値はinventory-r17で一致した。
2. **ID集合**：移行対象を96件・96一意IDとし、sourceとの不足集合・余分集合がともに空であることを確認する。ITEM-073があり、ITEM-X73がないことを個別に確認する。件数だけで通さない。
3. **全フィールド**：IDをキーに、label、scope、rolesの集合、concept_idsの集合をsourceと全件照合する。許容するrecord差分は0件。ITEM-088のsite-BとITEM-090のmanagerのみを境界例として確認する。
4. **概念と所属**：task.heatの表示名以外のlabel/axisは維持。legacy.unusedのみ廃止。task.measure/cut/heat/inspectは各24件、maintenance.inspectは12件、金属45・木材45・未確認6の各ID集合を照合する。件数に加えて集合の一致が必要。
5. **参照整合**：records・entriesのconcept_idsがすべて残存概念を参照すること、旧概念から未知の代替IDへ勝手に正本化されていないことを確認する。IDの重複・未定義参照は0を条件にする。
6. **入口の全フィールド**：既存2入口のID/path/role/scope/concept_idsをsourceと照合する。旧測定入口はtask.measureを保持して同じ24 ID、加熱入口も同じ24 IDを返す論理条件にする。
7. **境界の確認**：測定＋木材ではITEM-073を含み、測定＋材質未確認ではITEM-045を含む。材質未確認6件は金属／木材の集合に含めない。staffではITEM-030/060/090を含めず、managerでは含む。保全の登録12件を用途検査24件と区別する。
8. **移行先の照合**：実際の移行ファイルまたはDBの出力について2–7を再実行し、結果と差分を残す。今回この移行先は作成・照合していない。違反が残る提案全体をそのまま切り替えず、正本保持の修正を先に反映する。
9. **実環境の入口・認可・操作**：B/Cが既存pathを開き、初期条件、結果ID、role/scope境界、条件変更・解除・復帰を確認する。総合一覧が開くだけの挙動は測定入口の合格にしない。未実施。
10. **表示・利用者課題**：Cが画面サイズ、キーボード、支援技術で必要情報の参照を確認し、Dが既知IDの探索と用途×材質の候補比較を別の課題で観察する。成功・誤り・時間を別々に記録する。未実施。

現行稼働データや本番環境にはアクセスしていないため、ロールバック実施や切替完了も主張しない。資料S1/S2の入力、作業メモリの設計モデル、今後の移行先は異なる検査対象として扱う。

## 8. 静的サンプルの範囲

preview.htmlは標準HTMLの情報構造見本であり、visual_intent.id=equipment-admin-existingを判断の前提とする。配色・ブランド・書体・画面レイアウトの再設計は提案していない。デザイン資産が未提供なので、既存画面の外観を再現・保持できたという判定もしない。

見本にはstaffのカタログ例10件、旧測定入口の着地例3件、加熱入口の着地例3件、inventory_managerの材質未確認例3件を表示する。重複する正本参照を除いた設備数は13件である。全96件の画面実装でも完全移行でもない。役割別の節は比較用の静的例で、実認可やrole切替を実装したものではない。

用途・材質・保全条件を別のfieldset／labelで示し、条件欄は固定サンプルとしてdisabledにする。実際の絞込処理はない。ページ内リンクは対応節を示すアンカーで、既存URLへのHTTP転送を実装していない。

## 9. 確認結果と残件

| 確認層 | 実行した内容 | 結果の限界 |
|---|---|---|
| 入力・意味の照合 | 4 JSONの読込、revision、全ID、全属性、所属集合、入口条件と要件の照合 | 固定合成データ内の整合。実設備・承認台帳・利用ログは未確認 |
| 設計モデル | sourceから2件の承認済み変更だけを適用したメモリモデルを全96件で照合 | データ移行・登録ではない |
| 成果物の自己確認 | JSON契約の必須キー、6変更の採否、対象ID参照、HTML内のID・アンカー・全サンプル値を解析 | 自作チェック。独立評価や一般plan用checkerの実行ではない |
| 表示・操作・認可 | 未実施 | HTML構造から実描画・操作・安全な認可を保証しない |
| 人の効果 | 未実施 | 探索時間短縮、誤り減少、ラベル理解を実証していない |

残件はU-MATERIAL（6件の材質）、U-MAINTENANCE-MEANING（保全ラベルの詳細）、U-IMPLEMENTATION（移行と入口・認可）、U-RENDER-AND-USE（表示と利用者）に分けた。Aの情報構造で確定できる修正は完成させ、未提供の事実を作らず担当区分へ引き継ぐ。

確認の再実行は、build_deliverables.pyへこの課題の共通入力フォルダを1引数として渡す。出力先はスクリプトと同じフォルダに限定する。このスクリプトは入力を読取り、成果物とverification.jsonを作成するだけで、外部通信や移行先への書込をしない。

## 付録：用途と保全の正本所属集合

全96件を用途ごとに1回ずつ列挙した。保全の12件は同じ正本の別軸への所属なので、ここで設備を追加したものではない。材質6件は第6節、材質を含むすべてのrecord値の正本はS1に固定する。

| 概念ID | 件数 | 正本ID集合 |
|---|---:|---|
| task.measure | 24 | ITEM-001、ITEM-005、ITEM-009、ITEM-013、ITEM-017、ITEM-021、ITEM-025、ITEM-029、ITEM-033、ITEM-037、ITEM-041、ITEM-045、ITEM-049、ITEM-053、ITEM-057、ITEM-061、ITEM-065、ITEM-069、ITEM-073、ITEM-077、ITEM-081、ITEM-085、ITEM-089、ITEM-093 |
| task.cut | 24 | ITEM-002、ITEM-006、ITEM-010、ITEM-014、ITEM-018、ITEM-022、ITEM-026、ITEM-030、ITEM-034、ITEM-038、ITEM-042、ITEM-046、ITEM-050、ITEM-054、ITEM-058、ITEM-062、ITEM-066、ITEM-070、ITEM-074、ITEM-078、ITEM-082、ITEM-086、ITEM-090、ITEM-094 |
| task.heat | 24 | ITEM-003、ITEM-007、ITEM-011、ITEM-015、ITEM-019、ITEM-023、ITEM-027、ITEM-031、ITEM-035、ITEM-039、ITEM-043、ITEM-047、ITEM-051、ITEM-055、ITEM-059、ITEM-063、ITEM-067、ITEM-071、ITEM-075、ITEM-079、ITEM-083、ITEM-087、ITEM-091、ITEM-095 |
| task.inspect | 24 | ITEM-004、ITEM-008、ITEM-012、ITEM-016、ITEM-020、ITEM-024、ITEM-028、ITEM-032、ITEM-036、ITEM-040、ITEM-044、ITEM-048、ITEM-052、ITEM-056、ITEM-060、ITEM-064、ITEM-068、ITEM-072、ITEM-076、ITEM-080、ITEM-084、ITEM-088、ITEM-092、ITEM-096 |
| maintenance.inspect | 12 | ITEM-008、ITEM-016、ITEM-024、ITEM-032、ITEM-040、ITEM-048、ITEM-056、ITEM-064、ITEM-072、ITEM-080、ITEM-088、ITEM-096 |
