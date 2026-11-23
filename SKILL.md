---
name: anything-frontend-product-design
license: MIT
description: Webプロダクトの機能・情報設計、操作フロー、UI部品の実装、リリース判定を扱う。利用課題を決め、実画面で結果を確かめる。
---

# Anything Frontend Product Design

誰が何を達成するか、対象データと制約、成功と分かる結果を決める。既存画面では代表課題を試し、判断や操作が止まる箇所を記録する。不明点には仮定と確かめ方を添える。

今回の判断に合う担当を開き、その中で該当する項目を読む。

- [機能と情報設計](modules/product-information-architecture/SKILL.md) — 何を提供し、どの入口や名前で見つけられるようにするか。
- [操作フロー](modules/interaction-ux-flow/SKILL.md) — 完了までに何が変わり、中断や失敗からどう戻るか。
- [UI部品](modules/ui-engineering-design-system/SKILL.md) — どの部品を再利用し、状態と操作をどう実装するか。
- [検証とリリース判定](modules/design-qa-evaluation/SKILL.md) — どの条件を再現し、何を根拠に判定するか。

既存仕様を使い、担当をまたぐときは[受け渡しの約束](references/handoff.md)に従う。担当ファイルが手元にない場合は担当ブランチを探す。

複数案は内容・課題・成功条件をそろえ、結果の差と失敗条件を比べる。実装後は課題を最後まで試し、入力、アプリのバージョン、観察結果、未確認の条件を残す。根拠を調べるときは各ルールの出典か[分野別の資料](research/design-evidence/README.md)を開く。

視覚表現も扱うときは、主要な情報・操作・制約を [Art Direction](https://github.com/RNA4219/anything-frontend-art-direction) に渡す。適用後の実画面で発見から完了までを再確認する。
