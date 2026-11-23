# 設備カタログ分類再編：修正後の情報設計

## 結論と適用範囲

**名称変更CH04と空カテゴリ整理CH05を採用し、CH01・CH02・CH06を修正する。CH03の材質確定だけを6件に限定して保留する。** 修正案の設備正本はinventory-r17の96件である。提案の96件という総数の一致から、同一性保持は結論できない。ITEM-073の欠落とITEM-X73の追加、ITEM-088のscope変更、ITEM-090のroles拡張も戻す。[D1–D3]

状態は「取得済み合成データの構造照合・意味レビュー済み、実装・描画・利用者効果は未確認」。材質確定に関する部分HOLDはU01に限定する。未知のまま6件を保持する設計と、他90件の確定済み材質による探索は進められる。全設備を一律停止する判断ではない。

成果物はreview.json、design.md、preview.html。静的HTMLは13個の異なる設備IDを使う表示抜粋であり、全96件の画面実装や移行結果ではない。補助記録はcomparison.jsonとverification.json、再生成用コードはbuild_artifacts.pyに置いた。[D4]

## 1. 判断の入力と維持する条件

| 項目 | 固定した内容 |
|---|---|
| 正本snapshot | source-inventory.json、revision=inventory-r17、case_id=R04-equipment-reclassification |
| レビュー対象 | proposed-inventory.json、revision=inventory-r18-proposed、basis_revision=inventory-r17 |
| 同一性 | ITEM-001〜ITEM-096の96件。設備ID・名称・scope・roles・所属を保持 |
| 用途 | 測定、切断、加熱、検査を個別に絞れること |
| 材質 | 金属、木材、材質未確認を区別。未知を既知値へ補完しない |
| 保全 | maintenance.inspectは用途task.inspectと独立した軸 |
| 入口 | 提供された実在入口はentry.measureとentry.heatの2件だけ |
| 視覚意図 | equipment-admin-existingを維持。資産未提供のため標準HTMLで構造を示す |

この資料のsiteはレコードのscopeフィールドを指す。入口のall-sitesと、個々の設備のsite-A/site-Bを同一の値として扱わない。集合計算でのall-sitesは、提供された96件の範囲に含まれるsite-Aとsite-Bの和集合とした。未提供の拠点・権限仕様は推定しない。[D1–D3]

| 役割と目標 | 完了条件 | 必要な情報・設計機能 |
|---|---|---|
| staff：用途と材質で設備を選ぶ | staffをrolesに持つ設備から用途条件と材質条件に合うIDを識別できる | 設備ID・名称・用途・材質・siteを一覧で同時参照。用途と材質の独立した絞込 |
| staff：旧測定入口から測定設備を探す | entry.measureの同一role/scopeと用途条件で元の24件を保持 | 入口で用途=測定を引継ぎ、選択中条件と結果範囲を一覧に明示 |
| inventory_manager：未確認設備を照会する | 未確認6件の正本ID、既存用途、site、rolesを特定し、材質の根拠を記録できる | 未確認だけの論理ビューと照会一覧。照会窓口としての役割付与は設計上の提案で、実担当者・送信経路は未指定 |

予約、操作可能性、安全適合、検査合否を判断する機能は入力にない。材質ラベルが確定していることだけから設備全体の利用適合を宣言しない。

## 2. 変更の採否と根拠

| 変更 | 採否 | 理由・修正 |
|---|---|---|
| CH01 | revise | 測定と切断の用途区別が必須であり、broaderへの全所属置換を採用しない。task.measure/task.cutとsourceの48件の所属を保持する。F02。 |
| CH02 | revise | requirementsの別軸要件とsourceのaxisが根拠。表示名の一致や提案のexact宣言では同義と認定しない。maintenance.inspectと12件の所属を用途と独立に保持する。F03。 |
| CH03 | hold | 木材への確定変換を裏付ける値がない。6件はmaterial.unspecifiedのまま保持し、個別材質の確定だけU01で保留する。他90件の分類・探索は進める。F04。 |
| CH04 | keep | requirements.jsonのapproved_changes[0]で名称変更を明示承認。task.heatのID・axis・用途所属24件・entry.heatの条件はsourceと一致する。採用対象は温熱処理から加熱へのlabel変更のみ。ITEM-015/075の材質変更はCH03として戻す。 |
| CH05 | keep | requirements.jsonのapproved_changes[1]で整理を明示承認。inventory-r17の96件中legacy.unused所属0件、提供された2入口の参照0件、宣言された親参照も0件を照合したため空概念を削除できる。未提供の外部システム全体を調査済みとはしない。 |
| CH06 | revise | requirementsの旧測定入口条件保持を優先。entry.measureのstaff/all-sitesとtask.measure条件を併せて保持する。総合一覧が開くという提案の自己評価を移行成功の根拠にしない。F05。 |

変更一覧外の修正は次の3点。[D1–D3、review.json F01/F06/F07]

| 対象ID | 観測した不一致 | 修正後 |
|---|---|---|
| ITEM-073 / ITEM-X73 | 96件を保ったまま正本IDが置換 | ITEM-073（設備 073）を保持。ITEM-X73を修正案の正本へ取り込まない。後継・同一設備と認定しない |
| ITEM-088 | site-B → site-A | scope=site-B、roles=staff/inventory_managerを保持 |
| ITEM-090 | inventory_manager専用にstaffを追加 | roles=[inventory_manager]、scope=site-Bを保持 |

## 3. 修正後の分類・所属

設備を正本IDで一元に扱い、用途・材質・保全を別属性として同じ設備へ付与する。用途別の別設備を複製しない。用途の「検査」と保全の「検査」は、文脈見出しで区別する。task.workへの置換は採用せず、用途の4分類を保持する。[D1、D2、M1–M3]

| 分類軸 | 概念ID | 表示ラベル | 正本96件内の所属数 | 扱い |
|---|---|---|---:|---|
| task | task.measure | 測定 | 24 | sourceのID別所属を保持。 |
| task | task.cut | 切断 | 24 | sourceのID別所属を保持。 |
| task | task.heat | 加熱 | 24 | 名称だけ変更。ID・axis・所属を保持。 |
| task | task.inspect | 検査 | 24 | sourceのID別所属を保持。 |
| maintenance | maintenance.inspect | 検査 | 12 | 用途の検査とは別軸。付与の有無を保持。 |
| material | material.metal | 金属 | 45 | sourceのID別所属を保持。 |
| material | material.wood | 木材 | 45 | sourceのID別所属を保持。 |
| material | material.unspecified | 材質未確認 | 6 | 材質を確定せず個別照会。 |

所属数はroleによる絞込前の値である。用途の合計96、材質の合計96、保全の付与12で、レコード→概念の所属は合計204ペア。概念は8件になる。保全の12件は用途の検査24件と重複するため、設備数へ加算しない。legacy.unusedは現snapshotで所属・入口参照・宣言された親参照がなく、明示承認に従って空概念だけを削除する。[D1–D3、comparison.json、verification.json]

**全件を確定する規則：各IDのlabel・scope・roles・concept_idsをsource-inventory.json（inventory-r17）からそのまま採る。** 概念ラベルのtask.heatだけを「加熱」にし、概念legacy.unusedだけを除く。これが修正モデルの完全な定義であり、表の抜粋だけから残りの設備を推測しない。

用途の復元対象IDは次のとおり。

- task.measure（24件）: ITEM-001、ITEM-005、ITEM-009、ITEM-013、ITEM-017、ITEM-021、ITEM-025、ITEM-029、ITEM-033、ITEM-037、ITEM-041、ITEM-045、ITEM-049、ITEM-053、ITEM-057、ITEM-061、ITEM-065、ITEM-069、ITEM-073、ITEM-077、ITEM-081、ITEM-085、ITEM-089、ITEM-093
- task.cut（24件）: ITEM-002、ITEM-006、ITEM-010、ITEM-014、ITEM-018、ITEM-022、ITEM-026、ITEM-030、ITEM-034、ITEM-038、ITEM-042、ITEM-046、ITEM-050、ITEM-054、ITEM-058、ITEM-062、ITEM-066、ITEM-070、ITEM-074、ITEM-078、ITEM-082、ITEM-086、ITEM-090、ITEM-094
- task.heat（24件）: ITEM-003、ITEM-007、ITEM-011、ITEM-015、ITEM-019、ITEM-023、ITEM-027、ITEM-031、ITEM-035、ITEM-039、ITEM-043、ITEM-047、ITEM-051、ITEM-055、ITEM-059、ITEM-063、ITEM-067、ITEM-071、ITEM-075、ITEM-079、ITEM-083、ITEM-087、ITEM-091、ITEM-095
- task.inspect（24件）: ITEM-004、ITEM-008、ITEM-012、ITEM-016、ITEM-020、ITEM-024、ITEM-028、ITEM-032、ITEM-036、ITEM-040、ITEM-044、ITEM-048、ITEM-052、ITEM-056、ITEM-060、ITEM-064、ITEM-068、ITEM-072、ITEM-076、ITEM-080、ITEM-084、ITEM-088、ITEM-092、ITEM-096

maintenance.inspectを保持する12件：ITEM-008、ITEM-016、ITEM-024、ITEM-032、ITEM-040、ITEM-048、ITEM-056、ITEM-064、ITEM-072、ITEM-080、ITEM-088、ITEM-096。

保全タグ未付与は「このタグの付与なし」とだけ表現する。未検査、検査不要、合格などの意味へ置換しない。保全タグ付与ありも、検査済み・合格などを意味すると決めない。[D1、D2、M4]

## 4. 入口、絞込、判断場所

### 既存入口を維持する対応

| 入口ID / 既存path | role / scope | 初期用途条件 | 修正後に期待する対象 |
|---|---|---|---|
| entry.measure / /tools/measurement | staff / all-sites | task.measure | sourceと同一の測定24件。材質無指定では未確認ITEM-045も含む |
| entry.heat / /tools/heat | staff / all-sites | task.heat | sourceと同一の加熱24件。材質無指定ではITEM-015/075も含む |

旧URLを共通一覧へ接続する実装を採る場合も、入口の用途条件を初期状態として保持する。URLが開くだけ、管理者だけが探せること、無条件検索に表示されることを保持判定の代用にしない。新しい実在URL、旧ブックマーク、外部参照の存在は創作していない。実転送方式はU02の引継ぎ事項。[D1–D3、M2、M3]

### 絞込条件の意味

1. まずレコードrolesに要求roleが含まれる設備を対象にする。site条件は元のscopeから評価する。メニューの表示・非表示だけを認可の実装としない。
2. 用途、材質、保全は独立の条件として扱う。各軸は「指定なし」または単一概念を選ぶ案とし、指定された別軸同士はANDで結ぶ。未指定はタグを書き換える操作ではない。
3. 材質=木材/金属はその確定タグを持つ設備だけを対象とする。材質=未確認はmaterial.unspecifiedのみ。材質指定なしでは、role/scope/用途に合う未確認設備も残す。
4. 入口から渡された用途と、現在の材質・範囲を結果と同じ判断場所に表示する。フィルタの解除・変更操作、その後の履歴・状態は未実装でB/Cへ渡す。
5. 0件はそのrole/scope/絞込条件とsnapshot内の結果である。カタログ全体や実世界で設備が存在しない証拠にしない。

### 同じ一覧で常時参照する情報

一覧のpurposeは「現在のroleとsite範囲で、用途・材質の条件に合う設備IDを識別する」。設備ID、名称、用途、材質の既知/未確認、site、選択中条件を展開不要の情報とする。保全条件を比較する表示では保全タグも同時に示す。理由の詳細や変更履歴は補足へ置けるが、未知の表示は隠さない。[M2–M4]

用途別に正本を複製せず、同じ設備集合への論理ビューとして示す。管理者の未確認照会ビューは提案であり、既設入口・認可済み画面と称さない。preview.htmlの管理者節は、この資料の比較例である。

### 実装前の期待値

以下は全件データの集合計算結果であり、実操作の結果ではない。[verification.json]

| 条件 | 期待する件数・ID |
|---|---|
| staff / all-sites / 測定 / 材質指定なし | 24件、前節のtask.measureのID集合と一致 |
| staff / all-sites / 測定 / 木材 | 23件 |
| staff / all-sites / 測定 / 材質未確認 | 1件：ITEM-045 |
| staff / all-sites / 測定 / 金属 | 0件。このsnapshotと条件に限る |
| staff / all-sites / 加熱 / 木材 | 22件 |
| staff / all-sites / 加熱 / 材質未確認 | 2件：ITEM-015、ITEM-075 |
| inventory_manager / all-sites / 用途指定なし / 材質未確認 | 6件：次節の一覧 |
| staff / all-sites / 用途指定なし / 材質未確認 | 3件：ITEM-015、ITEM-045、ITEM-075。ITEM-030/060/090は含めない |

site/roleの保持照合はstaffが全87件（site-A=48、site-B=39）、inventory_managerが全96件（各site=48）。これらの件数に加えてID集合の一致を確認する。

## 5. 6件に限定した材質確認

| 正本ID | 用途 | site | 許容roles（入力値） | 修正後の材質 |
|---|---|---|---|---|
| ITEM-015 | 加熱 | site-A | staff, inventory_manager | 材質未確認 |
| ITEM-030 | 切断 | site-B | inventory_manager | 材質未確認 |
| ITEM-045 | 測定 | site-A | staff, inventory_manager | 材質未確認 |
| ITEM-060 | 検査 | site-B | inventory_manager | 材質未確認 |
| ITEM-075 | 加熱 | site-A | staff, inventory_manager | 材質未確認 |
| ITEM-090 | 切断 | site-B | inventory_manager | 材質未確認 |

U01の照会窓口はinventory_managerを候補とするが、担当者の指名・確認資料は未提供。各IDについて「材質は何か、どの資料・確認者・確認時点に基づくか」を確認する。未回答の間は未知を保持し、照会済みとも書かない。回答が一部に限られる場合は、そのIDだけを根拠とともに変更し、残りを一括で木材へ変えない。[D1、D2、review.json U01]

blocking=trueは、この6件を材質確定済みとする判断にのみ適用する。6件を未確認として表示すること、他90件の確定材質での探索、名称変更と空カテゴリ整理を妨げない。照会送信は実行していない。

## 6. 移行前照合と修正手順

1. **入力を固定する。** source revisionがinventory-r17、requirements.current_source_revisionとproposal.basis_revisionが一致することを確認する。comparison.jsonに入力のSHA-256がある。実装段階でsnapshotが更新されたら旧結果を流用せず再比較する。
2. **変更一覧を絞込条件にせず、全集合を比較する。** concepts・records・entriesのID、全宣言フィールド、各参照を照合する。CH01–CH06の理由は別途要件と照合する。既存checkerはchanges本文を自動審査しない。
3. **sourceから修正用の新しい作業集合を作る。** 96件のrecordsをID・label・scope・roles・concept_idsごと保持する。ITEM-X73を自動承継せず、ITEM-073を使う。用途・材質の推定復元やID再採番をしない。入力snapshotは編集しない。
4. **承認済みの2変更だけを概念に適用する。** task.heat.labelを加熱へ変更し、空のlegacy.unusedを削除する。task.measure、task.cut、maintenance.inspect、material.unspecifiedを残す。task.workは採用しない。
5. **入口条件を保持する。** 提供2入口のID/path/role/scope/concept_idsをsourceと同一にする。entry.measure=[task.measure]、entry.heat=[task.heat]を明示する。
6. **実際に移す予定の成果データを再取得し、以下の受入条件で差分照合する。** ここで検査したメモリ内モデルの一致だけを実移行結果に転用しない。
7. **実装担当へ引き継ぐ。** 旧URLからの条件保持、実認可、検索索引、条件変更や0件時の操作・表示を実環境で確認する。必要な情報が隠れていないかと利用者の探索成功は別の評価にする。

移行対象データの受入条件：

- ID集合がsourceと完全一致し、追加・削除・重複が0件。ITEM-073があり、ITEM-X73がない。
- 各レコードのlabel・scope・rolesがsourceと一致。特にITEM-088=site-B、ITEM-090=inventory_managerのみ。
- レコードID→concept_idの集合がsourceの204ペアと完全一致。総数のみの一致は不可。
- 概念差分はtask.heatのlabel変更とlegacy.unused削除だけ。残る概念ID・axisはsourceと一致し、参照切れ0件。
- 材質未確認の対象IDが6件と完全一致。木材45・金属45・未確認6の件数は補助値として確認する。
- 2入口の宣言条件が一致し、同role/scopeで期待するID集合が一致する。測定入口の無条件化を許さない。
- 説明できない追加差分があればその差分を含む移行を止め、元の保持条件へ戻す。未確認材質については未知を保持する運用で進め、確定変換だけを保留する。

この受入リストは実装先での今後の手順。今回実施した内容は次節に限定する。

## 7. 実行済みの検査と未実施事項

| 層 | 実施したこと | 限界 |
|---|---|---|
| 入力・構造 | compare_inventory.pyで全snapshotの宣言フィールドを比較。status=COMPARED、decision=NOT_EVALUATED | 比較終了は承認・品質PASSではない。changesは未検査フィールド |
| 意味レビュー | 要件、CH01–CH06、変更一覧外のID/scope/roles差分を照合 | 提供された合成要件の範囲。外部承認・ログ・実設備を調査していない |
| 設計モデル | sourceを基にしたメモリ内の修正モデルで、全96件・204所属・2入口の不変条件と集合計算を確認 | 自作コードによる自己確認。実移行結果や独立評価ではない |
| 成果物 | review.jsonの出力契約、HTMLの静的行と内部アンカーをソース解析で確認 | ブラウザ描画・操作は未実施。HTML解析は視覚品質やWCAG適合の確認ではない |
| 実装・人の結果 | 未実施 | 転送、認可、索引、操作状態、表示収まり、発見率、正答率、時間、選好は未確認 |

U02は遷移・認可・検索実装担当、U03は画面実装・利用者評価担当への引継ぎ。どちらも実担当者は未指定で、実施済みの引継ぎ連絡や承認を意味しない。既存の見た目を変える案は作っておらず、標準HTMLの採用から見た目の維持が検証できたとも言わない。

## 8. 出典と方法の範囲

- **D1：requirements.json**（版番号の記載なし、今回提供版、case_id=R04-equipment-reclassification）。must_preserve、approved_changes、visual_intent、scope_boundaryを判断基準にした。
- **D2：source-inventory.json**（revision=inventory-r17）。全96レコード・9概念・2入口を保持照合の正本にした。
- **D3：proposed-inventory.json**（revision=inventory-r18-proposed、basis_revision=inventory-r17）。全レコード、概念、入口、CH01–CH06をレビュー対象にした。rationaleは承認根拠ではない。
- **D4：task.md / output-contract.json**（ともに版番号の記載なし、今回提供版）。3成果物の形と確認範囲を優先し、一般plan.jsonは作成対象外とした。
- **M1：SKILL.md**（name=anything-frontend-product-ia、版番号の記載なし、今回提供版）。目標・情報関係、既存視覚意図の維持、構造と実利用の区別を適用。
- **M2：information-architecture.md / taxonomy-change.md**（版番号の記載なし、今回提供版）。対象・分類・所属・入口を別々に照合する手順を適用。
- **M3：navigation-evidence.md**（版番号の記載なし、今回提供版）。role/scope付き旧入口の対象条件保持を適用。
- **M4：decision-information.md / disclosure-and-verification.md**（版番号の記載なし、今回提供版）。未知値の保持、判断情報の所在、検証の層分けを適用。
- **比較補助：compare_inventory.py**（版番号の記載なし、今回提供版）。宣言フィールド差分の抽出に使用。出力のNOT_EVALUATEDを採否へ自動変換していない。

方法資料内の外部原典は今回開いていない。原典の現行性・一般的効果を検証したとは扱わない。与えられたファイルと、自分が作った確認記録だけを使用した。
