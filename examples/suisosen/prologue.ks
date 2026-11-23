; 水葬線　序章（仮稿）
; 本文と選択肢をここで編集する。各ラベルは保存位置にも使う。

*platform
[bg storage="station"]
[speaker name="水守 澪"]
湖の底で、切符を切る音がした。手の中の受話器は、まだ一度も鳴っていない。[p]
[jump target="*call"]

*call
[bg storage="hero"]
[speaker name="業務電話"]
「水守さん。最終列車が遅れています。ひとり、まだ橋の上にいるんです」[p]
[jump target="*name"]

*name
[bg storage="hero"]
[speaker name="水守 澪"]
駅員は私しかいない。十二年前に沈んだ妹は、私を名字で呼ぶときだけ、少し笑った。今もそうした。[p]
[jump target="*ticket"]

*ticket
[bg storage="relief"]
[speaker name="受話器の向こう"]
「そっちの改札、開けてくれる？　今度はちゃんと、お釣りも持ってる」[p]
[jump target="*choice"]

*choice
[bg storage="hero"]
[speaker name="水守 澪"]
右手には赤い信号灯。左手には、妹の百円玉がまだ冷たい。[p]
[link target="*red"]赤い灯を振る[endlink]
[link target="*wire"]受話器を握る[endlink]
[s]

*red
[bg storage="station"]
[speaker name="水守 澪"]
橋の上へ、赤い弧をひとつ描く。列車は止まった。水の向こうで、小さな革靴が砂利を踏む。[p]
[jump target="*redEnd"]

*redEnd
[bg storage="relief"]
[speaker name="妹"]
「ただいま、お姉ちゃん」。改札を抜けたのは妹だった。制服の袖からこぼれた百円玉には、明日の年号が刻まれていた。[p]
[ending title="赤灯の岸"]

*wire
[bg storage="phone"]
[speaker name="水守 澪"]
「帰ってくるなら、何を食べたい？」。受話器の奥で十円玉がひとつ落ちた。列車は私の脇を通り過ぎた。[p]
[jump target="*wireEnd"]

*wireEnd
[bg storage="phone"]
[speaker name="妹"]
「お姉ちゃんの、焦げた卵焼き」。朝、台所に卵がふたつ置いてあった。どちらもまだ、掌より温かかった。[p]
[ending title="朝の食卓"]
