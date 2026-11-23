# 予約変更の情報設計を調べる

**問い**　予約を取り違えずに変更するには、利用者が知っている情報をどの入口と候補行に出し、どこまで確かめればよいか。

- **題**　予約変更の情報設計
- **読み**　よやくへんこう の じょうほうせっけい
- **最初の検索語**　information architecture、card sorting、tree testing、change appointment、利用者の課題とサービスの範囲

## 調査の論点

- [x] 知見が集まる媒体と話題は何か。政府のサービス標準、Webの規格、実務記事、連邦機関の技術報告に原典があった。IA-01、IA-03、IA-04、IA-05。
- [x] 利用者の目的から関連機能をどこでまとめ、どこで分けるか。IA-01 の “Do one task per transaction”、IA-02 の “The principle of choices”。
- [x] 同じ種類の予約が複数あるとき、何を手掛かりにし、どの条件で分類やラベルだけでは足りないか。IA-02 の “The principle of objects”、IA-07 の “What you can do in the NHS App” と “Missing or incorrect information”。
- [x] カードソートとツリーテストが得る観察と限界は何か。IA-04 §1・§3、IA-05 の “The technique”、IA-06 の実施と分析。
- [x] 同じ課題で比較するとき、原典の判断をどう取り入れ、どこまで操作するか。IA-08 の入口9、15、39–41行、IA-05 の “Lessons learned”。

## 用語

- 情報設計、内容の対象と属性、選択肢、複数の分類軸、目的のそろったナビゲーション。［IA-02］
- グループ分けを参加者に委ねるオープンカードソート、既存カテゴリを使うクローズドカードソート、分類階層を課題でたどるツリーテスト。［IA-04、IA-05、IA-06］
- 予約変更の確定、変更申請、予約情報の欠落、変更可能条件。［IA-07］

## 人と媒体

| 人・組織 | 媒体と資料 |
| --- | --- |
| Government Digital Service、Driver and Vehicle Standards Agency | GOV.UKのサービスマニュアルと実サービスの公開案内。IA-01、IA-07。 |
| Dan Brown | ASIS&T の Bulletin。IA-02。 |
| W3C Accessibility Guidelines Working Group | W3C勧告。IA-03。 |
| Vicki Ahlstrom、Kenneth Allendoerfer | FAA William J. Hughes Technical Center の技術報告。IA-04。 |
| Dave O’Brien、Donna Spencer | Boxes and Arrows の実践記録。IA-05。 |
| Lindsay Goldstein、Maroya Faied、Shannon McHarg | Digital.gov と ONRR の調査資料。IA-06。 |
| NHS England、County Durham and Darlington NHS Foundation Trust | 利用者向け案内。IA-07。 |

## 原文と今回の適用

取得日は2026年11月23日。本文の取得元、ファイルと状態は[取得記録](fetch-log.jsonl)にある。公開同梱の原典には[権利表示](sources/README.md)が付く。

| ID | 一次資料と参照位置 | 今回の判断に使う条件 |
| --- | --- | --- |
| IA-01 | Government Digital Service。[Solve a whole problem for users](https://www.gov.uk/service-manual/service-standard/point-2-solve-a-whole-problem)（2026-01-29版 “What it means”）、[Getting the scope of your transaction right](https://www.gov.uk/service-manual/design/scoping-your-service)（2019-05-01版 “Do one task per transaction”）、[Naming your service](https://www.gov.uk/service-manual/design/naming-your-service)（2016-10-18版 “How to name your service”、 “Use research and testing”）。 | 目の前の操作から範囲を決めず、利用者の目的と近い別の取引を比べる。入口名を区別できない場合は機能の切り分けも確認する。 |
| IA-02 | Dan Brown, [Eight Principles of Information Architecture](https://doi.org/10.1002/bult.2010.1720360609), Bulletin ASIS&T 36(6), 2010, pp.30–34。Objects、Choices、Disclosure、Multiple Classification、Focused Navigation。組版された[同版PDF](https://uxgu.ru/ext/asis.org/Bulletin/Aug-10/AugSep10_Brown.pdf)でも確認。 | 対象の属性と可能な操作から分類軸を組む。選択前には次の判断ができる情報を出す。今回の分類効果を示す実験値としては使わない。 |
| IA-03 | W3C Recommendation, [WCAG 2.2](https://www.w3.org/TR/2024/REC-WCAG22-20241212/), 2024-12-12、SC 2.4.4・2.4.5・2.4.6。[同梱原文](sources/w3c/wcag22-2024-12-12.html)。 | リンク目的は文言またはプログラムで判定可能な文脈と合わせて確認する。見出し・ラベルは話題・目的を表す。複数経路の条件では、ページ集合と手続きの段階・結果ページの例外を確認する。 |
| IA-04 | Vicki Ahlstrom and Kenneth Allendoerfer, FAA [Information Organization for a Portal Using a Card-Sorting Technique](https://hf.tc.faa.gov/publications/2004-information-organization-for-a-portal-using-a-card-sorting-technique/full_text.pdf), September 2004, DOT/FAA/CT-TN04/31、§1、§3、§4。 | カード配置から分類候補や語彙を得る。分類時に置いたカテゴリと課題で探すカテゴリが一致するとは限らないので、到達を別に観察する。 |
| IA-05 | Dave O’Brien, [Tree Testing](https://boxesandarrows.com/tree-testing/), 2009-12-05版 “The technique”、 “Devising tasks”、 “The results”、 “Lessons learned”。本文が参照する Donna Spencer, [Card-Based Classification Evaluation](https://boxesandarrows.com/card-based-classification-evaluation/), 2003-04-07版 準備物、階層の転記、紙の課題提示手順。 | 現実的な課題を、同じ到達先・条件で提示し、初期選択、経路、回り道、到達、断念を記録する。ツリーの結果を画面全体や予約の確定の成績に広げない。 |
| IA-06 | Lindsay Goldstein、Maroya Faied、Shannon McHarg, [Open-source Information Architecture Design](https://digital.gov/2022/01/06/open-source-information-architecture-design-using-the-tools-you-have-to-conduct-card-sorting-and-tree-testing/), Digital.gov 2022-01-06、 “Card sorting” と “Tree Testing” 内の計画、実施、分析。[ONRR実施計画](https://github.com/DOI-ONRR/research/blob/master/onnr-dot-gov-research/06_tree_test/plan.md) “Goals”、 “Tasks”。 | 実利用者11名に課題を実施した別案件。順序による学習に対処し、経路の一致と分岐を観察した。今回の架空予約では比較手順の参考にする。 |
| IA-07 | NHS England [Hospital referrals and appointments](https://www.nhs.uk/nhs-app/help/appointments/hospital-and-other-appointments/)（2026-03-18レビュー版） “Rescheduling your appointment” と “Missing or incorrect information”。[County Durham and Darlington NHS Foundation Trustの案内](https://www.cddft.nhs.uk/patients-and-visitors/appointments/managing-your-outpatient-appointments-nhs-app) “What you can do in the NHS App” と “Changing or cancelling an appointment”。DVSA [Booking your test](https://www.gov.uk/theory-test/book-test) “Change or check your test details” → [Change your theory test appointment](https://www.gov.uk/change-theory-test) “What you’ll need”。 | 同種の予約は先に対象を選び、日時・場所などを手掛かりにする。欠落や承認待ち、受付条件、必要な識別番号は分類を変えても残る。GOV.UKの公開案内はリンク先まで操作し、NHSは公開手引を確認した。 |
| IA-08 | Anything Frontend Art Direction, [SKILL.md f5df625](https://github.com/RNA4219/anything-frontend-art-direction/blob/f5df625dbc577d6a3ca28e13ef09e39b135b4a6f/SKILL.md#L9), 9、15、17、39–41行。[visual-direction.md 57–59行](https://github.com/RNA4219/anything-frontend-art-direction/blob/f5df625dbc577d6a3ca28e13ef09e39b135b4a6f/references/visual-direction.md#L57)、[c-usability.md 3行](https://github.com/RNA4219/anything-frontend-art-direction/blob/f5df625dbc577d6a3ca28e13ef09e39b135b4a6f/references/c-usability.md#L3)。 | 役割が近い現物と制作者の説明を探す。利用者の課題と入力をそろえ、影響を観察した差だけを採用理由にする。[sankai の照合記録](sankai.md) |

## 調査の区切り

上の五つの論点に一次資料の位置が付き、原典から別資料へのたどり直しを確認できた。発案者の特定や媒体の網羅、今回の予約画面の実利用者データは確認対象に含めていない。追加で実利用者の経路を比較する際は、既知の手掛かり、選べる予約の件数、入口を開く前の情報を揃える。

## Art Direction との適用境界

見本の選び方、同条件の比較、出典と実観察を結ぶ手順を参照した。ここで扱う差は入口、分類、ラベル、選択前に必要な情報。配色・書体・余白・構図の選択は引用元の対象であり、端末幅・描画・読み上げを含めた確認は実画面で行う。予約枠の競合、送信の再試行、永続化はフロー・QA担当に渡す。[sankaiの照合記録](sankai.md)
