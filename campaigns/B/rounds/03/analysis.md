# R03 Analyst handoff

**抽出候補は B-IU-007 と B-IU-008 の2単位。** 詳細な指示本文、適用・非適用、条件規則、例外、依存、原典事実、未確定事項、固定13ケース対応は `units.json` にまとめた。状態は候補であり、登録・採用・fixture合格を意味しない。

## 分解・理解・溶解

実在する sankai の README、本体、decompose / understand / dissolve を読んだ。専用CLIは使っていない。研究者2名の findings、取得済みcaptureの該当箇所、R03 task/cases、既存 B-IU-001/002/005/006 と重複記録を照合した。

| 候補 | 仕事の境界 | 追加する条件 |
| --- | --- | --- |
| B-IU-007 | 中断した作業を、現在の主体・能力へ結び直す | query前の既知account不一致、再認証後のcapability再確認、同一intent/operationへの復帰、record欠落時の未解決、遅延応答の現在viewへの適用条件 |
| B-IU-008 | 更新された事実で比較・再判断し、条件付き変更と結果表示を結ぶ | opaque/equalityとHTTP強比較、対象資源の範囲、readと承認の分離、旧readの採否、操作時snapshotと現在resource観測の分離 |

R01の結果不明・再送とR02の修正・確認は依存先として再利用する。PR2のdraft/reopen/If-Match/conflict、Art Directionの [G-06](https://github.com/RNA4219/anything-frontend-art-direction/blob/main/references/g-state-forms.md#g-06)、[D-38](https://github.com/RNA4219/anything-frontend-art-direction/blob/main/references/d-interaction.md#d-38)、D-41は既知の概念で、新原則として数えない。

## 引継ぎで保持する境界

- WCAG 2.2.5 は **AAA**。Understanding は informative。fixtureの復帰要件は task 契約であり、AA一般義務・無期限保存・唯一の保存方式へ拡張しない。
- current identity/capability は確立済み認証系のtrusted input。保存record、同じorigin/tab、frontend guardをサーバー認可の証明にしない。保存/auth/React実装はCと適用先へ渡す。
- ETagはopaque。HTTP If-Matchの強比較、AIP-154のetag/ABORTED、Calendarの412を別契約として扱う。target validatorから関連枠等の原子性は導かない。
- Calendarの再取得・自動再設定sampleを利用者の再承認規範にしない。重要な事実変更への再判断はtaskとB-IU-006の適用である。
- 旧readを現在viewへ適用しないことと、正しくowner/target/operationへ相関した確定結果の無効化を分ける。結果の保存・表示は権限・保持契約に従う。React cleanupやepochを必須方式にしない。
- 今回のlookupは操作実行時snapshot、loadはresourceの現在観測。両方の事実を扱うため分けるが、単一応答で両方が権威をもって確定するAPIには追加照会を要求しない。current read失敗で確認済み操作成功を消さない。
- recovery record欠落/失効は未適用の証拠ではない。

## 固定ケースと未確定範囲

B-IU-007の主担当は **R01–R05・R09・R10**、B-IU-008は **R06–R08・R11–R13**。13件を重複なしの主担当へ割り当て、関連規則は相互に参照した。すべて **Analyst未実行の検証計画** と記録し、事前固定ケースを増減していない。

原典上の制約とfixture契約は分離済み。実APIのvalidator coverage/エラー対応、field依存とmerge可否、関連resource transaction、Cの認証・認可・保持・応答適用保証は適用先の未確定事項として、影響する判断だけに限定した。取得していない技法本文や実サービス適合、人の効率改善を検証済みとはしない。

再構成・登録・実装・実行検証は親へ引き継ぐ。
