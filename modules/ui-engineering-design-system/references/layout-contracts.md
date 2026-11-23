# リフロー・入力・実効クリック領域の契約

対象: C-UI-008 / C-UI-009。いずれも実ブラウザ・ATの確認を残すHOLD候補である。入力モデルのPASSは画面の合格ではない。

## 1. 情報と操作を保持して狭幅へ移す

1. 先に必要な情報・操作をIDで列挙する。A/Bから渡された優先度・前後関係・業務状態を入力にし、Cの都合で機能を削除しない。
2. 縦に読む内容は幅320 CSS px相当、横に読む内容は高さ256 CSS px相当で確認する。1280幅から400%などは設定例であり、実際のlayout viewportを記録する。物理解像度、スクリーンショット幅、zoom表示だけで境界到達を決めない。
3. 各IDについて境界状態の到達先を記録する。折り畳みや別位置への移動も可能だが、実際の到達操作と値・意味の保持を確認する。`overflow:hidden`、省略、操作の非表示でスクロールバーが消えただけなら合格にしない。
4. 二次元配置が必要な部分ごとにregion ID、必要性、overflowの所有者、根拠を記録する。表という名前だけで本文・操作・各セルまで免除しない。局所スクロール領域は有用な実装案だが一律必須ではない。例外部分だけがページoverflowを生む公式例もあるため、`scrollWidth > clientWidth` 単独で不合格にしない。
5. DOM順・視覚順・実際のTab/Shift+Tab順・ATの読み順を別々に観察し、課題上必要な前後関係を確認する。`reading-flow`等を含む対応差があるため、常にDOM順になると仮定しない。全配列の一致も一律要求しない。
6. `pointer` / `hover` / `any-pointer` / `any-hover`の能力queryと、実際に使用したmouse・touch・pen・keyboardを区別する。fine/coarseの両方に合致し得る。fineやhoverから他の入力経路の不在・小さいtargetの例外を推定しない。

規範と解説: [WCAG 2.2](https://www.w3.org/TR/WCAG22/)、[Reflow解説](https://www.w3.org/WAI/WCAG22/Understanding/reflow)。overflow・順序・入力機器については round-03 の出典台帳 C-S035〜C-S044 を参照する。最新機能の対応状況は対象環境で確認する。

## 2. サイズとspacingを別々に判断する

[Target Size (Minimum)解説](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)のサイズ判断では、軸平行の24×24 CSS px正方形が実効pointer-action領域内に収まることを確認する。直径24の円はbboxが24×24でも、このサイズ条件を満たした証明にはならない。spacing等の別条件は検討できる。

`getBoundingClientRect()`はborder boxを囲む矩形であり、hit areaと同一とは限らない。clip、変形、重なり、改行断片、子要素や関連controlのactivationを確認する。`elementFromPoint`の点検査だけで全面の有効性を証明しない。

本検査器が計算するのは、**同一状態・同一viewport CSS px座標系の、実効領域と一致すると入力で申告された充填軸平行矩形**だけである。未対応形状・誤差・遮蔽・重なりはHOLD。非矩形であること自体をWCAG不適合としない。

1. `width >= 24 and height >= 24`ならサイズ関係をPASSとし、その対象自身に追加spacingを要求しない。
2. いずれかが24未満なら、最小外接矩形中心に半径12の円を置く。23.999を丸めず、観測誤差を独自の規範許容差にしない。
3. 不足対象どうしは中心距離二乗 `< 576` を衝突とする。
4. 各不足対象の円と**他のすべての実対象**も比較する。矩形へ最短の横距離dx・縦距離dyから `dx² + dy² < 144` を衝突とする。相手が不足対象でも省かない。幅広で薄い対象は中心が遠くても円へ侵入する。
5. 等号での接触許容は公式図5・図10から導いたこのモデルの推論であり、規範本文が不等式を定義したとは書かない。
6. 他対象の例外を理由に障害物一覧から削除しない。新しいmenu/dialogが開いたらその状態を再評価する。

## 3. 例外は根拠と適用先を残す

| 例外 | 必要な確認 | 不足・誤用の例 |
| --- | --- | --- |
| 同等control | 同じページで同じ機能を持ち、基準を満たす対象 | 別ページ、機能が違う、自己・循環参照 |
| inline | 文中、または非対象文字の行高による制約 | `display:inline`だけ |
| UA決定 | UAが寸法を決め、作者が変更していない | nativeタグだけ、作者が縮小 |
| essential | 情報・機能に不可欠な提示、または法的要求 | 密度や見た目の好み |

検査器は文章・証拠ファイルの内容を評価しない。条件が整って見える例外でも `HOLD_EXCEPTION_REVIEW` とする。宣言で明確に矛盾する場合はその申告を承認しない。既にサイズまたはspacing関係を満たす対象では例外は不要と記録するが、不正な条件形式は拒否する。

## 4. 入力モデルの実行と読み方

```sh
python3 modules/ui-engineering-design-system/checks/layout.py modules/ui-engineering-design-system/examples/booking-reflow-model.json
python3 modules/ui-engineering-design-system/checks/layout.py modules/ui-engineering-design-system/examples/toolbar-target-model.json
```

入力schemaは `C-layout-model/1`。厳密なキー・型、重複IDとJSONキー、有限数値を検査する。座標は絶対値1e9以下、小数点以下18桁以内、各一覧500件以下、CLI入力2 MiB以下というローカル上限を設ける。これはWCAG要件ではない。数値はDecimalから有理数へ変換し、計算にepsilonを加えない。

| 終了値 / status | 意味 |
| --- | --- |
| 0 / MODEL_PASS | 入力された限定モデルの条件を満たした |
| 1 / MODEL_FAIL | 入力モデルに既知の保持欠落、非例外リフロー不成立、spacing衝突がある |
| 2 / INPUT_ERROR | 形式・型・上限・座標系等の入力契約を満たさない |
| 3 / MODEL_HOLD | 必要観測・周辺一覧・形状・例外判断等が未確定 |

`MODEL_FAIL`は入力に明示された欠陥を優先し、同時にHOLDの個別行も残す。たとえば `availability=missing` は証拠参照が空でも入力上の欠落として返し、証拠の有無を別欄にする。UA例外も作者によるサイズ変更やUA非決定が一方でも明示されれば申告条件不成立とする。`evidence.kind`に実観測と書かれていても、証拠は認証されない。`ui_status=HOLD`、`wcag_conformance=NOT_ASSESSED`を返す。reflowモデルでは正確な境界値の観測をローカルに要求し、319や321から320での挙動を補間しない。CLIはUnicodeをJSONのASCII escapeで安全に出力し、Decimalで表現できない巨大指数は構造化した入力エラーにする。文字列の表示品質をこの正規化から認証しない。

例の座標と観測は人が作ったsynthetic入力であり、HTMLから測定していない。[観測プロトコル](../checks/layout-observation-protocol.md)で必要な観測を追加してから、Dへ実画面の採否を渡す。

## 適用外と次の検証

文字200%拡大、focus遮蔽、keyboard操作、AT発話、入力切替、実hit geometry、既存ページ全体、ブラウザ間差はこのプログラムでは未検査。2.4.11の完全遮蔽とより厳しい部分遮蔽条件を混同しない。計算が通っても、これらを合格にしない。
