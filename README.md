# Anything Frontend Product Design

利用者が目的を達成できるよう、機能と情報の構造を決め、操作を実装し、結果を確かめるためのSkillです。同じ課題と入力で試作を動かし、利用者が何を見つけ、どう判断し、どの条件で完了できたかを採用理由にします。

[SKILL.md](SKILL.md) から相談に合う担当を選べます。複数の担当をつなぐ場合は、[受け渡しの約束](references/handoff.md) と [共通の試作課題](tests/fixtures/booking-change.md) を参照してください。

| 担当 | 設計するもの | 担当ディレクトリ |
| --- | --- | --- |
| A | 利用目的、情報の分類と名前、見つけ方 | `modules/product-information-architecture/` |
| B | 操作手順、状態遷移、中断・失敗からの復帰 | `modules/interaction-ux-flow/` |
| C | 実装時の部品選択、部品の契約、デザインシステム | `modules/ui-engineering-design-system/` |
| D | 検証の設計、観察結果、リリース判断 | `modules/design-qa-evaluation/` |

配色・書体・余白・構図の表現は [Anything Frontend Art Direction](https://github.com/RNA4219/anything-frontend-art-direction) が担当します。両方を使う場合は、利用者に伝える情報と操作の目的を共有し、表現が決まった画面を同じ利用課題で再確認します。

[29ブランド・施設を実画面で再訪した記録](research/product-journeys/walkthrough/README.md)では、入口と終点の余白・情報密度を操作経路と一緒に比較できます。[初回のクリック・タップ実測](research/product-journeys/README.md)、[利用者を観察した研究](research/product-journeys/human-studies/README.md)、[入口画面の余白と情報密度](research/product-journeys/spacing/README.md)も参照できます。

[調査資料の置き方](research/README.md)、[検証の実行方法](tests/README.md)、[実行・評価の証跡](evidence/README.md)。

このリポジトリの成果物は [MIT License](LICENSE) で配布します。収録する第三者の原典には、各原典に明記した条件が適用されます。
