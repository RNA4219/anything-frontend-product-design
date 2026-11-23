# 実画面観測プロトコル — 今回は未実行

この文書は再開用手順であり、実行証跡ではない。現在の環境ではブラウザ作業が制限されており、代替経路で再実行しない。許可された別の検証セッションで対象環境を決めて実施する。

## 観測前に固定する

- 課題・ページ・部品・状態ID、必要情報/操作ID、要求する前後関係、元の値。
- ブラウザ/OS/AT名と版、language、書字/scroll方向、CSS layout viewport幅高さ、zoomの種類と値、scroll位置、固定/浮遊層。
- 入力別mouse/touch/pen/keyboardの実施対象と、pointer/hover能力queryの結果。接続機器から実使用経路を推定しない。
- 例外候補region、内容、二次元性の理由、overflowの所有者。表以外の本文や操作は独立行にする。

## 同じ状態で採る観測

1. 通常幅で必要IDを一覧化する。状態を保存し、320 CSS px相当の縦scrollまたは256 CSS px相当の横scrollで同じIDへ到達する。長文、長いラベル、エラー、読み込み完了、menu/dialog表示を含める。
2. 代替・折り畳みがあるときは開く操作、移動先、元の値の保持まで記録する。スクロールバーの有無と保持結果を別にする。
3. DOM順、視覚順、Tab/Shift+Tabの実到達順、実ATの読み順を個別に残す。必要な前後関係、focusが完全に覆われていないかを観測する。順序差だけで不合格にしない。
4. 実効targetを同一状態のviewport CSS pxで測る。BCRは候補境界として扱い、clip/transform/fragment/overlap、子要素・label・event経路を確認する。点samplingは補助証拠とし全面の証明にしない。確定できなければgeometryを未対応/不確かとして残す。
5. 各不足対象の周囲の全targetを列挙する。scrollが変わった座標を混ぜない。例外対象も一覧に残す。同じ動作の重なり/unionやiframeが未解決なら本矩形モデルへ確定入力しない。
6. mouse/touch/pen/keyboardの必要経路を実際に操作し、focus/値/activation回数/業務結果を確認する。hoverなしの経路と機器切替を含める。
7. 200%文字拡大、固定層のfocus完全遮蔽、必要ならより厳しい部分遮蔽条件を別検査として記録する。reflow合格から自動転記しない。

## 証跡の最小行

`task_id / state_id / required_or_target_id / viewport / zoom / scroll / fixed_layers / input_method / environment_versions / expected / observed / evidence_ref / limitations / status`

観測できなかった行はNOT_RUN/BLOCKED/HOLD、再現した欠陥は位置・症状・根拠・影響・修正方法を残す。スクリーンショットからkeyboard/ATの成功を埋めない。HTML試作のブラウザ描画・操作は未実行であり、CSS指定寸法を実測結果にしない。
