# 独立反例の期待と実行結果

初回snapshotを固定して実行した。意味判定は検査結果と別の、入力事実に基づくreviewerの判断であり、人の実測や自動意味理解の結果ではない。

| ケース | baseline | 初回candidate | 独立意味判定 | 主な根拠 |
|---|---|---|---|---|
| control_preserve_identity_scope | PASS | PASS | 設計候補として可・実装/人は未確認 | 入力のD-17/D-42、複数所属、未知検索範囲、旧入口の対応をそれぞれ保持する。 |
| ce_short_with_context | FAIL | HOLD | 文脈付きの許容候補・C/人は未確認 | 選択場所の同一liにIDと適用条件があり、文字列衝突だけでは意味の曖昧さは確定しない。HTMLソース上の対応に限る。 |
| ce_short_without_context | FAIL | HOLD | 意味上の欠陥 | 選択時に区別する情報がなく、どちらがD-42かを決められない。HOLDは合格ではない。 |
| ce_context_only_after_landing | FAIL | HOLD | 意味上の欠陥 | 到着後の識別情報は選択時に参照できない。後段の情報を入口の文脈と数える主張を棄却する。 |
| ce_fabricated_distinct_labels | PASS | PASS | 意味上の欠陥 | planの識別表記と実UIにある情報が不一致。文字列一意化は証拠を生まず、Skillはこの回避を明示禁止する。 |
| ce_same_screen_distinct_records | PASS | PASS | 意味上の欠陥 | 同じscreen IDでも別レコードが対象。checkerはtoの不一致しか比較せず、レコード粒度の目的差を検出しない。 |
| ce_unknown_scope_means_global_absence | PASS | PASS | 意味上の欠陥 | 観測範囲が不明な検索0件は全体の不存在を含意しない。入力ではD-42の存在が確定している。 |
| control_zero_within_verified_scope | PASS | PASS | 設計候補として可・実装/人は未確認 | 0件の観測を消さず、確認済みの限定集合についてのみ該当なしと述べている。 |
| ce_legacy_reassigned_to_homonym | PASS | PASS | 意味上の欠陥 | 旧入口はD-17と明記されmust_preserve=true。題名一致で別対象D-42へ置換できない。 |
| ce_duplicate_canonical_by_membership | PASS | PASS | 意味上の欠陥 | 入力は同じD-17の複数所属。独立して更新するコピーを正本化すると同一対象の正本を増やす。 |
| ce_declared_target_after_real_decision | PASS | PASS | 意味上の欠陥 | g_chooseの完了は比較選択。情報IDと機能IDを後段へ複記しても実際の判断場所との不一致を解消しない。 |
| ce_required_information_hidden | FAIL | FAIL | 構造/意味の欠陥 | 選択に必要な改訂情報がtarget画面でprimaryでなくなる。 |
| ce_hard_error_dominates_label_hold | FAIL | FAIL | 構造/意味の欠陥 | 同名ラベルのHOLDへ変更しても必要情報不足のerrorを相殺しない。 |
| control_process_result_no_independent_entry | PASS | PASS | 設計候補として可・B/Cは未確認 | プロセス結果の独立入口を要求する根拠は入力にない。通常探索とmust経路はそのまま存在する。 |

## 読み方

- 短ラベル3件はすべてFAIL→HOLD。文脈なしをPASSにはしていない。文脈ありでも関連付け・人の理解は未確認。
- 6件の意味上の誤案は両checkerでPASS。これらを将来もPASSであるべき正例とは扱わない。手順で欠陥と判断し、検査範囲の限界として保持する。
- 必須情報不足の2件はFAILを維持。HOLDがerrorを相殺しない。
- 限定0件の対照はその入力の範囲を述べることだけを確認する。検索サービス全体のe_search=unknownを解消した実測ではない。
- HTMLを置いたケースはソース対比だけ。ブラウザー描画、クリック、支援技術、人の理解は未確認。
- 親の修正後は6つの意味反例だけを再実行し、4つの未検査フラグを確認した。初回成果は上書きしていない。

再現用スクリプト: run_counterexamples.py。各入力・事前期待・実行結果はcounterexamples/以下。修正版の記録はcorrection-check/以下。
