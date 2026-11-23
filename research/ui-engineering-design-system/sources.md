# 原典台帳

取得日は 2026-11-23（JST）。取得の成否、公開元、原文ファイル名、SHA-256 は [取得ログ](fetch-log.jsonl) に記録する。同梱した原典の権利表示は末尾にある。

| ID | 制作者・版 | 確認箇所と適用範囲 |
| --- | --- | --- |
| GOV-1 | GOV.UK Design System team。取得日の公開ページ、同梱ソースは `ff97fa6` | 提案に求める用途の広がりと既存部品との差、公開前の使いやすさ・一貫性・適用範囲。GOV.UK自身の掲載基準。 [Contribution criteria](https://design-system.service.gov.uk/community/contribution-criteria/) |
| GOV-2 | GOV.UK Design System team。取得日版 | Start with override classes、Small modifications、Large modifications、Check for accessibility。変更が既存部品の前提を外れる実例として、本文から Accordion と Step by step の両方を開き、用途と構造を確認。 [Extending and modifying components in production](https://design-system.service.gov.uk/get-started/extending-and-modifying-components/) · [Accordion](https://design-system.service.gov.uk/components/accordion/) · [Step by step navigation](https://design-system.service.gov.uk/patterns/step-by-step-navigation/) |
| HTML-1 | WHATWG HTML Living Standard。2026-11-22 固定版 | 4.10.1.1 フォームの作例、4.10.4 ラベル、4.10.6 ボタン、4.10.15–16 グループと凡例。 [スナップショット](https://html.spec.whatwg.org/commit-snapshots/6eac2b50b1af183f30fa2760b0269a0410f58a91/) · [フォーム](https://html.spec.whatwg.org/multipage/forms.html#the-label-element) · [フォーム要素](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |
| HTML-2 | WHATWG HTML Living Standard。同上 | 4.10.5.1.16。同じフォーム所有者・ツリー・空でない名前を持つ radio が属するグループと、単独 radio の制約。 [Radio Button state](https://html.spec.whatwg.org/multipage/input.html#radio-button-state-(type=radio)) |
| WCAG-1 | W3C、WCAG 2.2 Recommendation、2024-12-12 | SC 1.3.1、1.4.10、2.1.1、2.4.3、2.4.7、2.4.11、2.5.8、3.3.1、4.1.2、4.1.3。320 CSS px の関係は Reflow の解説 Note 1。 [WCAG 2.2](https://www.w3.org/TR/2024/REC-WCAG22-20241212/) · [Understanding Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) |
| ARIA-1 | W3C、WAI-ARIA 1.2 Recommendation、2023-06-06 | `status` と `alert` のロールと暗黙のライブ領域属性。 [status](https://www.w3.org/TR/2023/REC-wai-aria-1.2-20230606/#status) · [alert](https://www.w3.org/TR/2023/REC-wai-aria-1.2-20230606/#alert) |
| APG-1 | W3C WAI、APG。取得日版 | Read Me First の Principle 1 と Mobile and Touch Support、Keyboard Interface の Focus 節。ブラウザー・支援技術の組合せは個別に確かめる。 [Read Me First](https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/) · [Developing a Keyboard Interface](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/) |
| WAI-1 | W3C WAI、WCAG 2.2 Understanding と Techniques。取得日版 | フォーカスが変わらない通知の範囲と、空の `status` を用意する試験手順・実例。 [Understanding Status Messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) · [ARIA22](https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA22) |
| WAI-2 | Eric Eggert、Shadi Abou-Zahra、W3C WAI。2026-03-27更新 | Radio buttons のグループ名と個別ラベルの実例。 [Grouping Controls](https://www.w3.org/WAI/tutorials/forms/grouping/) |
| USW-1 | U.S. General Services Administration、USWDS team。Theme の記載更新 2024-05-15 | About、Customizing、Using。基礎色と用途の命名・差し替え、状態色の使用例。 [Theme color tokens](https://designsystem.digital.gov/design-tokens/color/theme-tokens/) · [State color tokens](https://designsystem.digital.gov/design-tokens/color/state-tokens/) |
| DTCG-1 | Design Tokens Community Group、Final Community Group Report 2025.10 | §7.2–7.2.3。別名の連鎖解決、循環の扱い。作例の CSS は JSON 形式仕様の実装対象外。 [Design Tokens Format Module](https://www.designtokens.org/tr/2025.10/format/#reference-resolution) |
| STR-1 | Stripe Docs、取得日版。API v1 | Network errors と Server errors の判断。接続の切断や 500 は確定結果の粒度が異なり、対象の再取得や別の照合手段が必要になり得る。 [Advanced error handling](https://docs.stripe.com/error-low-level) |
| STR-2 | Stripe API Reference、取得日版。API v1 | キー再使用時の結果とパラメータ照合、保存期間と対象になるリクエスト。Stripe 固有の契約。 [Idempotent requests](https://docs.stripe.com/api/idempotent_requests) |
| AWS-1 | Malcolm Featonby、Amazon Builders' Library、2021年公開 | Reducing client complexity、Late arriving requests、Same client request ID, different intent。キーと処理の同一性、保持期限、更新との整合。 [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) |
| HCI-1 | Bargas-Avila ほか、2007、Interacting with Computers 19(3)、330–341、DOI 10.1016/j.intcom.2007.01.003 | §3.4–3.5、§4.4–4.5、Tables 3、7、8。学部生を用いたドイツ語フォームで入力エラーの時機を比較。人工的な課題と説明省略が条件。予約の競合や支援技術での通知の効果は別途検証が必要。 [大学書誌](https://edoc.unibas.ch/entities/publication/b7cc4232-bd8e-4573-afd9-313e02dea377) · [論文PDF](https://interruptions.net/private/misc/Bargas-Avila-IntCom07.pdf) |
| AD-1 | Anything Frontend Art Direction、`f5df625` | E「フォーカスの扱い」、G「フォームとフィールドセット」「制約検証と送信」、I「テーマとコンポーネントライブラリ」、visual-composition「広幅から狭幅へ組み直す」。フォーム、フォーカス、テーマの適用点が重なる。Cは部品、状態、置換後の機能検証を担当。題材に基づく配色・書体・構図と視覚案の採用は Art Direction。 [参照した版](https://github.com/RNA4219/anything-frontend-art-direction/tree/f5df625) |

## 同梱と権利表示

[GOV.UK Contribution criteria の原典ソース](sources/govuk-contribution-criteria.md) は GOV.UK Design System team の資料（© Crown copyright）。Contains public sector information licensed under the Open Government Licence v3.0. 公開ページの権利表示を確認し、対応する上流ソースを未改変で収録した。上流のテンプレート記法と相対リンクを含む。 [公開ページ](https://design-system.service.gov.uk/community/contribution-criteria/) · [上流の版](https://github.com/alphagov/govuk-design-system/blob/ff97fa694738caafdd696bdbdd3e912b9910ed1e/src/community/contribution-criteria/index.md) · [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

他の原典は公開元・位置と取得記録で参照する。WHATWG は IPR Policy の §7.1、W3C Recommendation は文書ライセンスを確認。HCI-1 のPDFは Elsevier の権利表示に従い引用位置のみ示す。 [WHATWG IPR Policy](https://whatwg.org/ipr-policy#copyright-license-for-whatwg-publications) · [W3C Document License](https://www.w3.org/copyright/document-license-2023/)
