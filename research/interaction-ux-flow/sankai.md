# Art Direction の判断手順を操作フロー設計に使う

分解対象は [Art Direction の SKILL.md](sources/art-direction-skill.md) の固定版 `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f`。照合した原文は45行です。

| 作業単位 | 操作フローに適用する条件 |
| --- | --- |
| U1 見本を実見する（9行） | 新規フローでは、利用者が近い判断をする例の制作者資料と実物または同じ版の画面を開く。実見できない場合は代替を探し、観察できた範囲を記録する。小修正は症状に合わせて調査を絞れる。 |
| U2 条件を揃えて比べる（15行） | 採否が分かれる箇所を、同じ課題、入力、成功条件で比べる。既存版を片方に使え、症状が局所的ならその操作前後に絞れる。数字や画面上の差は、確認した条件で判断する。 |
| U3 再現条件を定め、原典と操作を照合する（17、39–41行） | 起点・選択・結果を確認する経路を定め、出典が保証する条件と、実際に観察した結果を記録する。通信先の代わりに状態モデルを使う場合は、模擬した入力と観察できる範囲が分かるようにする。 |

## 補足に読んだ固定版の資料と担当範囲

- **D-31、D-34〜38** は、問題から修復操作への経路、仮表示、複数の保留、再取得失敗、古い応答を考える入口です。D-34〜38は TanStack Query の事例です。B は保留・確定を見分ける条件と結果の扱いを決めます。キャッシュ更新や表示の実装は対象環境に合わせて選びます。 [d-interaction.md](https://github.com/RNA4219/anything-frontend-art-direction/blob/f5df625dbc577d6a3ca28e13ef09e39b135b4a6f/references/d-interaction.md#L41-L48)
- **G-03、G-05、G-06** は React の資料です。B はどの事実から表示を導くか、どの応答を受理するか、何を復元するかを定めます。フォーム確認表からは、不正値で送信に進まないこと、修正に戻れること、エラーが出る時点を参照しました。ラベルの連動、Enter の既定動作、HTML 要素の仕様は部品側で確認する項目です。 [g-state-forms.md](https://github.com/RNA4219/anything-frontend-art-direction/blob/f5df625dbc577d6a3ca28e13ef09e39b135b4a6f/references/g-state-forms.md#L13-L16)、[forms.md](https://github.com/RNA4219/anything-frontend-art-direction/blob/f5df625dbc577d6a3ca28e13ef09e39b135b4a6f/checklists/forms.md)
- **visual-direction** からは、役割が近い見本を同じ版で見る方法、比較条件を揃える方法、観察と操作の検査を区別して記録する方法を参照しました。字・地・線・画像の関係、広幅・狭幅での見え方は Art Direction の採用判断です。 [見本の探索](https://github.com/RNA4219/anything-frontend-art-direction/blob/f5df625dbc577d6a3ca28e13ef09e39b135b4a6f/references/visual-direction.md#L15-L19)、[採用条件](https://github.com/RNA4219/anything-frontend-art-direction/blob/f5df625dbc577d6a3ca28e13ef09e39b135b4a6f/references/visual-direction.md#L55-L65)

## 適用先で照合した原典

- 状態・イベント・遷移条件は SCXML §3.5。版の競合と更新再送は RFC 9110 §9.2.2、§13.1.1。同じ操作 ID の遅延再送、意味の違う入力、保持期間は AWS の実例に照らす。各資料の契約を、採用するサービスの保証と照合する。 [SCXML](https://www.w3.org/TR/2015/REC-scxml-20150901/#transition)、[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1)、[AWS](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- 旧枠の保持は USP「Reschedule Booking」466–492行の原子的な更新が成立する場合を手掛かりにした。NHS の事例では日程変更依頼を確認して送信し、医療機関が依頼を審査する場合がある。B では受付と業務上の変更確定をそれぞれ表し、最後の結果まで確かめる。 [USP 固定版](sources/usp-booking.md#L466-L492)、[NHS App](https://www.nhs.uk/nhs-app/help/appointments/hospital-and-other-appointments/)
- 確定前に選択・入力を修正できる確認と、完了後の参照情報や次の操作は GOV.UK の各パターンに照らす。同一画面内の状態通知は WCAG 2.2 の 4.1.3、対象となる重要な送信の誤り防止は 3.3.4 の条件を確認する。 [Check answers](https://design-system.service.gov.uk/patterns/check-answers/)、[Confirmation pages](https://design-system.service.gov.uk/patterns/confirmation-pages/)、[WCAG 2.2 4.1.3](https://www.w3.org/TR/WCAG22/#status-messages)、[WCAG 2.2 3.3.4](https://www.w3.org/TR/WCAG22/#error-prevention-legal-financial-data)
