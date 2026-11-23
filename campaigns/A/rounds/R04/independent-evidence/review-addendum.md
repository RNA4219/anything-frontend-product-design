# R04 修正確認

**R04-CR-001は修正版helperで解消を確認した。** 初回のREVISE判定・再現結果を変更せず、本追記と `correction-check.json` に別記録した。

| 項目 | 結果 |
|---|---|
| 出力とbeforeが同一path | INVALID_INPUT / exit 2、両入力bytes保持 |
| 出力がafterへのsymlink | INVALID_INPUT / exit 2、両入力bytes保持 |
| 出力がbeforeへのhardlink | INVALID_INPUT / exit 2、両入力bytes保持 |
| 別ファイルへの正常出力 | COMPARED / exit 0、両入力保持、保存JSONとstdout一致 |

通常例の結果は、初回凍結helperによる同入力の結果と完全一致した。修正版helperのSHA-256は `dbb31c82e2ffe6a2ec13e9f144e3ee80b93f07ca07d6592702fe42e6ce82e40b`。

初回凍結候補・匿名案生成の実験条件と、公開予定の修正版helperは区別する。初回helperのSHA-256は `2e5cc45b1a60c6760ca2ecdb5cf8b3dc6c8ef45bdc4ea5b980507fcb4cdbe7e4`。修正前の入力、期待、実結果、取得証跡は保持した。

確認はこの環境での4変形に限定する。実プロダクトの台帳、認可、索引、画面操作、人の探索成果を検証したものではない。同系モデルの独立スレッドであり、人間評価でもない。別の具体的未解決はなく、追加探索や試験は広げていない。

残件は匿名2案の受領と固定採点のみ。
