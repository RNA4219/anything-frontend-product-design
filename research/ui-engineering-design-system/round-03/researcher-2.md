# Round 03 / Researcher-2 — C-002 実装反例

**結論：追加価値は5つの条件付き契約にある。必要項目の保持、局所領域、順序、入力経路、実際の押下領域を別々に観測する。** 表示幅や CSS 宣言、過去の部品テストだけでページ全体を合格にしない。以下は原典の事実から導く規則案であり、規格の追加要件とは区別する。

- 調査日：2026-11-23。費用：unknown。
- 固定計画：`campaigns/C/rounds/03/plan.json`。変更なし。
- 範囲：公式製品・ブラウザー資料から重要反例5件。数値閾値とWCAG例外は Researcher-1 の担当。
- 実行境界：ブラウザー・AT未実行。反例はすべて再現手順案。現在の不具合再現・適合証明とはしない。
- 終了理由：割当範囲で5件を選定したため。飽和とは呼ばない。
- imozuru README、実際の `skills/imozuru/SKILL.md`、fetch.py CLI 契約を確認。fetch1回はDNS failure。追加取得/別経路再試行は行わず、reader断片を private に `full_original=false` で保存した。

## 既存責務との関係

Art Direction `references/e-accessibility.md` の E-02（reflow）、E-03/E-04（focus遮蔽）、E-07（小targetと例外）、`visual-composition.md` 59・65行の狭幅での意味関係・操作名・読順を再利用する。狭幅対応そのものを新発見として扱わない。

継承 booking.css はすでに `overflow-wrap:anywhere`、actions の折返し、button の最大幅、button/slot の `2.75rem` 最小高さ、fieldset の `min-inline-size:0`、dates の `minmax(0,1fr)` を持つ。これらは宣言の存在であり、320 CSS pxの実描画、clip/overlay後の押下領域、全入力経路での到達性を実測した証拠ではない。2.75rem を根拠なく「測定済み44px」と表記しない。

## 5つの反例と契約案

### 1. 隠すことで横スクロールだけを消したページ

**原典上の事実。** hidden と clip は到達性が異なる。Chrome資料は表のwrapperに局所scrollを置き、見出し関係とキーボード経路を保持する。 [R2-S1] [R2-S2]

**推論。** ページのoverflow量がゼロでも必要情報・操作の消失を否定できない。表の存在だけではページ全域を例外扱いできない。

**追加するローカル規則。** 必要情報/操作IDを先に列挙し、狭幅後の各到達経路を記録する。局所例外はregion ID・二次元を要する理由・対象内容・横方向overflowのownerを持つ。ページ本文は別評価する。

**再現手順案（未実行）。** 長い予約名と末尾の必須『変更を確定』操作を幅600pxの子要素に置き、320pxの親にhidden/clip/autoを各適用する案を用意。別案では600px表のみを局所autoにし、本文と操作はreflowさせる。mouse/touch/keyboardごとに全必須項目へ到達できるか確認。

**棄却条件。** scrollbar無しだけをPASSとする、必須ラベル/操作が到達不能、表を根拠に本文まで横scroll許可。

**例外・限界。** 装飾画像の意図した切抜きは、タスクに必要な情報/操作が失われない根拠があれば別扱い。必要な二次元構造の例外根拠はResearcher-1のWCAG整理に従う。単なる長文や設定したmin-widthを必要性としない。hidden自体を全面禁止しない。実際の到達手段を評価する。

### 2. 視覚順序だけを確認して読順も保証したとする

**原典上の事実。** flex/gridの視覚順序とsource順は分離できる。reading-flowはspeech/linear navigationを制御し、描画順を変更しない。Chrome記事は137からの提供を記す。 [R2-S4] [R2-S10]

**推論。** source/visual/focus/ATを同一配列と仮定するvalidatorは偽合格と偽不合格の双方を生む。

**追加するローカル規則。** DOM順・視覚順・実際のTab順・対象ATでの読み順を別観測とする。業務上必要な前後関係を保持するか評価し、単純な全配列一致を唯一の判定基準にしない。

**再現手順案（未実行）。** 予約日時→変更候補→確定のDOMを持つ3領域を狭幅でCSS orderにより並べ替える。通常順とreading-flow使用案を分け、Tab/Shift+Tab、対象ATの順を実測する。

**棄却条件。** screenshotだけで順序をPASS、CSS宣言だけでAT結果をPASS、常にDOM順という決めつけ。

**例外・限界。** reading-flowによりsource順と実際の順序が異なっても直ちに不適合としない。Chrome137の公開情報は他browser/ATの互換性証明ではない。装飾上の配置差で意味・操作が損なわれないケースもある。

### 3. 部品単体の合格を重なるページに移す

**原典上の事実。** USWDS headerの記録はv3.8.1。400%で表示・操作が残り重なり/切れがない項目がある一方、単体試験を自サイトで再確認するよう明記する。 [R2-S3]

**推論。** 固定header/footer/通知と内容の合成で、単体合格では見つからない遮蔽が発生しうる。

**追加するローカル規則。** zoomの実測viewport、固定層、scroll位置、focus target、必要操作の可視性/操作性を同じ状態で記録する。単体証拠をページ合格へ昇格しない。

**再現手順案（未実行）。** 予約画面に固定上部headerと長い下部通知を同時表示し、狭幅/実zoomで先頭から最終確定までTab移動する。各focus後のscrollとoverlay位置、全必須説明と操作を確認する。

**棄却条件。** focusが覆われ操作できない、説明が回復不能に隠れる、部品の過去PASSだけでページPASS。

**例外・限界。** 固定表示自体を禁止しない。必要な閲覧/操作が保たれることが条件。focusの完全遮蔽と部分遮蔽のWCAG水準差はArt Direction E-03/E-04へ委任。

### 4. fine/hoverの一致を入力限定の証拠とする

**原典上の事実。** Mozilla実装資料は複数入力のprimary判定の曖昧さを報告する。MQ4ではany-pointerのcoarse/fineが同時一致しうる。any-hoverはhover不能機器の存在やkeyboardの有無を判定しない。 [R2-S5] [R2-S6]

**推論。** fine/hover一致を根拠に対象を縮小したり、必須操作をhover専用にしたりする判断は混在入力で破綻する。

**追加するローカル規則。** 必要操作は採用する入力経路ごとに到達可能にする。MQの観測値、実際に使った入力、イベントpointerType、接続変更前後を区別する。MQのみからWCAG target例外を導出しない。

**再現手順案（未実行）。** touch+mouse状態でany-pointer:fineとcoarseが両方trueの観測を用意。mouseを接続したままtouchで操作し、hoverなしで同じ必須操作へ到達できるか確認。接続変更で見た目/標的が突然変わる場合も記録する。

**棄却条件。** fineだけでtouch到達性やtarget例外をPASS、hover一致だけで必須menuをhover専用にする。

**例外・限界。** hoverは補助的強調や追加の利便性に使える。必須操作の唯一の入口にはしない。すべての機器を実機網羅したとは主張しない。Mozilla文書内のSurface/Firefox64-65等の報告は現行欠陥の再現証拠ではない。

### 5. 外接矩形を実際に押せる領域と同一視する

**原典上の事実。** getBoundingClientRectはCSS border-boxを囲む矩形を返す。clipPathはgeometry/bounding boxを保ちつつclipped領域へのpointer eventsを除外する。elementFromPointは座標のtopmost elementを返す。 [R2-S7] [R2-S8] [R2-S9]

**推論。** 十分大きいbounding boxでもclip、非矩形、別要素の重なりで実際のhit areaが小さい/消失することがある。

**追加するローカル規則。** 矩形geometry評価は矩形で実際のtargetと一致する根拠がある場合だけ。非矩形・clip・transform・occlusion・iframe等の未対応条件はHOLD/unsupported。BCRの数値だけで押せる面積を証明しない。

**再現手順案（未実行）。** 48×48 CSS pxのSVG rectを半径8pxのclipPathで切る案、同じbuttonの上にpointer-events:autoの透明layerを置く案、noneに変える案を比較。BCR、selected pointsのelementFromPoint、実pointer activationを別々に記録する。

**棄却条件。** BCRが大きいだけでPASS、clipやoverlay状態不明でPASS、synthetic coordinatesをbrowser測定として扱う。

**例外・限界。** 透明でもpointer-events:noneのoverlayはpoint hitから除外されるが、可視性評価は別。hit-testでchildが返る場合は関連するactivation targetとの関係を確認。複数点samplingは未検査部分を含む領域全体の証明ではない。非矩形だけで失敗とせず、未対応モデルによる合否断定を避ける。幾何閾値と例外はResearcher-1へ委任。


## 観測データの最低契約

宣言値、synthetic geometry、持ち込まれた測定、ブラウザーでの描画/activation、AT観測を別種にする。どれも同じ `pass` に畳まない。観測にはページ/部品状態、CSS px座標系、layout viewport、zoomの方式/値、regionとscroll owner、必要項目ID、形状/clip/変形/遮蔽の適用条件、入力機器、環境/版、証拠の由来を添える。

- **幾何だけの結果：** 対応する形状モデルに対する数値判定のみ。実操作やWCAG適合の結果にしない。
- **不明・未対応：** 必須観測なし、矛盾、非対応形状、入力や座標系不明は HOLD または unsupported とし、一般的な合格にしない。
- **頁内再現：** 長いラベル、局所表、固定層、入力切替などで必要操作までの経路を実行する。
- **このセッション：** ブラウザー実行が停止されているため、実描画・hit testing・AT結果は HOLD。

このデータ構造は本調査の設計提案であり、出典がJSONフィールド名を要求しているという意味ではない。

## 原典・時点・読んだ範囲

- **R2-S1** [overflow CSS property](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/overflow) — live MDN; last modified 2026-11-16。参照節：Values: hidden / clip; Accessibility。reader 行：267, 271, 383, 418, 493, 527。
- **R2-S2** [Responsive tables](https://developer.chrome.com/docs/modern-web-guidance/guides/ui-atoms/responsive-table?hl=en) — live browser-vendor guidance; retrieved 2026-11-23; revision not pinned。参照節：Implementation Steps 1–2。reader 行：88, 97, 98, 125, 130。
- **R2-S3** [Header accessibility tests](https://designsystem.digital.gov/components/header/accessibility-tests/) — observed tests identify USWDS v3.8.1; retrieved 2026-11-23。参照節：Test the header in your project; Zoom magnification tests。reader 行：213, 386, 399, 404。
- **R2-S4** [Use CSS reading-flow for logical sequential focus navigation](https://developer.chrome.com/blog/reading-flow) — published 2025-05-01; states Chrome 137 availability; current cross-browser support not tested。参照節：reading-flow; reading-order; Interaction with tabindex。reader 行：48, 50, 51, 55。
- **R2-S5** [Firefox Windows pointing-device implementation report](https://github.com/mozilla-firefox/firefox/blob/main/widget/windows/docs/windows-pointing-device/index.md) — live main branch retrieved 2026-11-23; commit/date/browser version unpinned; historical reports not current reproductions。参照節：Selection of Primary Pointing Device; Pointer Media Queries。reader 行：495, 508, 511, 523, 540, 567, 569。
- **R2-S6** [Media Queries Level 4](https://www.w3.org/TR/mediaqueries-4/) — W3C Candidate Recommendation Draft 2026-02-19; work in progress。参照節：7.2–7.3 Interaction Media Features。reader 行：894, 895, 914, 916, 918, 920, 925, 926。
- **R2-S7** [Element: getBoundingClientRect()](https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect) — live MDN retrieved 2026-11-23; revision not pinned。参照節：Return value and scrolling。reader 行：207, 208, 211。
- **R2-S8** [Document: elementFromPoint()](https://developer.mozilla.org/en-US/docs/Web/API/Document/elementFromPoint) — live MDN; last modified 2025-06-03。参照節：Description / Return value。reader 行：183, 184, 186, 189。
- **R2-S9** [SVG clipPath](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/clipPath) — live MDN; last modified 2025-11-07。参照節：Example: geometry and pointer events。reader 行：255, 256。
- **R2-S10** [CSS Display Module Level 4](https://www.w3.org/TR/css-display-4/) — live draft retrieved 2026-11-23; revision date not inspected; not an implementation-support assertion。参照節：4 Reading Order。reader 行：754, 756, 770, 774, 778, 823。

Chrome responsive-table資料はwrapper、スクロール到達性、header関係の根拠として限定利用した。pseudo-elementを使うstack化例をそのまま実装推奨として採用していない。USWDSは記載された試験版v3.8.1であり、最新製品の版と断定しない。Mozilla mainの実装報告はcommit/実測browser版が未固定で、記載されたSurfaceや旧Firefoxの問題を現行の再現結果として扱わない。MQ4は2026-02-19 Candidate Recommendation Draft、CSS Display 4は作業中の資料として扱う。

**実行した1-hop追跡：** Mozilla実装資料のlink 78 → MQ4 §7.2–7.3、Chrome reading-flow記事のlink 9 → CSS Display 4 §4。資料末尾のリンク存在だけでなく遷移先の該当節もreaderで読んだ。

## 取得と監査境界

初期3クエリと公式資料確認2クエリを、それぞれ検索バッチとして実行した。ツールはヒットを統合して返すため、どのヒットがどのクエリ由来かは復元しない。選ばなかったヒットを含む返却全件はprivate rawに保持した。

fetch.pyの実行はMozilla資料への1回のみで、`[Errno -3] Temporary failure in name resolution`。全文原本の取得成功は0件。reader断片はページ原本とbyte一致しない。JSONのsource hashはprivate断片ファイルのSHA256であり、原本hashではない。

**未確認：** 実機・ブラウザー・AT、Firefox報告の現行再現や修正、相互運用性、全検索ヒット本文、地図専用実装。WCAG数値/円の間隔判定と例外根拠はResearcher-1へ渡す。非公開制御記録は公開研究物の外に保存した。
