# 部品とフォーカスの契約

## 1. 意図から要素を決める — C-UI-001

移動先がある操作は `a[href]`、画面内の実行は `button`、値の編集は適合する標準フォーム要素を先に検討する。非送信のbuttonには `type="button"` を明示する。現行HTMLの未指定typeはAutoで例外があるため、「必ずsubmit」とは一般化しない。標準buttonへ独自のEnter/Space起動を重ね、clickと二重実行にしない。

既存のcustom部品が意味・キー操作・フォーム参加を正しく担うなら再利用できる。要素を替える前に、必要な名前、役割、値、状態、実行ハンドラ、フォーカス担当を記録する。[HTML button](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element)、[HTML a](https://html.spec.whatwg.org/multipage/text-level-semantics.html#the-a-element)。Art DirectionのG9・I-09〜11の仕様一覧を再利用する。

## 2. 利用可否・編集可否・送信値を分ける — C-UI-002

| 条件 | 実装の選択肢 | 必ず確認する副作用 |
| --- | --- | --- |
| 実行不可、Tab順から外すことが目的に合う | 対応要素のnative disabled | FormDataからの除外、fieldsetの継承と最初のlegendの例外 |
| 実行不可でもTab順で理由に届く必要がある | 適合するbuttonのaria-disabledと共通実行ガード | ARIA自体は動作もTab順も変更しない。pointer・キー・公開ショートカット・送信経路を漏らさない |
| 編集不可、値を保ちたい | readonly対応のinput/textarea | checkbox等には効かない。name、checkedness等の別条件も送信に関わる |

利用不可理由と解除条件を、ポインターだけの説明へ閉じない。GOV.UKのdisabled回避方針をHTMLの禁止へ拡張しない。native disabledもJavaScriptからの値変更やサーバー権限を防がない。HTML disabledとaria-disabled=falseを矛盾させない。手組みpayloadにFormDataの規則が自動適用されるとは扱わない。

出典: [HTML disabledとentry list](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#enabling-and-disabling-form-controls:-the-disabled-attribute)、[readonly](https://html.spec.whatwg.org/multipage/input.html#attr-input-readonly)、[ARIA in HTML §4.2](https://www.w3.org/TR/2026/REC-html-aria-20260811/#requirements-for-use-of-aria-attributes-in-place-of-equivalent-html-attributes)、[USWDS Button](https://designsystem.digital.gov/components/button/#accessibility-guidance)、[GOV.UK Button](https://design-system.service.gov.uk/components/button/#disabled-buttons)。Art DirectionのG4・G6・G7を再利用する。

## 3. モーダルの開閉と画面復旧を分離する — C-UI-003

モーダル性は業務入力から受け取る。native dialogではmodalを `showModal()`、nonmodalを `show()` で開く。閉鎖は `close()` 等の閉鎖手順を使い、`open`の手動削除で代用しない。closeイベントで実装側のopen状態を同期する。前回のreturnValueを次回の取消へ流用しない。

custom/library実装では背景操作の抑止、スクロール制限、ARIA状態等の変更を記録し、すべての閉鎖経路で復旧する。復旧を「起動元が残っている場合」の中に置かない。フォーカス復帰の可否とは別に実行する。別のモーダルが残るケースは専用の層管理が必要で、単純に全inert属性を消す例へ一般化しない。

nonmodalにモーダル用の背景inertやフォーカストラップを追加しない。nonmodalの外で別作業をしている人を、閉じるたびに起動元へ戻さない。

出典: [HTML dialog](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-dialog-element)、[inert](https://html.spec.whatwg.org/multipage/interaction.html#inert)、[USWDS修正 #6786](https://github.com/uswds/uswds/pull/6786)。USWDSの報告は本試作での追試実績ではない。

## 4. フォーカスを動かす担当を一つにする — C-UI-004

初期・内容更新・終了について、対象、選定理由、担当、fallback条件を書く。native dialogの標準処理とautofocusで成立するなら、trapやEffectを重ねない。長文や構造化した導入なら内部見出し、不可逆操作ならより破壊的でない選択、入力なら意図した欄を検討する。これらは条件付き助言である。

native dialog自身にtabindexを付けない。APGの内部見出しへのtabindex=-1、Adobeのcustom wrapper例と混同しない。内容置換で現在の対象がなくなる場合は意味のある内部fallbackを指定する。有効なfocusが残る更新では奪わない。

閉じた後、ブラウザ/ライブラリが目的の復帰を完了したら手動focusを重ねない。起動元が削除・非表示・無効・inert等で利用不能なら、上流が指定した論理的な次対象へ移す。focus()を呼んだことではなく、実際のactiveElementで結果を確かめる。発話・スクロール・実機キー操作は別の観測として残す。

出典: [HTML dialog](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-dialog-element)、[APG modal条件と例外](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/#keyboardinteraction)、[USWDS #6703](https://github.com/uswds/uswds/pull/6703)、[Adobe #2763](https://github.com/adobe/react-spectrum/pull/2763)。Art Direction E2・I-09〜11を参照する。APGをWCAG規範本文として扱わない。

## 反証ケース

同じ部品で通常→利用不可→通常、開く→取消→再表示、起動元削除→閉鎖を試す。必要な値が送信から消える、別作業のfocusを奪う、背景制限だけが残る、操作が二重に実行される場合は修正する。実装しない機能に追加の状態機械を強制しない。
