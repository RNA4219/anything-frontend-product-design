# B-R04 独立 Critic / Evaluator 報告

## 結論

**最終判定は ACCEPT_WITH_LIMITATIONS。初期候補に見つけた表示不一致 B-R04-C01 は修正済み。宣言された非原子的 fixture の範囲で、未解決の修正必須事項はない。**

固定13ケースと候補作成前の補足3基準を、この担当が独立に実行した。さらに、実際のHTMLのclick/changeハンドラをjsdomで動かし、項目別表示・API呼出し・操作参照・実際の模擬副作用を照合した。初期の代表7経路は通過したが、終端後の取消受付案内を対象に追加した探索2件が失敗したため、初期判定をREVISEとした。親担当のHTML修正後、関連する4件だけを再実行し、解消を確認した。

これは同じモデルの別コンテキストによる検証である。客観的な人間評価、生成ベースラインとの効果比較、実サービスでの保証を意味しない。

## 1. 評価対象と固定基準

対象は `campaigns/B/rounds/04/` のtask、cases、interface、両freeze、protocol-notes、analysis、B-IU-009、batch-outcomes、module SKILL/checklist、batch-flowのモデルとHTMLである。初期snapshotも照合した。最終評価対象のSHA256は `artifact-hashes.json`、初期記録は `artifact-hashes-initial.json` に残した。

| 対象 | 評価した版・結果 |
| --- | --- |
| 状態モデル | `7e303c30025abf6b92aa05b269fe83b9e289a61f581f533f06713a7fa58efd12`。初期から修正後まで不変。 |
| 初期HTML | `dc4922b346b1e7dade402e441bcb29f0fd72727ba6b9bdaef6dba379370891c4`。初期REVISEと失敗を保持。 |
| 修正HTML | `5207bee27be273599bbab14eeee7f90f7723db809866f9e7162c0aec0e570567`。終端後の取消受付文言のみ修正。 |
| 固定13 | `test_batch_flow.mjs` はtest-freezeのhashと一致。基準変更なし。 |
| 候補前補足3 | `test_batch_boundaries.mjs` はsupplement-freezeのhashと一致。A02は同一試行と新試行の2変種を含む1基準。 |
| Registry | v0.1.1の失敗モードと履歴を確認。14規則・procedureは初期snapshotと同じ。評価時のREVISE表示は親が最終判定を記録する前の状態。 |
| module入口・checklist | 親がレビュー中に更新したtriggerと条件付き確認項目を再読し、最終hashへ反映。実行モデル変更として数えていない。 |

補足3はAnalystの危険指摘後、候補作成前に別途固定されたものである。元の13に加算して「16ケースの当初基準」とは扱わない。追加探索もこれらと別枠にした。

## 2. 独立実行の結果

| 証拠の種類 | 結果 | 記録と解釈 |
| --- | --- | --- |
| 固定suite | 13/13 PASS | `frozen-suite.json`。親のtask-resultsを実行結果として流用していない。 |
| 候補前補足suite | 3/3 PASS | `supplement-suite.json`。A01同時retry、A02遅い結果、A03外部変更。 |
| 初期代表DOM | 7/7 PASS | `initial/dom-events.json`。実HTMLの操作経路。 |
| 初期DOM探索 | 1/3 PASS | 期限切れ照会はPASS。終端後の案内2件はFAILで保持。 |
| 修正後の限定DOM確認 | 代表2/2、探索2/2 PASS | `revised1/dom-events.json`。取消の未確定・成功終端・取消終端だけを再確認。 |
| module探索 | 4/4 PASS | `edge-probes.json`。固定suiteに混ぜない。 |
| 選択した故障検出対照 | 4/4を検出 | `fault-controls/summary.json`。網羅的mutation scoreやUX改善率ではない。 |
| 原典hash | 新規8件＋既存依存2件一致 | `source-checks.json`。実行結果とは別の保存整合性。 |
| R2のraw receipt照合 | 5/5 exact byte一致 | 原文の要約・再編集を使わず、保存対象ブロックと宣言された改行で比較。 |

モデルと両suiteが修正を通じて同じhashであるため、表示1箇所の修正後に全suiteをもう一度回すことはしていない。修正後の検査を初期の全DOM実行と混同しない。

### 実際に操作した経路と、副作用との対応

| 経路 | 実測した結果 |
| --- | --- |
| mixed → 最小待機時刻 → retry → lookup | 初回effectsはa=1,b=0,c=1。時刻だけ進めても新しい送信はなく、retryはbのみ。cは元requestIdのlookupで解決し、最終effectsは各1、全成功。 |
| 受付のみ → server側完了 → lookup | 項目結果のない初回は3件ともunknownで未完了。server側の効果が各1になっても、照合するまで全成功を表示しない。照合後だけ全成功。 |
| 1件成立後に応答喪失 → lookup → cancel → lookup | 初回は全行unknown、aだけ効果1。start/retryで全件再送せず、照合でa成功、b/c処理中。取消受付だけでは取消済みにせず、再照合で成功1・取消2の終端。 |
| dependency → 先行retry → 後続retry | 先行aだけが最初の再試行候補。a成功後にbが候補になり、明示操作でbのみを送る。最終効果は各1。 |
| 適用済みunknownへ取消 → lookup | cへの取消受付後もcはunknown、効果1を保持。元操作のlookupで成功になり、取消済みに変えない。 |
| failedだがunappliedの証拠なし | 実効果が成立していても結果はunknown。新しいretryは出さず、元操作のlookupで解決する。 |
| 空選択 | start/retry/reconcile/cancelからAPI呼出しなし。成功を作らず、効果は0。 |

各snapshotでは、DOMのsummaryとviewのmessage、行IDと状態ラベル、表示参照と元requestId、表示された模擬serviceの値と `getEffects()` / `getServer()` を照合した。`getCalls()` で対象subsetとlookup参照も確認した。受付だけの経路は実装上の状態名が **unknown** であり、pendingという状態値だったとは報告しない。

## 3. 指摘 B-R04-C01 と解消確認

**重要度：medium。初期判定：REVISE。最終状態：RESOLVED。**

| 項目 | 内容 |
| --- | --- |
| 位置 | `examples/batch-flow.html` の `render()`、初期版36行、取消受付の案内生成。 |
| 症状 | 元操作が成功または取消として照合済みでも、「受付確認・元結果は別途確認」が残った。 |
| 再現A | mixedで開始→取消→照合。cの状態はsucceeded、effects.c=1、cの照合候補は0だが、追加確認を促す案内が残る。 |
| 再現B | lostで開始→照合→取消→照合。b/cはcancelled、finished=true、照合候補0だが同じ案内が残る。 |
| 根拠 | `initial/dom-events.json` のEDOM02/EDOM03。B-IU-009 D12/D14に対応する、元結果・次の選択・終端表示の整合。 |
| 影響 | 結果が確定した後も利用者に未実施の確認があるように見える。副作用の重複、誤った全成功、成功結果の消失は観測していない。 |
| 修正 | acceptedの取消受付について、元操作が終端なら「受付確認・元操作の結果は確認済み」、pending/unknownなら元の別途確認案内を出す。 |
| 再確認 | DOM03/DOM05で受付時の未確定状態を保持し、EDOM02/EDOM03で成功・取消終端に追加照合の案内が残らないことを確認。実効果とlookup回数の境界も維持。 |

初期 `verdict-initial.json`、`report-initial.md`、失敗したDOM probeを削除していない。候補の失敗を隠す形で基準やsnapshotを変更していない。指摘の機械可読記録は `finding-B-R04-C01.json`。

## 4. 固定suite外の探索と故障検出

module探索では、次の具体的な残余リスクを限定して検査した。

- **遅い取消受付：** lookupで元成功が確定した後に取消受付が届いても、succeededと効果1が残る。
- **誤った項目・試行ID：** submit応答もlookup応答も正しい二つの識別が一致しなければ成功にしない。正しい元参照でのみ解決する。
- **未適用の裏付けがないfailed/blocked：** retryable=trueだけでは再送しない。実効果が既にあってもunknownから照合へ進む。
- **再試行の再失敗：** 時刻到達は自動送信や成功保証にならない。明示したbだけを送信し、再び未適用となったら新しい最小時刻を守る。aは後から明示した時点にだけ送る。

故障対照は、候補ファイルのprivateコピーだけへ意図的な誤りを入れた。元候補・固定suiteは変更していない。

| 対照 | 入れた誤り | 実際に失敗した基準 |
| --- | --- | --- |
| N01 | 最小待機時刻を無視 | B05 |
| N02 | 返信の到着位置で結果を割当て | B03、B09 |
| N03 | 取消受付だけでcancelledへ変更 | B11 |
| N04 | 確定終端を遅いpendingで上書き可能にする | A02 |

N04はA02の同一試行側で検出された。すべての旧試行競合や全種類の欠陥を検出できるという意味ではない。検出対照に候補を不利に見せる生成ベースラインを使っていない。

## 5. 原典の実読と適用範囲

研究者の要約だけでなく、新規8件の保存本文と既存S104/T301の該当箇所を読んだ。読んだ位置・hash・主張との対応は `source-checks.json` にある。

| 原典と読んだ位置 | 確認した境界 |
| --- | --- |
| B-S401 local 48,114–119,244–246,251–288,294–300 | Graphのidはbatch内相関。外側200は全成功ではなく、順不同応答もある。永続lookupや冪等性の保証へ拡張していない。混在例の成功はreadで、任意writeの独立commit証明ではない。 |
| B-S402 local 80–95,104–108 | Retry-Afterは待機条件。再度429になり得る。SDKの非batch/batchの違いを保ち、全HTTP送信への人の再確認義務にしていない。 |
| B-S403 local 175–183,248–251 | Graphの依存制限と、特定externalConnectionで503後にも作成される反例。任意DAG対応や全503の分類にはしていない。 |
| B-T501 web L82–L86,L129–L145,L151–L158 | AIP-233の元requests indexは正当な相関契約。禁止対象は到着順での推測。同期atomicと非同期の部分成功条件を区別。 |
| B-T502 web L10–L28,L285–L296,L386,L456–L463 | UnprocessedItemsとその補集合の解釈は、完全で有効な応答が前提。応答喪失を空mapへ変えていない。 |
| B-T503 web L7–L15,L234–L238,L450–L461 | all-or-nothingと個別診断を分離。全体失敗内のNoneを個別commitにしない判断は契約を組み合わせた推論。 |
| B-T504 web L43,L67–L81 | request_idの冪等性目的と寿命。fixtureの新attempt IDを論理キーの更新指示へ移していない。B-IU-002の安全な同一キーreplay例外を保持。 |
| B-T505 web L188–L190,L201–L202,L215–L227 | writeのHTTPエラーだけでは未適用と断定できない。診断Request IDと永続操作参照を分け、SDK差を保持。 |
| B-S104 proto 88–105,133–155 | 取消受付・元操作終端・成功の区別。fixtureのlookup/cancelが各vendorに実在する証明ではない。 |
| B-T301 web L41–L58,L63–L80 | 補償は成立済み作用に対する別処理で、失敗もあり得る。blockedの未実行を補償待ちへ変えていない。 |

R2の保存はraw HTMLや全ページの取得を主張していない。最初の研究者側比較FAILは既存の `verification-initial.json` に残っている。本担当も最初に、tool separatorを含めたまま全履歴refを連結する比較を試したため不一致となった。比較方法を実際の保存対象ブロックと区切りに合わせ、ブロック内を正規化せずに5件すべてのbyte一致を再現した。`source-check-attempts.json` にこの失敗手順と訂正を残した。原典bytesは変更していない。これは候補の機能失敗や修正回数ではない。

## 6. 限界と引継ぎ

本評価が実証したのは、固定された選択集合と宣言済み非原子的fixtureに対する動作、模擬サービスの呼出し・効果、およびjsdom内の実イベントハンドラと表示文言である。

実vendor adapter、実SDKの再試行、実認可・cross-account、永続保存・再読込復帰、原子的transactionの実行、任意依存graph、実ブラウザの描画・キーボード・focus・ARIA・支援技術、人間の理解や効率は検証していない。実ブラウザ起動の制約を迂回していない。fixtureがlookup/cancelを宣言していることと、それらが実APIに存在することは別である。

親が独立結果をRegistryやcampaign記録へ反映する際は、初期REVISEと修正後限定再確認を残し、固定13、候補前補足3、探索、故障対照を分離する。公開する再現スクリプトに原典captureや環境固有のprivate制御ファイルを埋め込む必要はない。手順は `REPRODUCE.md`。
