# 調査ログ

## 0周目

- 規格・通信の探索役は SCXML、RFC 9110、Birrell/Nelson、AWS、Google Calendar、HL7 FHIR を調べた。SCXMLのイベントとガード、RFCの条件付き更新、RPCの呼び出し識別子を原典の候補にした。Googleのガイドから予約の原子的な枠切替までは確認できなかった。
- 実務・研究の探索役は NHS、GOV.UK、W3C、Wix、予約製品のヘルプ、待機表示の原著を調べた。旧枠と新枠の切替はWixのドラフト仕様、審査中・却下時・承認時の見せ方はNHSを候補にした。待機の長さに関する研究から予約変更の成功率は判断しなかった。
- 検索語と返った検索結果を [queries.jsonl](queries.jsonl) に保存した。複数クエリの結果が一つのリストで返った検索では、検索語をまとめて記録した。検索ヒット一覧には候補として表示された資料が含まれる。結論に使った位置は [原典マップ](map.md) に示した。

## 1周目

- SCXMLの概要から参考文献 “Harel and Politi” をたどった。旧リンクの転送先でHarelの著者ページを確認し、現在の業務設計への根拠は SCXML §3.5 と §5 に置いた。[著者ページ](https://www.weizmann.ac.il/math/harel/)
- GOV.UKの確認用パターンからDWPの導入事例、完了ページのパターンからGDSの再訪調査をたどった。前者の変更前確認の実例、後者の再訪集計に含まれる別要因を確認した。両パターンから公開例を開き、確認例の修正リンク、完了例の受付番号と次の手続を確認した。[確認の公開例](https://design-system.service.gov.uk/patterns/check-answers/default/)・[完了の公開例](https://design-system.service.gov.uk/patterns/confirmation-pages/default/)
- Wixの公開仕様から原典リポジトリを開き、予約変更の原子性、競合時のコード、原典ファイルとライセンスの版を確認した。[Wixリポジトリ](https://github.com/wix/universal-scheduling-protocol/tree/c941ac7409786acad6e61d7d51deeaf7479ade04)
- 初回取得で本文検査を通らなかったAWS PDFは公式HTMLで取得した。RPCの著者PDFはTLS証明書検証で失敗したため、UW–Madison公開の版を取得した。GOV.UK公開例は短いページだったため、HTMLを保存し画面固有の見出しを確認した。DWPの404は Check answers から元のリンクをたどり直して解消した。結果は [取得ログ](fetch-log.jsonl) に残した。
- Art Directionの固定版は読み取り専用で確認した。見本の実見、条件をそろえた比較、再現と出典照合の指示を [sankai](sankai.md) で対応づけた。

論点5件に一次資料の位置が付いた時点で探索を終えた。予約変更の利用者実験による効果、実ネットワークの性能、各サービスの内部実装は引き続き未確認。
