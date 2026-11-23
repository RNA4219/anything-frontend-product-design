# Round 03 Analysis — Reflowと実対象領域の検査契約

**結論：2つのUnitに整理する。実UIを要する判断はHOLD。幾何計算は対応形状と入力に限定した結果を返し、WCAG適合へ昇格しない。**

sankaiの分解・理解・溶解を現行のLLM手順で行った。独立した自動分解CLIは使っていない。固定評価計画は変更していない。以下の反証手順は全て未実行であり、実装・登録・反例実行は後続担当へ渡す。費用はunknown。

## 方法と証拠境界

【規範】WCAG Recommendationの要件、【公式解説】informativeなUnderstanding、【事実】一次実装資料の観測範囲、【推論】図例からの数式等、【製品policy】限定検査器の契約候補を区別する。第三者原文の転載ではない。MQ4/CSS Display 4のdraftを全実装の証明にしない。

Reflowの保持・例外scope・観測契約と、target実領域のサイズ/spacingへ2分割。順序/入力能力は観測条件として保持。

overflow量、CSS宣言、外接矩形、過去部品試験は、それぞれ保持・実target・ページ適合の証明とは異なる。例外を外すと意味が変わるため同じUnitに残す。

表/予約画面/特定ブラウザを必須実装にせず、対象・条件・強さを保持。数値、例外、未対応、証拠境界は維持し、識別子と保存形式を変更可能にする。

研究資料は2026-11-23取得の部分readerに基づく。両研究者の完全原文取得は各1回失敗し、WCAG本体には書き換え要約表示がある。原文完全取得・逐語一致・実ブラウザ/ATの観測を主張しない。検証の由来と未確認理由を残す。

## C002-U1 — Reflowの例外範囲と情報・操作・順序の観測契約を固定する

### 指示本文

1. 【規範】縦スクロールで読む内容は幅320 CSS px相当、横スクロールで読む内容は高さ256 CSS px相当で、情報・機能を失わず二方向スクロールを要しないか確認する。利用・意味のために二次元配置が必要な部分は、その部分だけを例外候補にする。400%は1280/1024 CSS pxから対応境界を得る設定例であり、画面解像度・画像幅・固定zoom値だけで境界到達を証明しない。
2. 【製品policy】観測前に必要情報と操作をIDで列挙し、元の状態と境界状態の到達先・到達手順を対応づける。再配置や折り畳み後も内容・操作へ到達できる根拠を残す。唯一の操作や必要説明を削除、clip、非表示にしてoverflowを消した場合、到達可能な代替がなければ保持条件を満たさない。非表示CSSの存在だけで一律不合格にしない。
3. 【公式解説＋製品policy】例外ごとに対象region ID、内容、二次元配置を必要とする具体的理由、影響するoverflowの所有者を記録する。表・地図等の名前だけで自動承認せず、隣接文章、ページ送り、操作、通常の表セルを個別に評価する。無関係な本文へページ全体の例外を継承しない。根拠不足の例外はHOLDにし、評価対象から無言で除外しない。
4. 【公式解説】局所scroll containerは有用な推奨であり、一律の規範必須条件ではない。例外部分だけがページoverflowを生み、全ての非例外部分が適切にreflowする場合は、ページoverflowという数値だけでFAILにしない。逆にscrollWidthとclientWidthが一致しても、情報・操作保持の合格にしない。
5. 【製品policy】証拠をCSS等の宣言、synthetic_geometry、supplied_measurement_unverified、browser_observed、assistive_technology_observedに分ける。ページ/部品/状態、書字・scroll方向、layout viewport、zoom方式/値、scroll位置、固定層、必要項目ID、入力方法、環境/版、観測資料、未知条件を同一状態へ結び付ける。部品単体や別状態の過去合格を現在のページへ移さない。
6. 【事実＋製品policy】DOM順、視覚順、実際のTab/Shift+Tab順、対象ATの読み順を別観測として、業務上必要な前後関係を確認する。reading-flow等により順序が変わり得るため、配列の全面一致や常にDOM順という仮定で合否を決めない。CSS宣言やスクリーンショットからAT結果を推定せず、機能対応と実際の順序が未観測ならその判断をHOLDにする。これは順序観測の条件であり、新しい汎用読順Unitを設ける指示ではない。
7. 【事実＋製品policy】pointer/hover/any-pointer/any-hoverは能力queryとして保存し、実際に使用したmouse/touch/pen/keyboard等の経路と分ける。fineとcoarseの同時一致を矛盾として拒否せず、fineやhoverの一致からtouch不在・keyboard不在・target例外を導かない。入力切替とhoverなしの必要操作は、対象環境が定まった実観測で確認する。
8. 【製品policy】不正形式・有限でない値・矛盾は入力不備として拒否し、必要観測の欠落・未対応条件は理由付きHOLDにする。入力契約の検査成功、実reflow、情報/操作保持、順序、focus、ATを別欄で返す。今回、実ブラウザ・ATを必要とする欄は未実行/HOLDとし、観測モデルの成功をWCAG適合にしない。200%文字拡大とfocusの完全/部分遮蔽は既存基準に従う別検査として保持する。

### 使う場面

狭幅・拡大時の画面、長いラベル、局所二次元領域、固定層を持つページを実装または検査する前後。

### 入力

- 必要情報/操作IDと業務上の順序制約
- ページ・部品・状態とregion別の内容、例外理由、overflowの所有者
- CSS pxのlayout viewport、書字/scroll方向、zoom方式/値、scroll位置
- 宣言と観測の由来、対象ブラウザ/ATの版、能力queryと実使用入力
- DOM/視覚/Tab/AT順の独立した観測、保持先と到達手順

### 出力

- region別の非例外reflow・例外根拠・保持先の対応表
- 必要情報/操作と意味上の順序制約の結果、未観測理由
- 入力契約検査と実描画/入力/AT検証を分離した報告

### 条件

- 固定rubricとrequired_casesを変更しない。
- 例外あり/なし、非例外領域、必須操作を同じページ状態で評価する。
- 観測フィールド名と判定ラベルは製品policyであり、規範がJSON schemaを要求するという意味ではない。
- 現セッションの実UI検査制限を迂回しない。未観測を合格で埋めない。

### 例外

- 必要な二次元部分の例外は、その部分以外の保持・reflow・操作・順序を解除しない。
- 折り畳みや再配置は到達可能性を保てば許される。装飾の切抜きと必要情報の欠落を区別する。
- ページoverflowだけで不適合とは限らず、local container不在だけでも不適合とはしない。
- 意味や操作に影響しない視覚配置差を、全順序の不一致だけで不合格にしない。
- SC 2.4.11の完全遮蔽とより厳しい部分遮蔽の条件を混ぜない。

### 依存先

- Art Direction E-02/E-03/E-04、E4-07、visual-compositionの意味・操作・読順指針
- 既存C-UI-001〜004の部品・状態・イベント・focus契約
- A/Bが定める必要情報・業務操作・順序、Dの評価とリリース判断
- 実描画・入力・ATを検証する際の対象環境と観測手段

### 理解：この単位にする理由

reflowの仕事は幅の測定だけで完結せず、失われない情報・機能と例外範囲を一体として持つ。順序と入力能力は観測の適用条件にまとめ、既存部品責務を増殖させず、宣言から実績への飛躍を防ぐ。

### 溶解：変更可能範囲

- regionや必要項目の識別子、証拠の保存形式、検査用フィールド名は対応関係と由来を保てば変更可能。
- 局所scroll、再配置、折り畳み等の実装方法は、必要情報・操作と非例外reflowが保たれる場合に選択可能。
- 製品が局所scroll containerを追加必須にする場合は、WCAGの義務と分けた製品policyとして明記する。

### 未確認事項と影響

- 対象ページで実際に必要項目が保持されるか、実zoom後のlayout viewportとscroll挙動。
- 対象ブラウザ/ATでのreading-flow対応と実際のTab/読み順。
- 混在入力と接続変更時の到達性。Mozillaの歴史的記録は現行再現ではない。
- 200%文字拡大とfocus遮蔽の実観測。これらはreflowや数値検査から決められない。

### 失敗条件

- 必須操作を隠してoverflowだけ消す
- 表を理由にページ全体を免除する
- 例外に起因するページoverflowを機械的にFAILとする
- 局所scroll containerを無条件の規範義務へ強める
- スクリーンショット・CSS・過去部品試験から順序やページ適合を推定する
- fine/hover一致で実際の入力や例外適用を決める

### 出典と位置

- [WCAG22](https://www.w3.org/TR/WCAG22/) — normative Recommendation; source identity reused from round-01。研究取得日2026-11-23; 完全原文未取得。1.4.10 Reflow / 2.5.8 Target Size (Minimum) / 1.4.4 Resize Text / 1.3.2 Meaningful Sequence / 2.4.11 Focus Not Obscured (Minimum)。研究記録 `researcher-1.json#/sources/0`。reader位置 `{"reflow": [612, 630], "target": [1152, 1168], "resize": [506, 513], "sequence": [405, 412], "focus": [987, 996]}`。
- [C03-R1-S02](https://www.w3.org/WAI/WCAG22/Understanding/reflow) — informative explanation; not a normative requirement。研究取得日2026-11-23; 完全原文未取得。Reflowing websites and web applications / Understanding the scope of exceptions / Tabular data and grid-based UI / Why specifically 320px and 256px? / Overlap with other success criteria。研究記録 `researcher-1.json#/sources/1`。reader位置 `[[63, 72], [99, 129], [155, 177], [181, 204]]`。
- [C03-R1-S04](https://www.w3.org/WAI/WCAG22/Understanding/resize-text) — informative; normative criterion restated at SC section。研究取得日2026-11-23; 完全原文未取得。Success Criterion (SC)。研究記録 `researcher-1.json#/sources/3`。reader位置 `[[33, 35]]`。
- [R2-S1](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/overflow) — official。live MDN; last modified 2026-11-16。Values: hidden / clip; Accessibility。研究記録 `researcher-2.json#/sources/0`。reader位置 `[267, 271, 383, 418, 493, 527]`。
- [R2-S2](https://developer.chrome.com/docs/modern-web-guidance/guides/ui-atoms/responsive-table?hl=en) — official。live browser-vendor guidance; retrieved 2026-11-23; revision not pinned。Implementation Steps 1–2。研究記録 `researcher-2.json#/sources/1`。reader位置 `[88, 97, 98, 125, 130]`。
- [R2-S3](https://designsystem.digital.gov/components/header/accessibility-tests/) — official。observed tests identify USWDS v3.8.1; retrieved 2026-11-23。Test the header in your project; Zoom magnification tests。研究記録 `researcher-2.json#/sources/2`。reader位置 `[213, 386, 399, 404]`。
- [R2-S4](https://developer.chrome.com/blog/reading-flow) — official。published 2025-05-01; states Chrome 137 availability; current cross-browser support not tested。reading-flow; reading-order; Interaction with tabindex。研究記録 `researcher-2.json#/sources/3`。reader位置 `[48, 50, 51, 55]`。
- [R2-S5](https://github.com/mozilla-firefox/firefox/blob/main/widget/windows/docs/windows-pointing-device/index.md) — official。live main branch retrieved 2026-11-23; commit/date/browser version unpinned; historical reports not current reproductions。Selection of Primary Pointing Device; Pointer Media Queries。研究記録 `researcher-2.json#/sources/4`。reader位置 `[495, 508, 511, 523, 540, 567, 569]`。
- [R2-S6](https://www.w3.org/TR/mediaqueries-4/) — official。W3C Candidate Recommendation Draft 2026-02-19; work in progress。7.2–7.3 Interaction Media Features。研究記録 `researcher-2.json#/sources/5`。reader位置 `[894, 895, 914, 916, 918, 920, 925, 926]`。
- [R2-S10](https://www.w3.org/TR/css-display-4/) — official。live draft retrieved 2026-11-23; revision date not inspected; not an implementation-support assertion。4 Reading Order。研究記録 `researcher-2.json#/sources/9`。reader位置 `[754, 756, 770, 774, 778, 823]`。

### 反証手順案（全件未実行）

| ケース | 手順 | 棄却条件 |
| --- | --- | --- |
| narrow-prose-page | 必要本文と操作を持つ通常文書を320 CSS px相当で観測し、必要項目ごとの到達先と非例外reflowを確認する。 | overflow数値だけで保持をPASSにする。 |
| local-two-dimensional-table | 必要な二次元表、折り返すセル、隣接本文と操作を分け、例外の対象と根拠を記録する。 | 表の存在だけでセルや隣接操作まで免除する。 |
| unjustified-page-wide-exemption | 表の例外を理由に通常本文も横scrollする入力を与える。 | ページ全体の例外を承認する。 |
| excepted-page-overflow | 例外部分だけがページoverflowを生み、全非例外部分は320内でreflowする観測案を用意する。 | ページoverflowまたはlocal container不在だけでFAILにする。 |
| long-label-and-retained-action | 長いラベルと唯一の確定操作をhidden/clip/autoや折り畳みで変え、到達性を入力経路別に確認する。 | scrollbar消失だけでPASS、または到達可能な折り畳みを一律FAIL。 |
| order-input-observation | DOM/視覚/Tab/AT順を別にし、reading-flowの未観測、fine/coarse同時一致と実touch入力を記録する。 | 全配列一致を唯一の条件にする、宣言からATをPASS、能力queryから入力不在を推定する。 |
| fixed-overlay-at-zoom | 固定headerと通知を合成した同一状態で、必要操作への到達とfocusを既存遮蔽基準に従って観測する。 | 単体の過去合格だけでページ合格、完全/部分遮蔽の水準混同。 |
| missing-or-synthetic-measurement | viewport/状態/証拠を欠く入力やsyntheticだけの入力を与える。 | 一般的なaccessibility PASSやbrowser_observedを出力する。 |
## C002-U2 — 実際の対象領域に限定してサイズと間隔を計算する

### 指示本文

1. 【規範＋公式解説】SC 2.5.8のサイズ条件は24×24 CSS px以上であり、公式解説に従い軸平行の24×24正方形が実際のpointer-action領域内に完全に収まることを確認する。外接矩形やmin-width/min-heightの宣言だけを対象内部の証明にしない。24直径の円のbbox=24×24はサイズ条件の証明にならない。
2. 【製品policy】限定検査器は、実効対象領域と一致すると確認された軸平行の充填矩形だけを扱う。全対象のID・動作・同一状態/CSS px座標系・x/y/width/height・証拠種別・形状適用条件・周辺対象一覧の完全性を受け取る。有限な数値、正の寸法、一意ID、同一座標系を検査する。非矩形、clip、変形、遮蔽、改行断片、iframe等が未解決ならHOLD/unsupportedとし、不適合そのものとは断定しない。
3. 【事実＋製品policy】getBoundingClientRectはborder boxを囲む矩形であり、実効hit areaを証明しない。elementFromPointの複数点samplingも領域全体と実activationの証明にはならない。子要素・関連control・event処理による実動作を確認する。別動作の重なりを除く必要や同一動作の扱いが未解決なら元の矩形を使ってPASSにしない。
4. 【規範＋製品policy】対応する矩形に限りwidth >= 24かつheight >= 24でサイズ条件を満たすと計算する。いずれかが24未満なら不足対象としてspacingまたは他の根拠付き例外を確認する。23.999を24へ丸めず、独自のepsilonをWCAGの許容差として追加しない。観測誤差により閾値のどちらか決められない場合はHOLDにする。
5. 【公式解説＋推論】不足対象iの最小外接矩形中心(cx_i,cy_i)へ半径12の円を置く。不足対象どうしでは中心距離二乗 < 576を重なりとする。さらに各不足対象iと他の全ての実対象jについて、dx=max(x_j-cx_i,0,cx_i-(x_j+w_j))、dy=max(y_j-cy_i,0,cy_i-(y_j+h_j))とし、dx²+dy² < 144を重なりとする。相手jが大きい場合も不足対象の場合もこの比較を省かない。中心距離だけでは幅広で高さの小さい対象への侵入を見落とす。
6. 【推論＋製品policy】上記strict <と等号の接触許容はUnderstandingの図5/図10の適合例から導いた限定幾何モデルであり、規範本文が不等式を定義したと書かない。対応する入力についてのみ、サイズ関係・円どうし・円と実対象の結果を別に返す。サイズを満たす対象自体にはspacingを追加要求しないが、その対象に隣接する不足対象の円との比較から除外しない。
7. 【規範＋製品policy】spacing以外の例外は条件と根拠を残す。同等controlは同一ページで同じ機能を持ち当該基準を満たす対象を特定する。inlineは文中であるか非対象文字のline-heightでサイズが制約される状況を示す。UA controlはUAがサイズを決め作者が変更していない根拠を示す。essentialは情報/機能に不可欠な提示または法的要求を具体化する。nativeタグ、display:inline、密度の好み、別ページ、循環する同等例外申告だけで承認しない。根拠不足はHOLD、明確な条件不一致は例外不成立として返し、無言skipしない。
8. 【製品policy】例外対象を含む他の実対象はspacingの障害物一覧から消さない。隣接対象の形状/座標が未確認ならそのspacing判断はHOLDにする。操作で開いたmenu/dialog等は当該状態の新しい対象を評価する。一時的に覆われた背後の対象の扱いを、一般的な情報やfocus遮蔽の許可へ拡張しない。
9. 【製品policy】synthetic矩形は計算モデルの試験入力として扱い、数値関係の狭いPASSだけを許す。持込測定、実ブラウザのlayout/activation、AT観測を混同しない。CSS変数2.75remの存在を測定済み44 CSS pxとしない。能力queryから実入力やSC例外を導かない。実targetの一致が未確認なら実UI結果はHOLDとし、幾何PASSからWCAG・keyboard・focus・操作完了の合格へ昇格しない。

### 使う場面

pointer targetの小ささ・隣接間隔を確認するとき。実効領域を測る前のschema設計、および限定矩形モデルの計算検査にも使う。

### 入力

- 全対象の一意ID・実動作・同一ページ/状態・CSS px座標系
- 実効軸平行充填矩形のx/y/width/heightとその根拠、隣接対象一覧の完全性
- 形状、clip、transform、重なり、改行断片、iframe等の対応状態
- サイズ/spacing/equivalent/inline/UA/essentialの判断根拠
- 証拠種別、実入力、環境/版、測定不確かさ

### 出力

- 対象ごとのサイズ関係とspacing衝突対、適用した例外と根拠
- 入力不備、未対応、未観測、不確かさを区別した診断
- 計算モデルの結果と実hit area・実操作のHOLDを分離した報告

### 条件

- 座標は同じviewport/state/単位に揃え、負の座標自体を不正にしない。寸法は有限・正とする。
- 全対象のactual geometryを把握せずに周辺の非衝突を保証しない。
- 接触境界の計算モデル、寸法判定、例外審査、証拠種別を独立に記録する。
- geometry/schemaだけの成功はこのUnit全体の実UI適合やWCAG適合を意味しない。
- 有限入力でも計算で非有限値になる等、数値処理の限界に達した場合は結果を拒否/保留し、非衝突扱いで続行しない。

### 例外

- spacingは宣言marginではなく円と実領域の幾何条件により確認する。
- 同等control、inline、UA決定、essentialの例外は各条件にのみ掛かり、他の基準を免除しない。
- 同じ動作・同じページを開く重なりには公式解説の例外があるが、意味の一致をbboxから推定しない。
- interaction/scripted contentに一時的に覆われた背後の対象をその状態で評価しない説明は、新しく出た対象の免除を意味しない。
- 非矩形は規範上の自動FAILではなく、この矩形検査器の未対応として扱う。

### 依存先

- C002-U1の観測由来・実入力・状態契約
- Art Direction E-07と既存入力/操作ガイダンス
- 既存C-UI-001〜004の意味・event・keyboard・focus契約
- 実target検証に必要な描画/activation観測、Dの評価

### 理解：この単位にする理由

サイズとspacingは同じ実効対象集合を共有し、例外と形状制限を外すと偽合格になる。矩形への限定は計算可能範囲を明示する製品policyであり、WCAGの対象形状を矩形へ限定する規則ではない。円どうしと円対実領域の両方を残すことで広く薄い対象の反例を扱える。

### 溶解：変更可能範囲

- geometry表現や実装言語は、単位・状態・実効領域・閾値・両方の交差条件・出典由来を保持すれば変更可能。
- 非矩形、clip、変形等は実効領域を検証できる別モデルと反証試験を追加して対応を広げられる。未知を無言で矩形へ近似しない。
- 製品としてより大きなtargetを要求できるが、24 CSS pxの基準と区別する。

### 未確認事項と影響

- 各実targetが宣言矩形と一致するか、遮蔽/clip後の領域、eventによる実動作。
- 規範由来の数値epsilonは今回の原典範囲で見つかっていない。
- 例外根拠の真偽と同等controlの実測結果は、適用ページの観測が必要。
- 全browser/端末/ATの互換性、現行Firefox報告の再現、targetに関する包括的hit-testing仕様の確認。

### 失敗条件

- bboxだけで実targetサイズをPASS
- clipや別動作overlayを無視
- 不足対象の中心距離だけを検査
- 全ての対象へspacingを追加必須化
- 例外や未対応対象を無言で削除
- 23.999を丸める、未知のepsilonを追加
- syntheticをbrowser実績・WCAG適合へ昇格

### 出典と位置

- [WCAG22](https://www.w3.org/TR/WCAG22/) — normative Recommendation; source identity reused from round-01。研究取得日2026-11-23; 完全原文未取得。1.4.10 Reflow / 2.5.8 Target Size (Minimum) / 1.4.4 Resize Text / 1.3.2 Meaningful Sequence / 2.4.11 Focus Not Obscured (Minimum)。研究記録 `researcher-1.json#/sources/0`。reader位置 `{"reflow": [612, 630], "target": [1152, 1168], "resize": [506, 513], "sequence": [405, 412], "focus": [987, 996]}`。
- [C03-R1-S03](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum) — informative explanation/examples; normative SC restated separately。研究取得日2026-11-23; 完全原文未取得。Exceptions / Size requirement / Spacing, Figures 5 and 10 / Key Terms: target, minimum bounding box, essential。研究記録 `researcher-1.json#/sources/2`。reader位置 `[[61, 103], [105, 129], [203, 235]]`。
- [R2-S5](https://github.com/mozilla-firefox/firefox/blob/main/widget/windows/docs/windows-pointing-device/index.md) — official。live main branch retrieved 2026-11-23; commit/date/browser version unpinned; historical reports not current reproductions。Selection of Primary Pointing Device; Pointer Media Queries。研究記録 `researcher-2.json#/sources/4`。reader位置 `[495, 508, 511, 523, 540, 567, 569]`。
- [R2-S6](https://www.w3.org/TR/mediaqueries-4/) — official。W3C Candidate Recommendation Draft 2026-02-19; work in progress。7.2–7.3 Interaction Media Features。研究記録 `researcher-2.json#/sources/5`。reader位置 `[894, 895, 914, 916, 918, 920, 925, 926]`。
- [R2-S7](https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect) — official。live MDN retrieved 2026-11-23; revision not pinned。Return value and scrolling。研究記録 `researcher-2.json#/sources/6`。reader位置 `[207, 208, 211]`。
- [R2-S8](https://developer.mozilla.org/en-US/docs/Web/API/Document/elementFromPoint) — official。live MDN; last modified 2025-06-03。Description / Return value。研究記録 `researcher-2.json#/sources/7`。reader位置 `[183, 184, 186, 189]`。
- [R2-S9](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/clipPath) — official。live MDN; last modified 2025-11-07。Example: geometry and pointer events。研究記録 `researcher-2.json#/sources/8`。reader位置 `[255, 256]`。

### 反証手順案（全件未実行）

| ケース | 手順 | 棄却条件 |
| --- | --- | --- |
| target-size-boundary | 24×24と23.999×24の充填矩形を与える。 | 後者をsize PASSに丸める、または前者へspacingを追加要求する。 |
| undersized-target-spacing | 20×20の対象をx=0とx=24、次に23.999へ置く。円対円と円対実対象を両方記録する。 | 接触例と侵入例を同じ非衝突として返す、またはstrict <を規範明文と表示する。 |
| circle-to-large-target | 16×16を(0,0)、40×40を(20,0)、次に(19.999,0)へ置く。 | 半径12の接触/侵入境界を区別しない。 |
| wide-short-neighbor | 16×16を(0,0)、100×16を(0,17)へ置く。中心間は遠いが小対象の円は相手の実領域へ侵入する。 | circle-circleだけでspacing PASSにする。 |
| exception-with-and-without-evidence | 同等/inline/UA/essentialごとに条件を満たす根拠付き案とBooleanのみ・条件不一致・循環参照案を対にする。 | 不足根拠をHOLDにせず免除、正当な例外までサイズ不合格として一律棄却。 |
| nonrectangular-or-clipped-target-limit | 直径24円のbbox、clipされた48×48、別動作layerのある矩形を与える。 | bboxだけでPASS、または非矩形を規範上の自動FAILにする。 |
| malformed-or-incomplete-targets | 非有限/非正寸法、重複ID、座標系混在、欠落隣接対象、計算overflow、不明例外を与える。 | 無言skipやgeneric PASSを返す。 |
| missing-or-synthetic-measurement | 同じ正常矩形をsynthetic、未検証持込測定、実観測の異なる種別で渡す。 | 幾何結果からbrowser/AT/WCAG結果を埋める。 |

## 重複排除

| 既存 | 今回の扱い |
| --- | --- |
| Art Direction E-02/E-03/E-04/E-07、E4-07、visual-composition | reflow、focus遮蔽、target例外、意味と読順を再利用。増分は観測入力、局所例外根拠、幾何境界、HOLD条件。 |
| Art Direction G4/C2/C3/D2の入力意味・情報保持・pointer/pan/zoom | 既存責務を維持し、一般的な操作/入力Unitを増やさない。 |
| booking-change/booking.cssのwrap/max-inline-size/min-inline-size/minmaxと2.75rem | 既存宣言を保持。宣言存在を実測reflow/実hit area/測定済み44pxへ昇格しない。 |
| C-UI-001〜004（round01 C001-U1〜U4） | 部品・状態・イベント・keyboard/focus責務を維持。本分析から委任し重複登録しない。 |
| C-UI-005〜007（round02 C003-U1〜U3） | token型/graph・theme・CSS出力の検査を維持。token宣言の成功と実geometryの成功を区別する。 |

## 検索の比較と残る判断

規範側で閾値と例外の意味を保ち、実装資料側で宣言・境界箱・部品単体からの誤推定を抑える。両者とも実UI検証の代わりではない。

Researcher 1は規範・解説の2 query/1検索batch、返却2 hitを記録。Researcher 2は初期3 queryと公式資料確認2 queryを記録。batch内のquery別帰属は不明で復元しない。両者の取得失敗や未観測を探索品質の優劣へ置き換えず、飽和率は未測定とする。分析者による追加検索は0。

- **未取得**：完全原文の取得は両研究者で失敗。規範readerは書き換え要約。 位置付き研究要約に基づく分析であり、未表示部分・逐語原文まで検証したとはしない。
- **未実行**：反例候補、実reflow、hit area、入力、ATは未実行。 verificationは手順案。実UIを要するUnitの採否はHOLD。純粋計算のみ後続の実行/独立再確認で限定判断可能。
- **推論**：接触許容のstrict <はUnderstanding図例から導いたモデル。数値epsilonなし。 規範明文の数式と呼ばず、未知の測定誤差はHOLDにする。
- **適用先未提示**：必要情報/操作、例外根拠、実対象集合、環境/版と実入力。 判定へ影響する箇所だけ保留。schemaや純粋計算の設計は進められる。
- **次backlog**：reading-flowとATの相互運用性、混在入力接続変更、非矩形hit-testingの対応拡張。 今回は測定条件/未対応理由に残し、汎用Unitへ昇格しない。

## 対象外

- 新しい汎用reading-flow/混在入力Unitの増設
- 既存E系、部品/keyboard/focus、token graph/theme/CSS出力契約の重複登録
- 全WCAG適合やブラウザ/ATの未実行合格
- 局所scroll containerの規範必須化、ページoverflowの無条件FAIL
- 未知の非矩形/clip/transformをbboxへ近似する検査
- 第三者全文・非公開調査記録・内部運用情報の公開
- 実装・登録・実UI実行・反例試験・commit

## 固定計画との照合

固定rubricは情報・操作の保持、局所例外、閾値/例外/入力条件、不正・不明観測の拒否、証拠種別、WCAGへの過大一般化防止、既存責務の保持を要求する。これらを2Unitの本文とverificationへ対応させた。
計画: `campaigns/C/rounds/03/plan.json`。SHA256: `1790a4f36964e7974061986021d3766a2456e8c75cead7085156571ecf6c9f97`。

必須ケース: narrow-prose-page, local-two-dimensional-table, unjustified-page-wide-exemption, long-label-and-retained-action, target-size-boundary, undersized-target-spacing, exception-with-and-without-evidence, nonrectangular-or-clipped-target-limit, missing-or-synthetic-measurement。

JSONと出典pointerの整合確認は成果物の形式検査であり、上記反例や実UIを実行した証拠ではない。
