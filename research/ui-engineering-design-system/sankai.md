# 担当間の受け渡しから取り出したUI実装手順

## 分解・理解・溶解

原文は [担当間の受け渡し](../../references/handoff.md) の `3d02174`、参照位置は行番号。利用課題と受入条件には短く安定したIDを付ける。課題を一文で記し、役割、きっかけ、対象、開始時の事実、成功時に確認できる事実を添える。表・JSONなどの形式と、予約変更のIDの例は適用先に合わせて選べる（L3、L14）。

| 取り出した指示本文 | 意味・依存先 | 維持条件と選べる範囲 |
| --- | --- | --- |
| **U01** 利用課題ID、状態ID、利用者とシステムの操作、遷移条件、保持・更新するデータ、受入条件IDを受け取り、操作と状態を部品に割り当てる。単独で使う場合は、必要な情報を既存仕様、実装、依頼内容から取る。 | Bの遷移とデータの扱いを引き継ぎ、部品として実装できる状態にする（L8、L14）。 | 受入条件との対応を保つ。部品の種類と入出力APIは適用時に決める。 |
| **U02** 利用課題ID、部品ID、状態と操作の対応、入力方法、表示・通知、試作を動かす方法を、挙動を再現する担当へ渡す。 | 契約だけで到達できない画面や状態も、起動方法と入力方法で再現できる（L9）。 | 受け手が同じ状態へ到達できる情報を保つ。試作技術と起動方法の具体形、評価対象の端末や支援技術は適用時に決める。 |
| **U03** 案を比べる場合は課題・データ・成功条件をそろえる。既存画面、競合、再試行、戻る操作、表示幅から、機能に影響する条件を試し、実際に操作した範囲を記録する。 | Dの観察を後から再現し、同じ条件で修正前後を比べられる（L10、L12）。 | 比較時の共通条件は維持し、試す範囲は対象機能への影響で選ぶ。既存版の有無と適用環境は案件ごとに確かめる。 |

Aの分類・ラベル検証、Bの遷移設計、Dの評価判定はそれぞれの担当資料に戻る。予約変更で使う排他選択や通信の取り扱い、色の用途名と具体値は適用先の判断で、下記の原典と照合した。

## 適用時の原典照合

Art Direction は `f5df625dbc577d6a3ca28e13ef09e39b135b4a6f` を参照した。

| 適用箇所 | 照合した条件と今回の判断 |
| --- | --- |
| 部品の再利用と共有 | 既存部品・合成を選ぶ判断を、GOV.UK の有用性・独自性と既存利用面の更新リスクに照合した。予約変更の合成は単一用途の作例として扱う。共通化を判断するときは複数用途の根拠と、互換性・維持担当を確認する。 [Contribution criteria](https://design-system.service.gov.uk/community/contribution-criteria/)・[Extending and modifying components](https://design-system.service.gov.uk/get-started/extending-and-modifying-components/) |
| 入力とフォーカス | Art Directionの G2-01・G2-07・G2-08、E4-10・E5-02・E5-09 と重なる。短い排他選択にはラベルと凡例があるHTMLのラジオ群を使う。競合後にラジオを一つだけ描画する構成は、無効候補と理由を残すか、単一候補から進む明示操作に変える。領域切替で消える起点には次のフォーカス先を決め、進捗通知には持続する状態と読み上げに渡る変化を確認する。 [G](https://github.com/RNA4219/anything-frontend-art-direction/blob/f5df625/references/g-state-forms.md)・[E](https://github.com/RNA4219/anything-frontend-art-direction/blob/f5df625/references/e-accessibility.md)・[WHATWG HTML §4.10.5.1.16](https://html.spec.whatwg.org/multipage/input.html#radio-button-state-(type=radio))・[WCAG 2.2](https://www.w3.org/TR/2024/REC-WCAG22-20241212/)・[ARIA22](https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA22) |
| 状態の保持と復旧 | 予約の競合と通信結果不明を分け、確定値、候補、操作の同一性を照合する。Stripeの資料ではAPI v1とv2で再送時の扱いが異なる。再送条件・キーの寿命・状態照合の手段は対象APIが決める。 [Advanced error handling の Content errors、Network errors、Server errors、POST requests](https://docs.stripe.com/error-low-level) |
| 視覚方針の適用 | I-01・I-02 の変数と面・文字の対、構成資料の「広幅から狭幅へ組み直す」「動いた後も状態を残す」に対応する。Art Directionに必要な情報の優先度と操作を渡し、決まった色・書体・構図を部品に接続する。用途名と値を対応させ、変更による依存箇所、フォーカス、状態の持続表示、狭幅の情報と操作を確かめる。 [I](https://github.com/RNA4219/anything-frontend-art-direction/blob/f5df625/references/i-components.md)・[構成](https://github.com/RNA4219/anything-frontend-art-direction/blob/f5df625/references/visual-composition.md)・[USWDS Theme color tokens](https://designsystem.digital.gov/design-tokens/color/theme-tokens/#customizing-theme-color-tokens) |

## 引用の再検証

外部原典の版・取得日は [原典台帳](sources.md) を参照する。
