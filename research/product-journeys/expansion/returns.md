# 返品期限と条件を調べる

各行の入口と終点は「表示された操作要素数／文字の矩形面積率／中央の最長余白（CSS px）」の順。— は計測対象外。[対象と方法](README.md)

| 条件 | 区分 | 判定 | 入口 | 終点 |
| --- | --- | --- | ---: | ---: |
| [Argos・PC](#returns-argos-returns-desktop) | 再訪 | 表示不可 | — | — |
| [John Lewis・PC](#returns-jl-returns-desktop) | 再訪 | 表示不可 | — | — |
| [John Lewis・スマホ](#returns-jl-returns-mobile) | 再訪 | 途中まで | 11／13.1%／58 | — |
| [LEGO・PC](#returns-lego-returns-desktop) | 再訪 | 表示不可 | — | — |

<a id="returns-argos-returns-desktop"></a>

## Argos（PC幅）

開始URLでAccess Deniedが表示され、返品条件を確認できなかった。

白地の上部にアクセス拒否の文言が表示される。

照合した表示　アクセス拒否

入口はアクセス制限、終点はアクセス制限。

[公式の入口](https://help.argos.co.uk/) · [前回の同じ条件](../walkthrough/returns.md#returns-argos-returns-desktop)

<a id="returns-jl-returns-desktop"></a>

## John Lewis（PC幅）

開始URLでHTTP/2プロトコルエラーとなり、返品条件を確認できなかった。

Edgeのページ到達エラーが中央に表示される。

照合した表示　接続エラー

入口は接続エラー、終点は接続エラー。

[公式の入口](https://www.johnlewis.com/customer-services) · [前回の同じ条件](../walkthrough/returns.md#returns-jl-returns-desktop)

<a id="returns-jl-returns-mobile"></a>

## John Lewis（スマホ幅）

顧客サービスからReturns & refundsを選んだ後、HTTP/2プロトコルエラーとなり、返品条件を確認できなかった。

入口は選択肢が縦に並び、終点はEdgeの到達エラー。

照合した表示　返品案内への接続エラー

記録した操作　タップ「Returns & refunds」

入口はサイトの画面、終点は接続エラー。

[公式の入口](https://www.johnlewis.com/customer-services) · [前回の同じ条件](../walkthrough/returns.md#returns-jl-returns-mobile)

<a id="returns-lego-returns-desktop"></a>

## LEGO（PC幅）

開始URLでアクセスがブロックされ、返品案内を確認できなかった。

白い画面に大きな赤い×印とブロックの説明がある。

照合した表示　アクセス拒否

入口はアクセス制限、終点はアクセス制限。

[公式の入口](https://www.lego.com/en-us/service) · [前回の同じ条件](../walkthrough/returns.md#returns-lego-returns-desktop)
