# Round 02 / Researcher-2 — 型付きトークンとテーマ契約

**結論：追加する価値があるのは、対応する型と構文、テーマ合成、公開する役割、出力名と参照先を明示して判定する契約である。** トークンの解決成功は、描画された色やアクセシビリティの合格を意味しない。調査日：2026-11-23。C-003 の限定的な判定器向け調査。

## 既存資料を再利用する範囲

Art Direction の I-01〜03 はCSS変数・面と文字の対・ライト／ダーク公開、B-01〜04 と B3-03/05/07/11/14 はコントラスト・端末設定・テーマ管理を扱う。これらを一般ガイドとして再利用する。templates/theme.html は Canvas/CanvasText と color-scheme を切り替え、端末設定へ戻す例であり、別名グラフや出力衝突を検査する実装ではない。

## 一次資料で確認した事実と、その限界

| 資料 | 確認した事実 | 読む箇所・版 |
| --- | --- | --- |
| [S1 Style Dictionary References](https://styledictionary.com/reference/utils/references/) | 出力から参照先をフィルター除去すると、別名を保った出力が壊れ得る。値変換後に元参照を復元することにも条件がある。 | outputReferencesFilter / outputReferencesTransformed。2026-11-23取得、パッケージ版未固定。 |
| [S2 Design Tokens](https://styledictionary.com/info/tokens/) | include と source は順序付きで合成される。意図的なテーマ上書きと誤った衝突は分ける必要がある。旧形式とDTCG形式を混同してはいけない。 | Overview note / Referencing / Collision warnings。ページはv4・旧形式の説明を含む。 |
| [S3 issue #1590](https://github.com/style-dictionary/style-dictionary/issues/1590) | 作者・利用者の議論で、テーマの意図的上書き、生成名の衝突、テーマごとの出力先の上書きが区別される。 | 2025-11-04開始。2026-08-27〜09-18コメント。最新リリースの対応完了を示す資料とは扱わない。 |
| [S4 issue #1398](https://github.com/style-dictionary/style-dictionary/issues/1398) | v4で寸法のvalue/unitオブジェクトが別変数へ展開された歴史的な報告。型と出力文字列の両方を検証する根拠。 | 2024-11-25本文、11-26・2025-01-20コメント。ページはClosed、修正版番号未確認。 |
| [S5 Spectrum styles](https://opensource.adobe.com/spectrum-web-components/tools/styles/) | 同じ意味トークンでも、ライト／ダークで参照先の番号が変わる。システム別に単独ファイル方式と基底＋上書き方式がある。 | Global tokens / Color options / Token imports。ページ表示 NPM 1.12.6。 |
| [S6 CSS Variables](https://www.w3.org/TR/2022/CR-css-variables-1-20220616/) | fallbackは利用先の型不一致を救済しない。fallback中の参照も循環に含まれる。別名は継承前に解決される。 | CR Snapshot 2022-06-16、§2.2–2.3、§3–3.1。 |
| [S7 CSS Color Adjustment](https://www.w3.org/TR/2025/CR-css-color-adjust-1-20251216/) | 強制色では使用色が変わり、shadowも消える。システム色と指定色の混用だけでコントラストは保証できない。 | CR Snapshot 2025-12-16、§2、§3.1。 |
| [S8 Spectrum Colors](https://spectrum.adobe.com/page/color) | 色の適用条件は前景・背景の対、透明度、テーマ、色以外のラベルに依存する。 | Solid color background / Two-tone color pairing。2026-11-23取得。 |

資料の事実から以下の局所ルールを提案する。全デザインシステムに同じ階層数・必須ロール一覧を強制する根拠は今回見つからなかった。

## 判定器に追加する契約と反証テスト

| 契約（提案） | 名前を付けた反例 | 失敗を判定する具体的なテスト |
| --- | --- | --- |
| 対応する構文・実効型・値形状・シリアライズ方法を固定する | dimension-object-split | 対応する寸法 {value:1,unit:px} は型を保持して1pxになる。未対応なら明確に拒否。value/unit分割、単位欠落、二重単位、objectの文字列化を合格にしない。[S2,S4] |
| 各テーマを合成してから独立に再解決する | dark-role-repoints | 本文→gray.900をdarkでgray.50へ変更し、期待値も変わること。darkだけの参照切れ・循環・型違いを失敗にする。[S3,S5] |
| 意図的上書きと出力衝突を別に扱う | hyphen-collapse-and-theme-overwrite | a.b と a-b が同じ --a-b になる場合を拒否。light/darkの出力先が同一なら拒否。宣言済みの基底→テーマ上書きは許容する。[S2,S3] |
| 出力に残す参照先を閉じる | filtered-palette-target | semantic.text→palette.ink の参照先を出力対象から落とす。別名を残すなら失敗、明示的に解決済み値を出すなら正値を検証。外部変数を許すなら別契約にする。[S1] |
| fallbackで型違いを隠さない | wrong-type-with-fallback | colorロール→dimensionを拒否。--x:16px; color:var(--x,red) を「redに復帰する」と判定しない。生のvar/calc/補間を実装しない場合は未対応として拒否する。[S6] |
| CSSのスコープを対応範囲として宣言する | ancestor-alias-freeze | 親でrole→baseを定義し子でbaseだけ変更しても、roleの再計算を保証しない。安全な限定実装では各テーマへ解決済みロール値を出力する。入れ子テーマはブラウザ未検証としてHOLD。[S6] |
| プロダクト側の必須ロール一覧を使う | all-tokens-resolve-but-text-role-missing | 存在するトークンがすべて解決しても、必須on-surfaceが無ければ失敗。基底からの継承を許すなら合成後の一覧で判定。[S5,S8] |
| グラフ判定結果と表示結果を分ける | shadow-only-focus-in-forced-colors | 型・名前が正しいテーマにshadowだけのフォーカス表示を付けても、WCAGや強制色対応の合格を出さない。機械レポートは検査した範囲だけを返す。[S7,S8] |

これらはテスト仕様の提案であり、この研究役は実装・実行をしていない。フォーマットの完全準拠、CSSのカスケード計算、表示コントラストは主張しない。単位をvar(--gap)pxのように文字列接続する実装にも、CSSトークンの置換と文字列置換が異なる境界テストを置ける。[S6]

## 見つけた／見つからない／調べていない

- **見つけた：** 参照を残した出力の欠落、意図的上書きと生成名衝突の差、寸法の型情報喪失の報告、テーマ別の別名変更、CSS fallbackと継承の限界。
- **見つからない：** 普遍的な意味ロール一覧・階層数、正常取得できた原文ファイル、issue #1398の修正版番号。
- **調べていない：** Fluent/USWDSのトークン資料の深掘り、最新版を導入した再現、ブラウザ実行、入れ子テーマの実表示、全DTCG形式／Resolver対応表。後者の仕様調査は補完する別研究役の担当。

## 実行記録と制約

初期検索は3本（Style Dictionary、Spectrum、CSS Variables）、一次資料の衝突確認で追加1本。初期の結合応答が大きく全ヒットを保存できていないため、検索記録の完全性は主張しない。追加検索9件の返却結果は保存した。

実際に実行した取得コマンド：

```sh
cd /workspace/scratch/785c8ae49c7b/imozuru
python3 skills/imozuru/scripts/fetch.py /workspace/scratch/785c8ae49c7b/private-research/C/round-02/researcher-2/sources style-dictionary-references https://styledictionary.com/reference/utils/references/
```

結果はDNS解決失敗、取得成功0件／失敗1件。保護設定変更や繰り返しの再取得はしていない。readerの部分抽出は原文と分けて保存した。コード内空白などが正規化される可能性があり、原文そのもの・完全本文とは扱わない。issue #1590からリンク66で#1398へ実際に移動して内容を確認した。

費用は不明。停止理由は委任された限定範囲の調査完了であり、飽和や網羅を主張しない。公開成果物に第三者全文を含めない。実装変更・登録・コミットなし。

