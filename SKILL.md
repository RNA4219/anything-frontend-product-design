---
name: anything-frontend-product-design
license: MIT
description: Webプロダクトの機能・情報設計、操作フロー、UI部品の実装、リリース判定を扱う。実サイトの操作数・余白・情報密度を参照し、同じ利用課題で設計を検証する。
---

# Anything Frontend Product Design

誰が何を達成するか、対象データ・制約・成功条件を決める。
既存画面は代表課題を試して止まる箇所を記録し、不明点には仮定と確かめ方を添える。

| 用件 | 担当 |
|---|---|
| 提供する機能・情報とその入口 | [機能と情報設計](modules/product-information-architecture/SKILL.md) |
| 完了までの状態変化・中断・失敗からの回復 | [操作フロー](modules/interaction-ux-flow/SKILL.md) |
| 部品の再利用・状態・操作の実装 | [UI部品](modules/ui-engineering-design-system/SKILL.md) |
| 再現する条件・証拠・リリース判定 | [検証とリリース判定](modules/design-qa-evaluation/SKILL.md) |

定量評価は[製品評価チェックリスト](references/product-checklist.md)で課題ごとの実測から判定し、比較材料は[用件別の実例](references/site-comparisons.md)を使う。

既存仕様を使い、担当をまたぐときは[受け渡しの約束](references/handoff.md)に従い、表の担当スキルがなければこのスキルのリポジトリで該当担当のブランチを探す。
複数案は内容・課題・成功条件をそろえ、結果の差と失敗条件を比べる。
実装後は課題を最後まで試し、入力・アプリの版・観察結果・未確認の条件を残す。
根拠は各ルールの出典か[分野別の資料](research/design-evidence/README.md)から調べる。

視覚表現も扱うときは、利用課題・受入条件と画面で優先する情報や操作をそろえ、[Art Direction の手順](https://github.com/RNA4219/anything-frontend-art-direction/blob/main/SKILL.md)で意匠を決める。すでに意匠案があればそこから始める。[受け渡しの記入例](references/handoff.md#art-direction)に沿って対象の部品に反映し、同じ課題を実画面で再確認する。
