---
name: anything-frontend-product-design
license: MIT
description: Webプロダクトの機能、情報構造、操作フロー、再利用できるUI部品、リリースの受入条件を設計・実装・評価する。利用者の目的から、正常時と失敗時の振る舞いを決め、実画面と観察結果で判断する。
---

# Anything Frontend Product Design

利用者、目標、対象のデータと制約、目標を達成したと分かる結果を最初に確認する。既存画面がある場合は、代表的な利用課題を現行版で実行し、どこで判断や操作が止まるかを観察する。情報が足りなければ、その判断に影響する仮定と確認方法を書く。

| 今回の判断 | 読む担当Skill |
| --- | --- |
| 何を提供し、どこから見つけられるようにするか | `modules/product-information-architecture/SKILL.md` |
| 開始から完了までに何が変わり、異常時にどう戻れるか | `modules/interaction-ux-flow/SKILL.md` |
| 既存部品をどう再利用し、状態や操作をどう実装するか | `modules/ui-engineering-design-system/SKILL.md` |
| 何を再現し、どの証拠でリリース判断するか | `modules/design-qa-evaluation/SKILL.md` |

担当をまたぐ場合は [受け渡しの約束](references/handoff.md) に従う。既存の仕様や実装に必要な情報があればその情報を使い、今回必要な判断から進める。担当ファイルがまだないチェックアウトでは、該当する担当ブランチを探す。

選択肢が複数あるときは、同じ内容・課題・成功条件を使い、案ごとの差と失敗条件を観察する。実装を伴う場合は利用目的を最後まで達成できるかを確かめる。使った入力、アプリの版、観察結果、確認できなかった条件を残す。

課題に合う設計案を探すときは、[分野別の設計ルールと出典](research/design-evidence/README.md)から、適用条件と確かめ方を選ぶ。

視覚表現も扱う依頼では、主要な情報と操作、機能上の制約を Art Direction に渡す。表現を適用した実画面で、情報の発見、操作、完了の確認をもう一度試す。 [Anything Frontend Art Direction](https://github.com/RNA4219/anything-frontend-art-direction)
