# C-001 — Researcher-1：操作部品の状態とDOMの契約

**結論：採用候補は、操作の意味・利用可否・モーダル性を入力に受け、対応するネイティブ機構と検証条件を出力する契約である。** 「無効」「読取専用」「モーダル」という見た目の分類だけでは不足する。以下は一次資料による研究結果と提案を分けたもので、実装・ブラウザ検証・AT検証は未実施。

調査日：2026-11-23。対象：C-001のみ。HTMLは取得時表示の2026-11-22更新版。Art Direction参照コミット：`f5df625dbc577d6a3ca28e13ef09e39b135b4a6f`。imozuru：`30c3b59a076ce228f05aa3036809297422f23dee`。

## 1. 確認した事実

1. **リンクとボタンは別の意味を持つ。** `a[href]` はハイパーリンクを表す。`button` はtypeに応じた起動処理を持つ。現行HTMLのtype既定値はAutoであり、command属性等と親selectに関する例外がある。「type未指定なら常にsubmit」とは一般化できない。[HTML-ANCHOR](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-a-element)、[HTML-BUTTON](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element)

2. **HTMLのdisabledは、すべての変更を禁止する仕組みではない。** 属性の値でなく存在で有効になる。disabledなfieldsetの子孫には、最初のlegend配下の例外がある。利用者操作キューのclickを抑止し、制約検証の対象から外すが、JavaScriptや同一radio群からの間接変更まで禁止しない。フォームのentry list構築ではdisabledなfieldを除外する。[HTML-DISABLED：4.10.19.5、4.10.22.4](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#enabling-and-disabling-form-controls:-the-disabled-attribute)

3. **readonlyは編集可否を表し、disabledと同義ではない。** 適用可能なinputのreadonlyは利用者編集を止め、制約検証の対象外になる。checkboxやbuttonには適用しない。readonlyだけを理由にentry listから除外する規則はなく、nameなど他の条件は引き続き必要である。[HTML-READONLY](https://html.spec.whatwg.org/multipage/input.html#attr-input-readonly)、[HTML-DISABLED：4.10.22.4](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html)

4. **aria-disabledは操作停止コードの代わりにならない。** ARIA in HTMLは、buttonでnative disabledの代わりに使う場合、機能的な無効化のスクリプトを併用する例を明記する。native属性との矛盾は不可で、disabledとaria-disabled=falseの併用は禁止。ARIAの無効状態はフォーカス可能な子孫にも及ぶ。[ARIA-HTML：4.2](https://www.w3.org/TR/2026/REC-html-aria-20260811/#requirements-for-use-of-aria-attributes-in-place-of-equivalent-html-attributes)、[ARIA12：aria-disabled](https://www.w3.org/TR/wai-aria-1.2/#aria-disabled)

5. **showModalによるモーダル性は、aria-modalの文字列と別の機構である。** HTMLは最上位モーダルとそのflat-tree子孫以外をinertにする。inertはフォーカス、ヒットテスト、アクセシビリティAPI公開等に関わる。最上位モーダルは祖先のinertを逃れるが、自身のinert指定は別である。ARIAはモーダル内部だけで操作を完結できることを要求する。[HTML-INERT：6.3、6.3.1](https://html.spec.whatwg.org/multipage/interaction.html#inert)、[ARIA12：aria-modal](https://www.w3.org/TR/wai-aria-1.2/#aria-modal)

6. **dialogのフォーカスは、初期対象と開閉アルゴリズムを確認する必要がある。** HTMLは期待する操作対象へのautofocusを勧め、対象がなければdialog自身へのautofocusを示す。dialog自身へのtabindexは禁止。openの手動削除はcloseイベント等を省く。close時の復帰処理は、モーダルだったか、現フォーカスが内部にあるかで分岐するため、非モーダルの外に移動済みの利用者を一律に呼出元へ戻す契約は誤る。[HTML-DIALOG：4.11.4、dialog focusing steps、close the dialog](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-dialog-element)

7. **WCAG 4.1.2は名前・役割・変更可能な状態等のプログラム上の扱いと変更通知を要求する。** 標準HTML部品を仕様どおり使う場合に関する注記は、この達成基準の説明であり、コンポーネント全体のWCAG適合を保証する文ではない。キーボード操作・脱出は2.1.1/2.1.2にも照らす。[WCAG22：4.1.2](https://www.w3.org/TR/WCAG22/#name-role-value)、[2.1.1](https://www.w3.org/TR/WCAG22/#keyboard)、[2.1.2](https://www.w3.org/TR/WCAG22/#no-keyboard-trap)

## 2. 提案する再利用契約（規格の引用ではなく設計提案）

業務側から受け取る入力は、`intent`（移動/操作/入力）、`canExecute`、`editable`、`availabilityPresentation`、`dialogMode`、`initialFocusTarget`、`returnFocusFallback`、`serializationPolicy`。なぜ実行不可か、いつ取消できるか、何を保存するかはCで創作しない。

| 入力・状態 | DOM/動作の契約候補 | 反証できる観測 |
| --- | --- | --- |
| 移動 / 通常操作 | 移動先のある遷移はa[href]、操作はbuttonを初期候補。非送信ボタンはtype=buttonを明示 | button操作が意図しないform submitを起こす。リンクの別タブ操作などが失われる |
| 実行不可・通常の無効化 | 対応要素のdisabledを使用。ARIA同義属性を重ねない。送信対象から外れる結果をserializationPolicyと照合 | Tab/クリックから対象処理が実行される。必要データがFormDataから消える |
| 実行不可・Tab上で発見可能にする明示要件あり | 適合するbuttonでaria-disabled=trueを使用する場合、すべての公開実行経路を同じcanExecuteでガード。HTML disabledとは併用しない | pointer/Enter/Space/公開ショートカット経路のどれかで実行数が増える |
| 編集不可だが値を使う入力 | readonly適用可能な型だけを使う。表示値・DOM value・送信値の期待を分けて記録 | 利用者編集で変化する。readonlyだけを理由に値が送信から消える |
| モーダルを開く/閉じる | 接続済みdialogをshowModalで開き、意味のある初期対象を選ぶ。close系処理とcloseイベントをアプリ状態へ同期。取消結果を業務状態へ誤適用しない | 背後を操作できる。DOMは閉じたがアプリはopenのまま。取消で確定処理が実行される |
| 非モーダル | showを選ぶ。モーダル用の背景inert・循環フォーカスを機械的に適用しない。外へ移動済みなら閉じる際のフォーカスを奪わない | 背景の通常操作が不能になる。閉じると別の作業から呼出元へ強制移動する |
| 呼出元消滅 | 利用可能な呼出元への復帰を確認し、不可能なら渡された論理的な次対象へ移す | 削除済み/hidden/disabled/inertの呼出元を復帰先として成功扱いする |

契約の最小出力は「要素・型・DOM属性/プロパティ・実行ガード・フォーカス遷移・送信結果・検証ケース」の1組。CSSクラスやdata-stateは表現用であり、この組の代替として扱わない。ネイティブ機構と重複するkeydown起動を足す場合は、二重実行が起きないことを示す。

## 3. 反例と限定条件

- **readonlyなcheckbox**：属性が付いているだけで読取専用とはならない。「全入力にreadonlyを付ける」案を棄却する材料。[HTML-READONLY](https://html.spec.whatwg.org/multipage/input.html#attr-input-readonly)
- **変更不可の識別子をdisabledへ置換**：送信が必要な値ならentry listから落ちる。値を固定する要件と送信から除外する要件は別入力にする。[HTML-DISABLED](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html)
- **aria-modal=trueの見た目だけのパネル**：背景の操作が残るなら宣言と挙動が一致しない。反対に非モーダルへ常時trapを追加するのも誤り。[ARIA12](https://www.w3.org/TR/wai-aria-1.2/#aria-modal)、[HTML-INERT](https://html.spec.whatwg.org/multipage/interaction.html#inert)
- **最初のボタンへ必ず初期フォーカス**：編集対象より前にreadonly欄やcloseボタンがある場合に目的を外す。HTML自身がこの例を扱う。[HTML-DIALOG](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-dialog-element)
- **disabledなら状態値は変わらない**：JSやradio群による変更は可能。DOM属性だけを業務の不変条件と誤認しない。[HTML-DISABLED](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#enabling-and-disabling-form-controls:-the-disabled-attribute)

## 4. 反証テスト案（未実行）

| ケース | 操作 | 合格条件 / 棄却条件 |
| --- | --- | --- |
| normal | buttonをpointer、Enter、Spaceで各1回起動 | 各経路の確定回数が1。keydown+clickによる2回実行は棄却 |
| unavailable | native/ARIA両方式で前記経路と公開ショートカットを試す | canExecute=falseで確定回数0。見た目のみの無効化は棄却 |
| readonly/payload | 同じname/valueのenabled、readonly、disabledをFormDataで比較し編集を試す | 前2者は他の送信条件を満たせば値が残る。disabledは除外。readonly checkboxを合格扱いしない |
| inherited-disabled | disabled fieldset内、最初のlegend内、legend外を比較 | 例外を無視する「全子孫同じ」判定を棄却。自身の.disabledだけで判定しない |
| modal / cancel | 開く→Tab/Shift+Tab→Escapeまたは取消→再表示 | 初期対象が意味に合い、背景のpage要素に進まず、取消が確定を呼ばず、DOMと状態が再同期する |
| invoker-removed | 開いた後に呼出元を削除し、閉じる | 指定の論理的なfallbackがactiveElementになる。復帰成功の空判定を棄却 |
| nonmodal-counterexample | showで開く→背景の入力へ移動→閉じる | 背景を操作でき、閉じても背景入力からフォーカスを奪わない |
| stale/state-change | 実行可能→不可→可能、開く→取消→開くを繰返す | 意味・DOM状態・実行ガードが一致。古いハンドラや非表示のaria-modalが残らない |

これらは仕様から導いた実装側の反証条件。特定ブラウザの合格実績ではない。Tabの判定はページ背後への漏れを検査し、ブラウザUIへの移動をページ部品と混同しない。

## 5. Art Directionとの重複と純増

| 再利用する既存ID | 再利用範囲 | 今回加えるもの |
| --- | --- | --- |
| E2-01〜06、E4-08〜10 | モーダル背景、Tab、初期/復帰フォーカス、キー操作の参照 | modal/nonmodal分岐、closeイベントとstate同期、invoker消滅・フォーカス奪取の反証 |
| G4-17、G6-12/24、G7-14、G10-13 | readonly適用型、disabled効果、fieldset例外 | availabilityの選択表、FormData結果と業務入力の結合、ARIA方式の実行ガード |
| G9-01/03/04 | button内容・type・起動条件 | 非送信type明示、Auto例外を誤一般化しない検査、二重起動の反証 |
| I-09〜11、I3-01〜06 | ライブラリの責任範囲、名前、初期focus、CSS状態 | ライブラリ採用後も確認するstate→DOM→操作→送信/復帰の観測契約 |

既存項目が無いとは主張しない。純増は仕様リンクの増量ではなく、入力・出力・例外・棄却条件を結び付ける契約である。I2のform-associated custom elementsの追加実装は今回不要。

## 6. 証拠・限界・再現

全9文書の正規URL、版、節、取得日、privateコピーの行・SHA-256は同階層の `researcher-1.json` に記録。全文転載なし。

- 実施：imozuru fetch.py 3本、3クエリを1バッチ検索、原文open/find、実リンク追跡3本。追加検索クエリ0。
- 取得失敗：3本ともDNS解決失敗。安全設定は解除していない。web表示の原文抜粋と元JSONはprivateだけに保存。**完全原文の取得成功は0件**であり、抜粋のSHAを原サイト完全原文のSHAとは呼ばない。
- 検索記録：ツールが返す8件全ヒットと3つの実クエリを保存。バッチ内の個別クエリへの帰属は公開されないため未確定として保持。
- 未確認：ブラウザ/AT実挙動、端末別focus設定、requestCloseやcommand属性等の配備可能性。規格掲載を実装済みと推定しない。
- 未探索：複合widget全般、入れ子modal、Shadow DOM/iframeの包括的検証、独自フォーム要素、業務の取消/保存ポリシー。
- 費用：金額、モデルtoken、AT成功率、飽和率は未測定。検索量と実行数だけを記録。
- 状態：研究根拠は提示済み。採用判定は親側のローカル実装検証後。skill unitの登録・実装・commit・pushは行っていない。

再実行した取得コマンドと追跡経路はprivateの `log.md`。保存場所は `/workspace/scratch/785c8ae49c7b/private-research/C/round-01/researcher-1/`。

