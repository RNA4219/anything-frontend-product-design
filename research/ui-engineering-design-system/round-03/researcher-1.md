# Round 03 Researcher 1 — Reflow と対象領域の原典調査

**結論：狭い画面と対象サイズは、宣言された幅・外接矩形・ページのスクロールバーだけでは適合判定できない。** 実効対象領域と情報・機能の保持を観測し、純粋な幾何検査はその入力に対する関係だけを返す。実ブラウザ・支援技術の結果は HOLD。本調査は研究のみで、実装・テスト・ブラウザ操作は未実行。

固定評価基準は `campaigns/C/rounds/03/plan.json`。変更していない。詳細な出典、節、数式、反例、検索履歴は隣の `researcher-1.json` に収録した。

## 1. 規範・解説・プロジェクト方針を分ける

|区分|根拠と扱い|
|---|---|
|規範|[WCAG 2.2](https://www.w3.org/TR/WCAG22/) の SC 1.4.10、2.5.8。既存 round-01 の WCAG22 を再利用し、今回必要な節のみ reader で補った。|
|公式解説|[Understanding Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow)、[Understanding Target Size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)。説明・図例は informative。|
|推論|公式図例から幾何の境界接触を許容する比較式を導く。式自体が規範に記載されているとは言わない。|
|ローカル方針|対応形状を「実効領域が確認された軸平行の充填矩形」に限定し、不明な形状・観測を HOLD にする。WCAG 全体の判定器とはしない。|

取得制約：`fetch.py` は新規 URL へ1回実行し、DNS の一時的名前解決失敗。再試行・保護解除なし。reader は部分断片で `full_original=false`。WCAG 本体の reader は rewritten summary と明記されていたため、原文完全取得や逐語一致を主張しない。公開ファイルは要約・判断・出典のみ、生 reader は private に置いた。

## 2. Reflow の実装契約に必要な点

- 縦スクロールなら幅 **320 CSS px 相当**、横スクロールなら高さ **256 CSS px 相当**。1280 幅から400%は前者に対応する設定例であり、画面解像度やスクリーンショット幅をそのまま入力にしない。[WCAG SC 1.4.10](https://www.w3.org/TR/WCAG22/#reflow)
- その境界で情報・機能を失わないことが必要。メニューへの格納や再配置は、利用者が内容へ到達できれば許容される。唯一の送信操作や必要な説明を消して overflow をなくす方法は、保持条件を満たさない。[Understanding の Reflowing websites and web applications](https://www.w3.org/WAI/WCAG22/Understanding/reflow)
- 二次元配置の例外は、その配置が利用・意味に必要な部分に限る。表に隣接する文章、ページ送り、操作まで自動的に免除しない。セル自身も通常は Reflow が必要。[Understanding の scope / tabular data](https://www.w3.org/WAI/WCAG22/Understanding/reflow)
- **ページに横スクロールがあれば即 FAIL、とはできない。** 例外動画だけがはみ出し、非例外部分が320内で読める公式適合例がある。局所スクロールへの封じ込めは有用な推奨で、すべての場合に課す規範ではない。[Understanding 図11、L113–119](https://www.w3.org/WAI/WCAG22/Understanding/reflow)

推奨入力は、実測 viewport・書字/スクロール方向・内容領域一覧・必要情報/操作の保持先・例外対象IDと理由・証拠種別。単一の `scrollWidth <= clientWidth` では保持も例外範囲も確認できない。

200%文字拡大、意味のある読み順、フォーカスが作者作成内容で完全に隠れないことは別の検査として残す。320幅へ収まっただけで、SC 1.4.4 / 1.3.2 / 2.4.11 も満たしたとはしない。[WCAG](https://www.w3.org/TR/WCAG22/)・[Resize Text](https://www.w3.org/WAI/WCAG22/Understanding/resize-text)

## 3. 対象サイズ・間隔を厳密に分ける

SC 2.5.8 の最小値は24×24 CSS px。現行の公式解説は、**軸と平行な24×24の正方形が実際の対象内部へ完全に収まる**ことをサイズの判定として説明する。直径24の円は外接矩形24×24でもサイズ条件を満たさない。丸く見える CSS 要素の実クリック領域が円か矩形かは別途観測する。[Understanding Size requirement、図1–3](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)

サイズ不足時の spacing は、対象の最小外接矩形の中心へ直径24の円を置き、その円が他の実対象または他の不足対象の円と重ならないこと。非凸形では中心が対象外にあってもこの中心を使う。[Understanding Spacing](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)

|純粋幾何モデル|比較式|境界の根拠|
|---|---|---|
|矩形のサイズ|w >= 24 かつ h >= 24|規範の「少なくとも」と充填正方形の説明|
|不足対象どうしの円|中心距離の二乗 < 576 なら重なり|20×20、間隔4の適合例（図5）より、中心距離24の接触は許容|
|不足対象の円と他の矩形|中心から矩形までの最短距離の二乗 < 144 なら重なり|16×16と大対象の間隔4の適合例（図10）より、距離12の接触は許容|

円どうしだけでは足りない。幅100・高さ16の対象の端に別対象が近い場合、中心どうしが遠くても小対象の円が広い対象へ食い込む。すべての不足対象について、他の実領域との比較も行う。数値許容差は原典から得ていない。23.999を24へ丸めたり、独自の0.5px許容をWCAGとして追加しない。

別機能の対象との重なりはサイズ測定から除く。同じ動作・同じページを開く場合の例外は定義にあるが、DOMの矩形だけでその意味まで証明できない。形状、clip、overlap、transform、実hit areaが不明なら HOLD。[Understanding Key Terms: target](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)

## 4. 五つの例外に必要な証拠

|例外|必要な確認|不十分な申告|
|---|---|---|
|Spacing|前記の円と実領域の比較|marginの宣言だけ|
|Equivalent|同じページの別コントロールが同じ機能を持ち、この基準を満たす|別ページ、別機能、互いを参照する未証明の免除|
|Inline|文中、または非対象テキストのline-heightにサイズが制約される|display:inline、リンク一覧、文字ラベルというだけ|
|User Agent Control|UAがサイズを決定し、作者が変更していない|native要素というだけ|
|Essential|特定提示が情報に不可欠、または伝える情報に対する法的要求|高密度を好む、実装を変えたくない、というだけ|

条件は [SC 2.5.8](https://www.w3.org/TR/WCAG22/#target-size-minimum) に由来する。例外を Boolean で置くだけでは、その適用を確認したことにならない。操作で新しく出現したメニューやダイアログの対象も評価する。

## 5. 反例候補と証拠ラベル

**以下はすべて未実行。** JSONに座標付き入力を保存した。

1. 24×24 と 23.999×24 の境界。
2. 20×20 の2対象を x=0 / 24 に置く接触ケースと、x=23.999 の侵入ケース。
3. 16×16 対象と大対象の間隔4 / 3.999。
4. 幅100・高さ16の対象を使い、円どうしは離れていても円と実対象が重なるケース。
5. 直径24円を bbox=24×24 として誤ってサイズPASSにするケース。
6. 24×24要素が別機能に部分遮蔽され、元の矩形を実効領域として使ってしまうケース。
7. 唯一の操作を消して overflow がなくなるケース。
8. 正当な局所表と、隣の文章へ例外を拡大するケース。
9. 例外動画がページoverflowを生むが文章は正しくreflowするケース。
10. 全入力が合成矩形でも、結果を browser-observed と誤表示するケース。

証拠は `synthetic_geometry`、`supplied_measurement_unverified`、`browser_observed`、`assistive_technology_observed` を区別する。純粋検査で分かるのは、入力の形式・有限値・対応形状と幾何関係。実際の折返し、情報保持、到達可能性、hit testing、キーボード/支援技術の動作は実観測が要る。

## 6. 既存ガイダンスとの重複・探索監査

Art Directionの E-02 / E-03 / E-07 は既にReflow境界、フォーカス遮蔽、小対象の例外を持つ。G4-23 / G4-24 / G4-29 / G4-34 は入力の意味、ラベル、作動を扱い、C2-02 / C2-11 / C3-01 はエラーの位置・入力保持・証拠記録を扱う。D2-01 / D2-10 / D2-11 はポインターとパン/ズームを扱う。今回の追加候補は、これらを観測入力・境界値・HOLD条件へ落とす部分。既知事実を新原則として数えない。

初期検索はW3C限定の2 queryを1回のbatchで実行。toolが返した全2 hitを記録し、両方開いた。個別queryとhitの対応、検索エンジン内部の全ヒット数は非公開なので不明。Understanding→規範本文、Reflow→Resize Textを実リンクで追跡した。全文取得0、fetch失敗1、再試行0。費用 unknown。本調査は検索readerとファイルの読み書きに限定し、実画面の観測は未実行。

未検索：WCAG issue履歴、ACTの詳細、ブラウザhit-testing仕様、デバイス別UA挙動、1.3.2/2.4.11のUnderstanding、実証研究。数値epsilonは確認範囲に見つからなかった。bounded researchとして停止し、飽和率は算出しない。
