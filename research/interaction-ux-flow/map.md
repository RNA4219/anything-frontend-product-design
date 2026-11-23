# 予約変更の操作・状態設計の原典

**問い**　利用者は競合や送信後の通信断が起きても、元の予約を失わず、重複なしで日時を変更し、最終結果を確認できるか。採用条件と、サービスがその条件を満たさない場合の復帰先を調べる。

## 調査の論点

| 論点 | 原典の位置 |
| --- | --- |
| 1. 知見はどの媒体に集まるか | W3C勧告の状態構文、IETFのHTTPメソッド・条件付き更新、ACMの通信研究、Amazon Builders’ LibraryのAPI実装、NHSの利用者向け案内、GOV.UKのデザインシステムと利用観察。下表の SCXML・RFC・RPC・AWS・NHS・GOV-CHECK・GOV-REVISIT |
| 2. 状態・イベント・ガードをどう関連づけ、何を保持するか | SCXML §3.1.1、§3.5、§5。ローカルの `scxml.md:346,368`（“only if an event”）。ART-STATE D-38、G-03、G-06 |
| 3. 予約変更が競合したとき旧予約はどの条件で保持できるか | USP [保存原典477行目](sources/usp-booking.md#L477)（“Reschedule is atomic”）、NHS `nhs-appointments.md:92`（“stay as booked”）、RFC §13.1.1、CAL `calendar-versions.md:29`（“If-Match”） |
| 4. 結果不明・重複・遅延に対して再送が成立する条件は何か | RFC §9.2.2（“Idempotent Methods”）、RPC §3.1–3.2（“Call Identifier”）、AWS `aws-idempotency-html.md:151,230`（“Late arriving requests”） |
| 5. 確認・復帰・完了表示をどの場面で提示し、何が確認できないか | GOV-CHECK `govuk-check-answers.md:390`（“change their answers”）、GOV-DONE `govuk-confirmation.md:100`（“bookmark the page”）、GOV-ITERATE `govuk-carers-study.md:26`、GOV-REVISIT `govuk-return-study.md:26`、WCAG `wcag-status.md:23`（“without receiving focus”） |

## 用語と人

- `state`、`event`、`cond`、`target`、`datamodel` は SCXML。編集長は Jim Barnett（Genesys）。
- `idempotent methods`、`If-Match`、`lost update` は RFC。編集者は Roy Fielding、Mark Nottingham、Julian Reschke。
- `call identifier` は Andrew D. Birrell と Bruce Jay Nelson（Xerox PARC）の RPC 原著。 `same client request ID, different intent` と `late arriving requests` は Malcolm Featonby（AWS）の実装記事。
- `pending` と `reschedule is atomic` はそれぞれ NHS の審査を伴う案内と Wix の仕様例。 `check answers`、`confirmation pages`、`bookmark` は GOV.UK のサービス設計。Mel Johnson は変更前確認の導入事例、Ed Horsford は完了ページへの再訪を報告した。

## 原文

取得日は2026年11月23日。ローカルで取得した原文のファイル名・取得経路は [取得ログ](fetch-log.jsonl) で確認できる。公開する原典と権利表示は [同梱原典](sources/README.md) にまとめた。

| ID | 原典・版・担当 | 該当箇所と公開元 |
| --- | --- | --- |
| SCXML | W3C *State Chart XML (SCXML): State Machine Notation for Control Abstraction* 1.0、2015-09-01 | §3.1.1、§3.5、§5。[W3C固定版](https://www.w3.org/TR/2015/REC-scxml-20150901/#transition) |
| RFC | IETF *HTTP Semantics* RFC 9110 / STD 97、2022-06 | §9.2.2、§13.1.1、§15.5.10、§15.5.13。[再送](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)・[If-Match](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1) |
| RPC | Birrell / Nelson *Implementing Remote Procedure Calls*、ACM TOCS 2(1)、1984-02、pp.39–59 | §3.1–3.2。[著者サイトの書誌](https://www.birrell.org/andrew/papers/)・[UW–Madisonが公開した論文の写し](https://pages.cs.wisc.edu/~remzi/Classes/736/Papers/birrell-rpc.pdf) |
| AWS | Malcolm Featonby *Making retries safe with idempotent APIs*、Amazon Builders’ Library、2021年公開 | “Retries and semantic equivalence”, “Late arriving requests”, “Same client request ID, different intent”。[原文](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) |
| CAL | Google Developers *Get specific versions of resources*、Calendar API v3、取得日版 | “Conditional modification” と例外の挿入操作。[ガイド](https://developers.google.com/workspace/calendar/api/guides/version-resources#conditional_modification) |
| USP | Wix *Booking Lifecycle*、Universal Scheduling Protocol Draft 2026-08-20、固定コミット `c941ac7` | “Reschedule Booking” の “Reschedule is atomic”。[公開仕様](https://usp-protocol.dev/specification/booking/#reschedule-booking-post-bookingsbooking_idreschedule)・[同梱した原典](sources/usp-booking.md) |
| NHS | NHS App *Hospital referrals and appointments*、2026-03-18レビュー | “Rescheduling your appointment”, “Rescheduled or cancelled appointments”, “Missing referrals and appointments”。[NHS App Help](https://www.nhs.uk/nhs-app/help/appointments/hospital-and-other-appointments/#missing-or-incorrect-information) |
| GOV-CHECK | GOV.UK Design System *Check answers*、取得日版 | “Let users go back and change their answers”、配置と変更リンクが見える公開例。[原文](https://design-system.service.gov.uk/patterns/check-answers/#let-users-go-back-and-change-their-answers)・[公開例](https://design-system.service.gov.uk/patterns/check-answers/default/) |
| GOV-DONE | GOV.UK Design System *Confirmation pages*、取得日版 | “How it works”, “Help users who bookmark the page”, “Known gaps” と受付後の案内が見える公開例。[原文](https://design-system.service.gov.uk/patterns/confirmation-pages/#help-users-who-bookmark-the-page)・[公開例](https://design-system.service.gov.uk/patterns/confirmation-pages/default/) |
| GOV-ITERATE | Mel Johnson *A live service is not the end of the story*、DWP Digital、2016-07-08 | “Using data to iterate” と画面資料。複数の変更を含む報告のため、完了率の変化を確認画面だけの効果と扱わない。[制作者の報告](https://dwpdigital.blog.gov.uk/2016/07/08/a-live-service-is-not-the-end-of-the-story/) |
| GOV-REVISIT | Ed Horsford *Do users return to your service after finishing?*、Design in government、2015-12-10 | “Measuring users returning” と改善画面。完了ページへの到達には更新や履歴移動も含まれる。[制作者の報告](https://designnotes.blog.gov.uk/2015/12/10/do-users-return-to-your-service-after-finishing/) |
| WCAG | W3C *WCAG 2.2*、2024-12-12勧告、公式解説は取得日版 | §4.1.3 と、文脈を移動せず伝える状態通知の例。[勧告](https://www.w3.org/TR/2024/REC-WCAG22-20241212/#status-messages)・[解説](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) |
| ART-STATE | Anything Frontend Art Direction、`f5df625dbc577d6a3ca28e13ef09e39b135b4a6f` | 入口の見本・比較・レビュー指示、D-31/D-34〜38、G-03/G-05〜06。位置と適用範囲は [sankaiの照合](sankai.md)。[固定版](https://github.com/RNA4219/anything-frontend-art-direction/tree/f5df625dbc577d6a3ca28e13ef09e39b135b4a6f) |

## 残る問い

実サービスで通信切断後の復帰や競合を起こした観察研究と、個別サービスでの操作IDの保持期間は確認できていない。ダミーの同一入力で結果照会・再送・競合を実行し、サービス契約に依存する判断を [判断条件](../../modules/interaction-ux-flow/references/decisions.md) に記した。
