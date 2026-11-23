# 実例を設計や評価に使う

利用者が何を達成し、何を確認できれば成功かを一文で決め、用件・端末幅・入力方法・終点が近い事例を選ぶ。
この文書の一つ上にあるスキルのルートで `python scripts/find_journeys.py --task reset --mode mobile --status confirmed --limit 1` を実行し、用途に合わせて課題と端末を変える。
課題キーは `mug` が商品検索、`repair` が誤記の訂正、`shirt` が価格とサイズ、`friday` が金曜の閉館時刻、`store` が店舗の住所と営業時間、`reset` がパスワード再設定、`returns` が返品期限と条件を指す。

`find_journeys.py` は同じ観察IDの最新巡回を返すので、`status`・`actions`・入口と終点の測定値・`finding` を確認し、`source` からその観察の根拠と終点をたどる。
操作回数だけなら `--view actions`、位置・余白・文字の密度や測定済みの要素間距離なら `--view layout` を使い、記録のない距離は推定せずに `source` の個別記録も確かめる。
クリック・タップとスクロールの扱いは [検証前の操作数の評価案 D-IU-214](../registry/D/skills/D-IU-214.json)、文字の矩形面積や中央の平坦な帯の定義と限界は [余白の測定](../research/product-journeys/spacing/README.md) で確認する。

他社の操作数や余白を合格基準にせず、未到達を自分の製品の不具合と決めつけずに、選んだ実サイトと自分の画面、または条件をそろえた2案の比較を明記し、その差についての仮説を自分の製品で確かめる。
自動操作から人の所要時間や達成率は求められないため、迷いや達成の評価には参加者・課題・端末を記した [人対象の研究](../research/product-journeys/human-studies/README.md) を参照する。
