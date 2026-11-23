# 調査ログ

調査日 2026-11-23（JST）。論点と資料の対応は [原典地図](map.md)、確認した原文の版と位置は [原典台帳](sources.md) を参照。

## 0周目　媒体と用語

- 規格・英語用語からの検索役は WHATWG のフォーム、W3C の WCAG 2.2、WAI-ARIA、APG に到達した。radio group、focus order、status messages、reflow を記録。 [検索ログ](queries-standards.jsonl)
- 制作者・公開デザインシステムからの検索役は GOV.UK Design System team、USWDS team、Design Tokens Community Group、Stripe、AWS Builders’ Library に到達した。contribution criteria、override、theme token、idempotency を記録。 [検索ログ](queries-systems.jsonl)

## 1周目　本文の取得とリンクの追跡

- HTML Living Standard から 2026-11-22 の固定スナップショットへ。分冊 URL は 404 だったため固定版の一体文書と現行の該当分冊を取得。WCAG 4.1.3 から Understanding、ARIA22 の実例へ進み、フォーカスを移す画面切替と保留時の通知を照合した。
- GOV.UK の変更ガイドから Accordion と Step by step navigation の実例を開いた。本文から利用場面と制約を読み、共有部品の採用条件は Contribution criteria、局所的な変更の選択は Extending and modifying components の条件に戻した。公開元のフッターから OGL を確認。Web 検索ツールで OGL が 403 だったため、同じ URL を HTTP で取得して本文を確認した。
- USWDS の theme color から state color へ、DTCG の Aliases / References から連鎖解決へ進んだ。Stripe Advanced error handling から Idempotent requests、AWS 原典の遅延要求と異なる意図の扱いを確認した。
- エラー表示の実証研究を別に確認。HCI-1 は入力エラーの提示時機の比較に限って参照し、送信結果不明やアクセシビリティ適合の根拠にはしない。
- 調査役2名の探索は完了。論点5件に、今回の作例の採用・適用外の判断に使える原典が付いたため終了。検索入口は分野を分けており、検索集合の重なりによる飽和率は出していない。予約業務での利用者研究、スクリーンリーダーとブラウザーの組合せ、実サービスの並行更新は評価範囲外。
- 公開元の原文はローカルに保存。状態と取得経路、ハッシュは [取得ログ](fetch-log.jsonl) にある。
