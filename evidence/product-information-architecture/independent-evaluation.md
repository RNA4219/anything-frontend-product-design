# 独立評価

2026年11月23日。実装に参加していない別のエージェントに、以下の公開用の依頼、担当Skill、予約変更の共通課題を渡した。実装者のテスト、正答経路、事前の評価は渡さず、評価者は CLI のヘルプと出力から操作を組み立てた。エージェントによる架空の操作であり、参加者調査は実施していない。

> 公共施設の予約画面で、同じ工作室の予約を取り違えるという相談が来ました。変更対象を利用者が見つけられる入口を決めたいです。共通課題に沿って二案を実際に試し、どこまで判断できたかと、別の予約が紛らわしいときにも判断が成立するかを教えてください。調査に進むなら、どの疑問に何を使うかも短く決めてください。

## 初回の観察と修正

| 独立評価の指摘 | 修正と再評価 |
| --- | --- |
| 通常と同日の追加ケースは両案で完了したが、課題文に元時刻があるため、時刻が分からない場合を試せなかった。追加ケースの厳密な条件は同室・同日・同状態で、元時刻は異なる。 | `unknown-time` で同じ候補を使い、課題文から照合に使う時刻・予約番号を外した。両案で変更を保留でき、推測による確定を課題未達と判定した。 |
| 原典マップと実行証跡にたどり着けなかった。 | 参照先を追加し、最終版で両方へのリンクを確認した。 |
| Windows の既定エンコーディングではパイプ出力の日本語が崩れた。環境の `python` は実行エイリアスだった。 | Skillに `py -3.11 -X utf8` を記載し、ヘルプが読めることを確認した。 |

評価者が改めて独自に入力したWindowsでの再現例。

```powershell
$example = 'modules/product-information-architecture/examples/booking_choice.py'
py -3.11 -X utf8 $example --variant status --help
py -3.11 -X utf8 $example --variant status --scenario base --steps 'group changeable' 'open R-204' 'slot 12-10' confirm reopen 'group changeable' 'open R-204'
py -3.11 -X utf8 $example --variant status --scenario unknown-time --steps 'group changeable' 'open R-206' 'slot 12-10' quit
py -3.11 -X utf8 $example --variant status --scenario unknown-time --steps 'group changeable' 'open R-206' 'slot 12-10' confirm reopen 'group changeable' 'open R-206'
py -3.11 -X utf8 $example --variant room --scenario unknown-time --steps 'group workshop' 'open R-204' 'slot 12-10' confirm reopen 'group workshop' 'open R-204'
```

## 再評価の結果

- 変更元時刻が既知の通常と追加の2ケースを両案で、計4回完了した。確定前にR-204の前後を確認し、再表示後に12月10日14:00を読み直した。対象だけが変わり、終了コードはすべて0。
- 時刻・予約番号が分からないケースでは両案で対象候補が2件残った。一覧、または確定直前で止めると全予約が維持され、終了1、`deferred_without_change`。開始直後の終了も同じ結果になるため、照合して保留したことの確認には操作経路を使う。
- 推測でR-206を確定した場合と、偶然R-204を確定した場合は各1件の変更が記録された。いずれも終了1、`changed_without_identification`。予約通知の照合からの復帰と、画面での誤確定防止は未実装。
- 次の利用者調査では、候補のまとまりや語彙はオープンカードソート、最初の枝と回り道・到達はツリーテスト、識別情報が足りないときの判断や確定結果の読み直しは操作可能な試作で観察する、と評価者は判断した。

この評価から、分類による候補数の変化、選択前に読める識別情報、確定前後の結果を再現できた。入口の発見可能性や実利用者の選好は未確認。[実行結果](execution.md)
