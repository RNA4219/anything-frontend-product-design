# 評価手法を選ぶ

| 知りたいこと | 方法と採用条件 | 確認できる範囲 |
| --- | --- | --- |
| 要求された表示や状態を実装が再現できるか | 期待値と操作が定義でき、テストデータを初期化できる場合に自動確認する。状態変更では表示と永続化の観測をそれぞれ置く。 | 実行した版、入力、経路、環境での一致。 |
| 手順の途中で、情報や次にできる操作を画面から判断できるか | キーボード・画面幅・支援技術など影響する環境を選び、人が対象操作を最後までたどる。評価者同士の影響が問題になる場合は所見を集約前に別々に取る。 | 評価者がその場で確認した挙動と指摘。評価者の推測には推測と書く。 |
| アクセシビリティの達成範囲を調べたい | 適用する WCAG 版・適合レベル・対象・環境・選択手順を決める。選んだ完全なプロセスについて既定経路と、よく使われ完了に重要な分岐を特定し、それぞれのステップを確認する。ステータス通知は条件に応じて支援技術まで確認する。 | 適合の主張には、対象全体の適合条件と適切な評価手続きが必要。〔EM〕〔WCAG〕 |
| 利用者の達成、誤達成、時間を比較したい | 対象層から参加者を募り、具体的で中立な課題と正解基準を準備する。同一人物が複数案を使う場合は順序の偏りを扱う。持ち越しが強ければ別の参加者群を検討する。 | 対象者・課題・収集条件に依存する。合成データの操作や評価者の判断から達成率を推定しない。〔GOV-B〕〔CUE〕〔ORDER〕 |

## 失敗や復帰を確認する場面

- データを訂正すれば進める場合は、エラーの対象、保持された入力、訂正できる場所、訂正後の完了を確認する。サービス側で原因を取り除く必要がある場合は、利用者が訂正できる場合と分けて設計判断を行う。〔GOV-V〕〔WCAG〕
- 同じ異常でも、送信前の拒否と、確定後に応答だけ失った場合では観測すべき状態が違う。前者では元データと次候補、後者では最新状態の把握と副作用の一意性を確認する。保存の有無によって次の行動を変える例は GOV.UK のサービス障害画面にある。〔GOV-E〕
- 同じ録画でも、完了の読み取りは評価者間で割れうる。比較の前に、何が表示されたら達成か、最後までたどらなかった操作をどう扱うかを定め、所見の違いは元の記録と照合する。〔CUE〕〔EE〕

## 参照元

〔EM〕W3C, WCAG-EM 2.0 §4.3.3・§4.4.2・§4.5.1。適合評価向けの経路・記録の方法を受入設計にも応用した。 [2026年7月23日 Group Note](https://www.w3.org/TR/2026/NOTE-wcag-em-2-20260723/)

〔WCAG〕W3C, WCAG 2.2 の 3.3.1、3.3.3、4.1.3 と適合要件「Complete processes」。 [2024年12月12日 Recommendation](https://www.w3.org/TR/2024/REC-WCAG22-20241212/)

〔GOV-V〕GOV.UK Design System のフォーム検証。入力の訂正に関する画面と運用の例。 [Recover from validation errors](https://design-system.service.gov.uk/patterns/validation/)

〔GOV-E〕GOV.UK Design System のサービス障害画面。入力が保存された場合とされなかった場合の実例と、調査範囲。 [Problem with the service pages](https://design-system.service.gov.uk/patterns/problem-with-the-service-pages/)

〔GOV-B〕GOV.UK Service Manual の課題の選択、参加者、成功・誤達成、再計測。 [Usability benchmarking a website or whole service](https://www.gov.uk/service-manual/measuring-success/usability-benchmarking-a-website-or-whole-service)

〔CUE〕Molich、Sharon、Kirakowski（2010）による同一レンタカーサイトと共通課題の比較。予約確定前に停止する実験手順のため、確定結果は測定対象外。 [CUE-8、Method と Measuring Time-on-task](https://www.dialogdesign.dk/tekster/cue8/CUE-8_JUS.pdf)

〔EE〕Hertzum、Molich、Jacobsen（2014）による利用テスト分析の評価者差。 [著者プレプリント §4.4、§5.3–5.4](https://mortenhertzum.dk/publ/BIT2014.pdf)

〔ORDER〕MacKenzie（2013）の順序効果と相殺。 [Within-subjects vs. Between-subjects Designs](https://www.yorku.ca/mack/RN-Counterbalancing.html)

原典の版・取得・Art Direction との担当境界は [調査マップ](../../../research/design-qa-evaluation/map.md) を参照。
