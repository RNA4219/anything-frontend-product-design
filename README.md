# Anything Frontend Product Design

フロントエンドを作るときに、「利用者が何を選び、どう操作し、何をもって完了とするか」を決めるスキルです。たとえば画像を書き出す画面なら、保存ボタンの見た目に加えて、ダウンロードした画像が直前のプレビューと一致するところまで確かめます。

## 動く作例『水葬線』

**[『水葬線』を開く](https://rna4219.github.io/anything-frontend-product-design/)** · [単体HTMLの保存へ](https://rna4219.github.io/anything-frontend-product-design/#download) · [序章の台本を読む](examples/suisosen/prologue.ks)

[![『水葬線』。湖に沈んだ駅を背に、赤い襟巻きの水守澪が振り返る。左に作品名と「序章をプレイ」のボタンがある。](assets/suisosen-preview.webp)](https://rna4219.github.io/anything-frontend-product-design/)

湖底の駅に、十二年前に亡くした妹から電話がかかってくる。架空の短編伝奇ADVの作品サイトです。「序章をプレイ」を開き、全文を表示して台詞を送ると、赤い灯を振るか、受話器を握るかを選べます。どちらの結末からも選択の直前に戻れます。台詞と作品紹介は差し替え用の仮稿です。

### 序章の遊び方

| したいこと | 操作 |
| --- | --- |
| 自分の速さで読む | 本文をクリック／タップ。表示途中の1回目はその台詞の全文表示、表示後の1回で次へ進む。キーボードでは Enter・Space・→ で送り、← で一つ戻る。分岐では Tab と Enter で選ぶ。 |
| 読み返す | 「履歴」で今回通った台詞を確認。「既読スキップ」は、次が未読のときと選択肢で止まる。「オート」も選択肢で待つ。 |
| 選択の前に保存する | 「セーブ・ロード」で3つの栞から保存先を選ぶ。ロードすると台詞と選択履歴が戻る。同じブラウザーで再訪すると、作品ページから直前の場面を再開できる。 |
| オフラインで遊ぶ | 作品情報の「単体HTMLを保存」で `suisosen.html` を保存して開く。3枚の絵とプレイヤーを収録。保存先のブラウザーやファイルの場所によって、栞の保管先は変わる。 |

### 4つのスキルを1つずつ、2周使った記録

| 順番 | 1周目で作ったもの | 2周目に実画面で変えたこと |
| --- | --- | --- |
| 1. [Product Design](SKILL.md) | 「初見で序章を起動し、選んだ結末を読める」を完了条件にした。台詞送り、分岐、終幕、栞からの復帰をつないだ。 | Enterで分岐へ進むとフォーカスが本文の外に抜けた。最初の選択肢に移し、履歴は直近の発言が見える位置から開くようにした。 |
| 2. [Art Direction](https://github.com/RNA4219/anything-frontend-art-direction) | 『魔法使いの夜』PC版の物語紹介で、雨の街と赤い傘が一枚に収まる構図を観察。『水葬線』では青い湖面を題名の余白に取り、赤い襟巻きを人物の目印にした。DGXのMOSS-Imageで主人公、水没駅、業務電話の3枚を生成した。[参照した公式画面](https://www.typemoon.com/products/mahoyo/story.html) · [MOSS-Image](https://openmoss.ai/MOSS-Image/) | 390px幅で片目が画面外に切れた。スマートフォンでは画像の表示位置を右へ寄せ、両目を入れた。画面幅に合わせて駅の風景も個別に切り取った。[390px幅の実画面](assets/suisosen-mobile.webp) |
| 3. [Motion Atlas](https://github.com/RNA4219/motion-atlas) | タイトルに[Soft enter](https://github.com/RNA4219/motion-atlas/blob/8cff76041b06a30d7f4b4b9f79979b8e30512f60/src/cinema.js)を応用。台詞の途中で押すと、その台詞を一度で表示する。 | 背景が変わるときだけ、直前の絵を340msで透過する2層構成にした。既読スキップ時は即時切替。端末の「動きを減らす」設定では、タイトル・背景・文字送りをすべて即時表示にした。 |
| 4. [unslop](https://github.com/heydamir/unslop) | 操作の主役を「序章をプレイ」に絞り、下端の細い路線と終電時刻をこの作品の地紋にした。 | 外部リンクに見える矢印を取り、入口を切符の切り取り線で仕上げた。スマートフォンの読書画面を全面に広げ、6個の補助操作を2段にそろえた。 |

Chromeで文字を即時表示にした場合、初見から片方の終幕まで **7操作**（起動1・台詞送り4・選択1・台詞送り1）。390 × 844 CSS pxでは起動ボタンの上端が566px、高さが52px、直前の紹介文との余白が18px。320px幅でも横スクロールは0pxだった。マウス・キーボードとタッチエミュレーションで操作し、保存したHTMLは通信を無効にして終幕まで確認した。

### 台本を差し替える

[序章の台本](examples/suisosen/prologue.ks)で、各ラベルの本文、話者、背景、選択先を編集します。台詞末尾の `[p]` がページ送り、`[link]` が分岐です。ラベル名はセーブ位置にも使います。変更後はリポジトリのルートで `python examples/suisosen/sync_scenario.py` を実行すると[配布HTML](docs/index.html)に反映されます。`--check` で同期状態だけを確認できます。プレイヤーは吉里吉里／KAGのページ待ち・リンク・栞を参照したブラウザー実装で、この台本用のタグを解釈します。[KAG3 タグリファレンス](https://krkrz.github.io/krkr2doc/kag3doc/contents/Tags.html)

同じ手順で作例を依頼するときは、利用者の最初の操作と、最後に画面で確認できる結果を指定します。

> 架空の伝奇ADVの公式サイトと、2通りの結末まで読める序章を単体HTMLで作ってください。Product Design、Art Direction、Motion Atlas、unslopの順に1つずつ使い、2周してください。1周目は「起動 → 台詞送り → 分岐 → 終幕」を通し、2周目は390px幅の実画面とキーボードで見つけた問題を直してください。画像はDGXのMOSS-Imageで生成し、紹介文と台詞は仮稿として分離してください。



## 自分のプロダクトで使う

[スキルの入口](SKILL.md)から相談に合う担当を選びます。製品を点検するときは、用件ごとに成功条件を先に決め、操作回数、要素間の余白、画面内の情報密度、実際に得られた結果を記録します。[製品評価チェックリスト](references/product-checklist.md) · [担当間の受け渡し](references/handoff.md)

| 担当 | 設計するもの | 担当ディレクトリ |
| --- | --- | --- |
| A | 利用目的、情報の分類と名前、見つけ方 | `modules/product-information-architecture/` |
| B | 操作手順、状態遷移、中断・失敗からの復帰 | `modules/interaction-ux-flow/` |
| C | 実装時の部品選択、部品の契約、デザインシステム | `modules/ui-engineering-design-system/` |
| D | 検証の設計、観察結果、リリース判断 | `modules/design-qa-evaluation/` |

## 設計判断に使える記録

[実サイトの用件別の索引](references/site-comparisons.md)から、操作回数・余白・情報密度を参照できます。[29ブランド・施設の実画面](research/product-journeys/walkthrough/README.md)と[新規12ブランド・施設を含む追加観察](research/product-journeys/expansion/README.md)を収録しています。人の探索時間や達成率については[利用者を観察した研究](research/product-journeys/human-studies/README.md)を参照してください。

[調査資料の置き方](research/README.md)、[検証の実行方法](tests/README.md)、[実行・評価の証跡](evidence/README.md)。

## ライセンス

このリポジトリのコードと作例は[MIT License](LICENSE)で配布します。参照したunslopの作者はDamir Sokolovskyで、スキルのライセンスは[CC BY 4.0](https://github.com/heydamir/unslop/blob/main/LICENSE)です。作例は端末の書体を利用します。第三者の原典には各資料の条件が適用されます。
