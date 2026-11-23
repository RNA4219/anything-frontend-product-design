# C-001 Round 01 — sankai分析

**結論：4単位に分ける。追加価値は、要素・利用可否・送信結果・モーダル終了・フォーカス担当を、条件と反証手順を伴う指示にすること。** 一般的なアクセシビリティ基準はArt Directionへ委任する。

## 方法と証拠の限界

sankai README、SKILL.md、分解・理解・溶解の参照を読み、仕事の切れ目で分解し、規範の強さと例外を原典のreader抜粋へ照合した。自動分解CLIは使用していない。指示本文は編集した実装提案で、規格の逐語引用ではない。版と参照位置はanalysis.jsonおよび両researcher JSONに記録。

完全原文のダウンロードは計8回すべてDNS解決失敗（成功0）。保存根拠はreaderの部分抽出である。ブラウザ・ATの追試とローカル実装テストは未実行。実装・登録・commitはこの分析の対象外。

凍結済み `campaigns/C/rounds/01/plan.json` を先に確認した。normal / unavailable / cancel / invoker-removed / nonmodal-counterexampleを維持し、以下の検証は未実行の反証案とする。親から、local Chromium起動時のsocket拒否、接続Browserのtimeout、cloudのdata URLのポリシー拒否によるBLOCKEDを受領した。回避策は試していない。純粋な契約検査を実行できても、未実行のbrowser/AT挙動候補はHOLDのままとする。

## C001-U1 — 意図から標準要素と動作担当を決める

**指示本文**

1. 移動先・操作・入力という意図と、フォーム送信の有無を受け取り、移動には a[href]、操作には button、入力には適合する標準フォーム要素を最初に検討する。非送信操作の button は type=button を明示し、送信操作は対応する type と form owner を記録する。
2. 標準要素で必要な意味と動作が満たせない場合に、既存ライブラリまたは独自部品を検討する。その場合は不足する機能と、名前・役割・状態、キー起動、フォーム参加、フォーカスを実装する担当を記す。外見の変更だけを独自widget化の根拠にしない。これは本分析の実装提案であり、native dialog 一律必須という規格ではない。
3. 要素・type・実行ハンドラ・委任する標準動作を一組で出力する。native button の既定起動に keydown 起動を追加するなら、一操作で二重実行しないことを示す。リンクに Space 起動を一律要求せず、a の disabled 属性だけで移動が止まると判断しない。

**使う場面・入力→出力：** 反復利用する操作・入力部品の作成または既存部品の統合時。 操作の意図と移動先 / フォームへの所属と送信目的 / 既存ライブラリと必要な対応環境 → 要素/type/form owner/起動担当の選定記録 / 標準機構から外れる場合の理由と不足責務。

**保持条件・例外：** HTML の意味と適用条件を保持する。ネイティブ利用だけをWCAG全体適合の保証としない。 業務上いつ実行できるかはU2の入力として受け取る。 現行HTMLのtype既定はAutoで、command/commandforと親selectの条件がある。USWDSの省略時submitという説明を全HTMLへ一般化しない。 既存の検証済みライブラリを外すことや、新しいcustom widgetを作ることを必須にしない。

**切り出す理由：** 意味と標準起動を決める仕事は、状態の業務判断やモーダル終了処理から独立して取り出せる。担当を定める部分は実装事故を防ぐための推論。

**変更可能範囲：** クラス名、スタイル、フレームワーク、ハンドラの配置は同じ観測動作を保つ範囲で変更可能。 要素やtypeの変更は意味・キー起動・フォーム効果を再確認する。

**依存・未確認：** art-direction/references/g-state-forms.md# g9-01, g9-03, g9-04; art-direction/references/i-components.md# i-09, i-10; C001-U2（利用可否またはフォーム値があるとき）。未確認: 対象ブラウザとライブラリ版の統合結果。

**反証案（未実行）：** [normal] buttonをpointer・Enter・Spaceで各1回起動し実行回数1と非意図のsubmitなしを確認する。リンクはEnterと標準の移動操作を確認する。 棄却条件: 実行不能・二重実行・意図しないフォーム送信。

**出典：** [HTML-ANCHOR](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-a-element) / [HTML-BUTTON](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) / [WCAG22](https://www.w3.org/TR/WCAG22/) / [R2-S2](https://designsystem.digital.gov/components/button/#accessibility-guidance)

## C001-U2 — 利用可否と編集可否を送信値まで接続する

**指示本文**

1. canExecute、editable、利用不可理由、解除条件、説明への到達方法、Tab順に残す要否、保存/送信する値を上流から受け取る。これらが同じ意味だと仮定せず、各状態についてDOM属性・実行ガード・期待する送信値を一行に対応づける。
2. 利用不可で、順次フォーカスから外す判断と送信から除外される効果が要件に合う対応要素にはnative disabledを選ぶ。fieldsetによる継承と最初のlegendの例外を含めた実効状態で判断する。属性がfalseという文字列でも存在すれば無効であり、disabledがJSやradio群による値変更まで防ぐとは扱わない。
3. 利用不可でもTab順での発見性が必要な適合するbuttonではaria-disabled=trueを選択できる。ARIA自体はフォーカス順も実行も変更しないため、通常のフォーカス可能性を保ち、公開するpointer・キー・ショートカット・送信等の実行入口を共通canExecuteで抑止する。説明をポインターだけの経路に閉じない。
4. 編集不可の値を保持する場合はreadonly対応の入力型等を選ぶ。checkbox/buttonにはreadonlyを効くものとして付けない。表示値・DOM value・送信値を区別し、disabledならentry listから除外、readonlyだけでは除外されないことを期待値に反映する。ただしname、checkedness、submitter等の他の参加条件も満たす必要がある。対応するreadonlyとnative disabledは制約検証からも外れるため、検証参加と送信期待値を並べて記録する。
5. HTML disabledとaria-disabled=falseを矛盾させない（規格上の禁止）。同義のtrueを重ねないことは規格の推奨として扱う。通常の送信を再現するAPI選択はArt Direction G7-05/G7-25へ委任し、ボタンの無効化のみでフォーム全体の全経路を止めたと推定しない。

**使う場面・入力→出力：** 利用不可・読取専用・送信待ち等の状態を持つ操作/入力部品。 canExecute、editable / 理由、解除条件、説明の到達方法、Tab順要件 / serializationPolicy、form owner、name、値、送信経路 → 状態→DOM属性→公開実行経路のガード→検証参加→送信期待値の対応表。

**保持条件・例外：** 理由や保存/取消ポリシーをCで創作しない。 ARIAの無効状態はフォーカス可能な子孫にも及ぶため、広いコンテナへ付ける場合は対象範囲を確認する。 利用不可理由と解除方法はUSWDSの製品ガイダンスを基にした設計提案。HTMLの一律要求として表示しない。 GOV.UKのdisabled回避は同設計システムのユーザー理解に関する指針であり、HTML disabledの禁止ではない。 aria-disabledによる発見性を全コントロールの義務にしない。 native disabledと独自保存処理は別機構。手組みpayloadにnative FormDataの除外規則が自動適用されるとは仮定しない。

**切り出す理由：** 実行抑止だけを切り出すと、値が送信から落ちる副作用と理由への到達可能性を失うため一つの仕事にまとめる。全公開経路の共通ガードは仕様の逐語要件でなく実装提案。

**変更可能範囲：** native/ARIA方式はTab順・説明・送信契約を再評価して変更可能。 理由文や業務条件は上流仕様に従い変更可能。

**依存・未確認：** C001-U1; art-direction/references/g-state-forms.md# g4-17, g6-12, g6-24, g7-05, g7-14, g7-25, g10-13。未確認: 対象製品で無効操作をTab順へ残す必要性。 ネイティブ以外の送信パイプラインが保持する値。

**反証案（未実行）：** [unavailable] 選択したnative/ARIA方式でpointer・Enter・Spaceと公開ショートカット/送信入口を試し、canExecute=falseの確定回数0と説明到達を確認。可能→不可→可能も確認。 棄却条件: どれかの公開入口で実行する、または説明に到達できない。 [readonly_payload] 同一の参加条件のenabled/readonly/disabledのFormDataを比較する。fieldsetの最初のlegend内外も対象実装で使うとき確認する。 棄却条件: readonlyとdisabledを同じ送信契約と扱う、適用外readonlyを有効扱いする。

**出典：** [HTML-DISABLED](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#enabling-and-disabling-form-controls:-the-disabled-attribute) / [HTML-READONLY](https://html.spec.whatwg.org/multipage/input.html#attr-input-readonly) / [ARIA-HTML](https://www.w3.org/TR/2026/REC-html-aria-20260811/#requirements-for-use-of-aria-attributes-in-place-of-equivalent-html-attributes) / [ARIA12](https://www.w3.org/TR/wai-aria-1.2/) / [R2-S1](https://design-system.service.gov.uk/components/button/#disabled-buttons) / [R2-S2](https://designsystem.digital.gov/components/button/#accessibility-guidance)

## C001-U3 — モーダル終了処理を復帰先の成否から独立させる

**指示本文**

1. dialogModeと開閉・取消・確定ポリシーを受け取る。native dialogを使う場合は接続済み要素をmodalならshowModal、nonmodalならshowで開く。open属性の手動除去で閉じたことにせず、close等の実際の終了経路とcloseイベントでDOMとアプリ状態を同期する。利用するAPIの配備可否は別途確認する。
2. cancel要求と実際のcloseを区別する。取消が阻止されて開いたままなら終了済みにしない。各表示回の結果を識別して、古いreturnValueや前回の確定状態を今回の取消へ流用しない。何を確定/保存するかは渡された業務ポリシーに従う。
3. 標準modalの背景制限はブラウザへ任せる。既存ライブラリ/独自modalを使う場合は、背景操作の制限・公開状態・キーによる退出を誰が管理するかを決め、aria-modal=trueだけで動作が成立したとは判断しない。
4. 実際に閉じる全経路で、このmodalが加えたinert/aria-hidden/イベント制約等を元の状態へ戻す処理を、呼出元探索やfocusの成功条件の外で実行する。既存属性を無差別に消さない。残るmodalがある場合はその制限を維持するが、今回の資料はスタック全体の実装を保証しない。
5. nonmodalへ背景inertやmodal用Tab循環を適用しない。終了後の行先はU4の条件で判断し、背景の別作業へ移動した利用者からフォーカスを奪わない。

**使う場面・入力→出力：** modal/nonmodalを開閉する部品の統合、取消、再表示、呼出元消滅を扱うとき。 dialogMode / cancelPolicyと確定結果 / 既存の背景状態と所有レイヤー / 利用可能なnative/library API → 開く→要求→実際のclose→背景復旧→状態同期の経路と担当 / 各経路の取消/確定結果。

**保持条件・例外：** nativeとcustomの責務を分ける。ネイティブ機構に重複する背景制約を機械的に足さない。 外側復旧とfocus復帰を分離することはUSWDS事故から導いた実装提案。 closeしていないcancelイベントでは終了後処理を実行しない。 ほかのmodalや元来必要な非公開状態まで解除しない。 custom fallbackは対象環境・既存ライブラリの要件を根拠として選び、native dialogの規格上の禁止と取り違えない。

**切り出す理由：** 終了処理が呼出元存在の条件内にある実装事故を防ぐ境界。焦点の行先がなくても外側の復旧を完了できる。

**変更可能範囲：** state管理方法、ライブラリ、close結果の表現は同じ終了条件を満たす範囲で変更可能。 取消可能性と確定処理の変更は上流の業務判断を要する。

**依存・未確認：** C001-U4（フォーカスの選定と復帰）; art-direction/references/e-accessibility.md# e2-01, e2-02, e2-03, e2-05, e2-06; art-direction/templates/dialog.html（例。業務ポリシーの既定値ではない）。未確認: requestCloseやcommand等の対象環境での利用可否。 入れ子modal、Shadow DOM、iframeをまたぐ包括的挙動。

**反証案（未実行）：** [cancel] 開く→対応する取消ボタン/Escape→再表示で、取消に確定効果がなく、DOMと状態が一致し、終了時に所有した制限が戻ることを確認。 棄却条件: 取消で確定、古い結果の再利用、閉じた後に背景制限やopen stateが残る。 [invoker-removed] 開いてから呼出元を削除し、ボタン閉じ/Escapeを各経路で試す。背景の操作と公開状態の復旧をfocus結果と別々に観測する。 棄却条件: 呼出元検索失敗で復旧が飛ぶ。 [nonmodal-counterexample] show等でnonmodalを開く→背景inputへ移動→閉じる。 棄却条件: 背景が操作不能、またはそのinputからfocusを奪う。

**出典：** [HTML-DIALOG](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-dialog-element) / [HTML-INERT](https://html.spec.whatwg.org/multipage/interaction.html#inert) / [ARIA12](https://www.w3.org/TR/wai-aria-1.2/) / [R2-S4](https://github.com/uswds/uswds/pull/6786) / [R2-S3](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/#keyboardinteraction)

## C001-U4 — 初期・更新・終了のフォーカス担当を一つにする

**指示本文**

1. 初期focus、内容更新後の保全、終了後の復帰それぞれについて、選定理由と移動を実行する担当を一つ定める。native dialogではブラウザのfocus手順とautofocusを初期候補とし、アプリEffectやtrapの自動focusを重ねない。
2. 初期対象は内容から選ぶ。長文/構造の導入を読む必要があれば内部の静的見出し等、不可逆の確認ではより破壊的でない選択肢、通常の入力では期待される入力対象を検討する。APGの条件付き助言を必ず先頭button/Tab対象という一律規則へ変えない。
3. native dialog自身にはtabindexを付けない。直ちに操作する内部対象がなければHTMLが示すdialog自身のautofocusを検討する。APGの内部見出しへのtabindex=-1や、Adobeのcustom wrapper fallbackをnative dialogへのtabindex指定へ転用しない。
4. 内容全置換で現在のfocus対象が消える場合に限り、現在のmodal内の意味のあるfocus可能なfallbackを選ぶ。Tab移動可能な要素がゼロでもfocus可能な対象はあり得る。残っている有効なfocusを更新のたびに奪わない。
5. native dialogを閉じるとブラウザが以前のfocusへ復帰を試みる。modalだった場合、または現在のfocusが内部の場合に復帰手順が働く条件を保つ。ブラウザ/ライブラリが目的の復帰を達成したら手動focusを重ねず、呼出元が消滅/非表示/無効/inertで復帰不能な場合や上流が別の次作業を指定した場合に、指定された利用可能な論理的対象へのfallbackを担当レイヤーが行う。
6. 復帰結果は実際のactiveElement等で確かめる。nonmodalの外で別作業をしている場合には、常時呼出元へ戻す処理を適用しない。ブラウザUIへの移動と背後のページ部品への漏れを区別し、ATの発話を全環境で厳密に一回にする保証を作らない。

**使う場面・入力→出力：** modalの表示、内容全置換、終了にfocus移動が伴うとき。 内容と操作結果 / initialFocusTargetと選定理由 / returnFocusFallbackまたは次の作業対象 / ブラウザ/ライブラリ/アプリの担当境界 → 各focus遷移の対象・理由・担当・fallback条件 / 観測されたfocusと未検証のAT条件。

**保持条件・例外：** 背景復旧はU3が担い、focus失敗で止めない。 一担当化と成功確認は実装事故からの工学的提案。APGをWCAGの規範本文と呼ばない。 APGは呼出元消滅以外にも、完了結果に続く次作業が自然な場合の別対象を認める。 nativeが以前のfocusを記録することと、任意の論理的な起動元へ必ず成功して戻ることは同じではない。 内容更新がない部品へ動的fallback実装を追加ゲートとして強制しない。

**切り出す理由：** 初期・復帰・更新で同じ複数担当の競合が起きるため、移動の所有権を一仕事として抽出する。特定ライブラリのfooter先頭やwrapperを既定値にはしない。

**変更可能範囲：** 初期対象、復帰先、担当レイヤーは内容・業務フローに応じて変更可能。単一担当と各例外は保持する。 autofocusやfocus APIの選択はnative要件を守り観測で確認する。

**依存・未確認：** C001-U3; art-direction/references/e-accessibility.md# e2-02, e2-03, e2-04, e2-05; art-direction/references/i-components.md# i-09, i-11。未確認: 対象ブラウザとATの発話、スクロール、focus挙動。 dynamic replacement後のnativeと採用ライブラリの具体的差。

**反証案（未実行）：** [normal] 開いた直後の対象、移動の担当、導入の可視性、Tab/Shift+Tabで背後ページへ漏れないことを確認。 棄却条件: 意味に合わない対象、競合する二重移動、背後ページへの漏れ。 [invoker-removed] 呼出元を除去して閉じ、指定fallbackが実際のfocus対象か確認。 棄却条件: 無効な元要素を成功扱い、fallback不在。 [content-replacement] 全置換する実装で、focus中の要素をTab対象ゼロの内容へ置換し、意味のある内部対象がfocusを受けるか確認。 棄却条件: bodyや背後へ脱落。

**出典：** [HTML-DIALOG](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-dialog-element) / [R2-S3](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/#keyboardinteraction) / [R2-S5](https://github.com/uswds/uswds/pull/6703) / [R2-S6](https://github.com/adobe/react-spectrum/pull/2763)

## 調査間の照合

| 論点 | 判断 |
|---|---|
| buttonの既定type | USWDSの一般説明より、HTMLのAutoとcommand/select条件を保存。非送信type明示という設計提案は共通。 |
| disabledとaria-disabled | GOV.UKの回避方針は製品ガイダンス。native利用も、適合要素でARIA+スクリプトも可能。同義trueの重複回避はSHOULD NOT、falseとの矛盾は禁止。aria-disabled自体によるTab追加はない。 |
| native/customの復帰 | HTMLは以前のfocusへの条件付き復帰手順。APGはmodalの論理的復帰先ガイダンス。native成功時の手動二重focusを不要とし、利用不能や業務上の次対象にはfallbackを残す。 |
| dialogのtabindex | native dialogには禁止。APGの内部静的対象やAdobeのcustom wrapper例は別対象。 |
| form submission | R2は未調査、R1がentry-listのdisabled除外とreadonly非除外を補完。全readonly値の無条件送信や手組みpayloadへの自動適用は言えない。 |
| フォーカス発話回数 | 複数担当の競合防止は採用候補。PRのAT結果を本環境の実績や全環境での一回発話保証にしない。 |

R1は3検索語・1検索呼出で規格の境界を確認し、R2は9検索語・5検索呼出で公式製品ガイダンスと修正事例を追跡した。後者の障害報告は当事者の実装記録であり、本分析の追試結果ではない。結合検索結果の個別検索語への帰属は不明、R2初回は転記、飽和率・金額・モデル原価は未測定。分析での追加検索は0。

## 既存参照との分担

| 既存範囲 | 判断 |
|---|---|
| E2-01〜06 / E4-08〜10 | 一般的な名前・キー・背景・focus要件は参照再利用。差分はnative/custom分岐、close同期、復旧の独立、focus担当、反例。 |
| G4-17 / G6-12,24 / G7-05,14,25 / G9-01,03,04 / G10-13 | 属性・API仕様の網羅一覧を再作成しない。差分は上流の利用可否・Tab順・送信期待値を同じ行へ結合する手順。 |
| I-09〜11 / I3-01〜06 | ライブラリ責務とCSS状態の一般説明を参照。差分は担当を固定し観測可能な結果にする契約。 |
| I2 form-associated custom elements | 今回は追加実装せず。独自要素の包括的フォーム参加へ一般化しない。 |

## 対象外と残る判断

汎用WCAG一覧、外観基準、独自フォーム要素、複数modal・Shadow DOM・iframeの包括的実装、互換性表、業務ポリシー新設は含めない。担当や背景復旧を決める指示は、特定ライブラリの具体的なDOM配置から取り出せるが、ネイティブ要素の禁止条件は外せない。

対応ブラウザ/AT、利用不可理由と解除条件、Tab順の要否、保存/取消方針、復帰先は適用先の入力として残る。これらは未提示情報であって、新しい承認条件ではない。4単位は必要な依存と一緒に利用する指示候補であり、独立Skillの実装・登録や汎用性の証明を行ったものではない。
