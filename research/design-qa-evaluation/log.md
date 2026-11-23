# 調査ログ

2026年11月23日。目的は、利用課題から正常・異常・復帰の条件を定め、結果まで操作した証拠によって採否を提案するための原典を見つけること。

## 0周目

- 規格・制作資料の検索役。W3C WAI と GOV.UK の評価と実例を探した。5検索語、34件。固定版 WCAG-EM と WCAG、GOV.UK の実例と Service Manual の候補を返した。
- 研究・作り手の実例の検索役。比較実験、評価者差、学習・順序効果、業務試作を探した。12検索記録、181件。最初の4語は一括検索で返却結果と各語の対応が得られなかったため1記録にまとめた。CUE-8、Hertzum ら、MacKenzie、NASA の候補を返した。
- 検索役は公開候補の検索、メタデータ、位置の確認までを担当した。検索記録は [queries.jsonl](queries.jsonl)。

## 1周目

- WCAG-EM 最新の安定版から固定版を開き、完全なプロセスの選択と評価手順から WCAG 2.2 の完全なプロセスへ進んだ。EM は適合評価の方法、WCAG は適合要件として扱う。
- GOV.UK の検証エラーから障害画面と実例に進んだ。元の画面と保存状態が違う [保存例](https://design-system.service.gov.uk/patterns/problem-with-the-service-pages/offline-support-link/) と [未保存例](https://design-system.service.gov.uk/patterns/problem-with-the-service-pages/offline-support/) を開いた。次の行動が保存状態によって変わる点を確認した。Service Manual から [モデレーター付き利用テスト](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing) にたどった。
- 研究の検索役は Molich を起点に、[CUE-8 の実施主体](https://www.dialogdesign.dk/cue-8/) の公開一覧、著者版、実施指示書へ進んだ。旧出版社の掲載先は取得できず、著者公開版を使った。評価終了点、チーム間解釈の差、順序を通常の QA と実利用者研究にどう適用するか確認した。改修前後で同一条件を使った別研究は引用まで確認したが、一次本文を確認できた範囲で判断した。
- ローカル保存には imozuru の取得ツールを利用した。GOV-V はページ内の別パターン名を取得ツールが404とみなした。直接取得し HTTP 200、記事タイトル、該当見出し、本文量で再確認した。取得結果は [fetch-log.jsonl](fetch-log.jsonl)。

5論点すべてに一次資料が付き、既定経路・分岐の採り方、技術的な受入と利用者研究の適用条件、完了地点の違いを確認できたため終了。実サービスの同時実行・本番データ・参加者の達成率を裏付ける証拠は今回の評価対象外。[原典マップ](map.md)
