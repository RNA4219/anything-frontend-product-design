# デザインQA・受入評価の原典マップ

誰が何を達成したら完了かを定め、正常・異常・復帰を操作して、どの証拠で採否を判断できるかを調べた。取得と探索の経緯は [調査ログ](log.md) に記録した。

## 論点

| 論点 | 原典を当てた範囲 |
| --- | --- |
| この分野の知見はどこに集まるか | W3C WAI の規格と評価方法、GOV.UK の制作・サービス評価資料、DialogDesign の比較評価資料、HCI 研究者の原著。 |
| 「失敗観測・証拠不足・正常経路だけの合格」を何で区別できるか | EM・WCAG の範囲、既定経路と分岐、再現可能な記録。判定名と必須条件の組み合わせは本 Skill の判断規則。 |
| 復帰時の完了をどう認定できるか | GOV-V・GOV-E・GOV-C の訂正、保存状態、確認の例。競合と応答消失の試作では元予約、最新予約、再表示、確定回数を観察した。 |
| 同じ課題・入力・成功条件の比較はどこまで有効か | GOV-B・CUE・EE・ORDER。到達点、評価者差、比較順序を確認した。試作の比較では評価者が指定経路を実行した。 |
| 合成ケースで何を断定できないか | GOV-B の参加者・達成・誤達成、CUE の試験終了点、EE の解釈差。実利用者の達成率、対象外の環境、本番の同時実行や副作用は別の証拠を要する。 |

## 用語・人・媒体

- 完全なプロセス、既定経路、分岐経路、評価範囲、適合主張。W3C Accessibility Guidelines Working Group、W3C WAI。
- 検証エラー、入力保存状態、完了確認、利用ベンチマーク。GOV.UK Design System team、Service Manual。
- 課題達成、誤達成、time-on-task、evaluator effect、順序効果。Rolf Molich、Tomer Sharon、Jurek Kirakowski、Morten Hertzum、Niels Ebbe Jacobsen、I. Scott MacKenzie。DialogDesign、Journal of Usability Studies、Behaviour & Information Technology、York University。

## 一次資料

取得日は2026年11月23日。本文のローカル保存名は [取得ログ](fetch-log.jsonl) の `file`。PDF は本文PDFと抽出テキストを保管した。GOV-E の [作例コードと権利表示](source-code/NOTICE.md) を同梱した。第三者資料には原典の権利表示と条件が適用される。

| ID | 文書・版 | 確認位置 | 権利・公開範囲 |
| --- | --- | --- | --- |
| EM | W3C, WCAG-EM 2.0、2026-07-23 Group Note。 [固定版](https://www.w3.org/TR/2026/NOTE-wcag-em-2-20260723/) | §4.1、§4.3.3、§4.4.2、§4.5.1 | W3C Document License。取得した抽出本文はローカル保管。 |
| WCAG | W3C, WCAG 2.2、2024-12-12 Recommendation。 [固定版](https://www.w3.org/TR/2024/REC-WCAG22-20241212/) | 3.3.1、3.3.3、4.1.3、§5.2.3 | W3C Document License。取得した抽出本文はローカル保管。 |
| GOV-V | GOV.UK Design System, Recover from validation errors、取得日版。 [原典](https://design-system.service.gov.uk/patterns/validation/) | When not to use、How to tell the user、Research on this pattern | Crown copyright。別記のない内容は OGL v3.0。 |
| GOV-E | GOV.UK Design System, There is a problem with the service pages、取得日版。 [原典](https://design-system.service.gov.uk/patterns/problem-with-the-service-pages/) | How it works、Research on this pattern、回答が [保存された画面](https://design-system.service.gov.uk/patterns/problem-with-the-service-pages/offline-support-link/) と [保存されなかった画面](https://design-system.service.gov.uk/patterns/problem-with-the-service-pages/offline-support/) | Crown copyright。別記のない内容は OGL v3.0。 |
| GOV-C | GOV.UK Design System, Confirmation pages、取得日版。 [原典](https://design-system.service.gov.uk/patterns/confirmation-pages/) | How it works、Help users who bookmark the page、Known gaps | Crown copyright。別記のない内容は OGL v3.0。 |
| GOV-B | GOV.UK Service Manual, Usability benchmarking a website or whole service、2018-08-06。 [原典](https://www.gov.uk/service-manual/measuring-success/usability-benchmarking-a-website-or-whole-service) | Choosing tasks to test、Recruiting participants、What to measure、Running future rounds | Crown copyright。別記のない内容は OGL v3.0。 |
| CUE | Molich、Sharon、Kirakowski、CUE-8、2010。 [掲載論文の著者公開版](https://www.dialogdesign.dk/tekster/cue8/CUE-8_JUS.pdf)・[会議報告](https://www.dialogdesign.dk/tekster/cue8/CUE-8_UPA.pdf) | Method、Measurement Approaches、Measuring Time-on-task。実施主体の [実施指示書 Version 5](https://www.dialogdesign.dk/tekster/cue8/cue-8instr.pdf) §4–5 も参照。 | 掲載論文の著者公開版 p.1 は個人・教室に複製を限定。公開物にはリンクを収録。 |
| EE | Hertzum、Molich、Jacobsen、2014。 [著者プレプリント](https://mortenhertzum.dk/publ/BIT2014.pdf)・[DOI](https://doi.org/10.1080/0144929X.2013.783114) | §4.4、§5.3–5.4 | 再配布条件未確認。公開物にはリンクを収録。 |
| ORDER | I. Scott MacKenzie、Within-subjects vs. Between-subjects Designs: Which to Use?、2013-03-29。 [著者の研究ノート](https://www.yorku.ca/mack/RN-Counterbalancing.html) | Interference Effects and Learning Effects、Counterbalancing | 再配布条件未確認。公開物にはリンクを収録。 |

## Art Direction との境界

参照版は Anything Frontend Art Direction の `f5df625`。 [公開リポジトリの該当版](https://github.com/RNA4219/anything-frontend-art-direction/tree/f5df625)

- `SKILL.md` の「レビューでの使い方」、`references/c-usability.md` C-01・C3-01〜07 と、対象状況を先に決め、出典の種類を見極め、実画面で観察を分ける考え方が重なる。Dではその観察を利用課題ID・受入条件ID・リリース判定に結ぶ。
- `references/visual-direction.md` の「意匠の採用条件」と、比較時に同じ文言・データ・幅・状態を使う点が重なる。Art Direction が扱う主役、字・地・線などの表現を適用したあと、Dでは同じ課題で発見・操作・完了を再確認する。
- `references/g-state-forms.md` と `checklists/forms.md` に入力保持、訂正、送信、成功表示の関連確認がある。Dの受入計画では、Bが定めた遷移や C が用意した部品の挙動を実際の操作で観測する。
