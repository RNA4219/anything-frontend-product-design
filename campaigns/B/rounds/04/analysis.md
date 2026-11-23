# B-R04 Analyst — 部分結果と項目単位の回復

## 結論

**B-IU-009を1件、DRAFT 0.1.0として取り出す。** 新規分は、原子性と完了契約の分類を入口に、固定した選択集合・相関・項目別の証拠・回復subset・集約表示を一つの判断手順へ結ぶことである。14規則を `units.json` のトップレベル `units` に収めた。unknown、安全な再送、取消、補償、復帰、reviewを新しい原則として再登録しない。

この作業はsankaiの**分解・理解・溶解**まで。再構築・Registry登録・候補実装・固定試験・公開は親の担当である。固定B01–B13への対応は提案であり、Analystは行動試験を実行していない。

## 1. 読んだ対象と版

sankaiの実ファイル `tooling/sankai/skills/sankai/SKILL.md` と `references/decompose.md`、`understand.md`、`dissolve.md` を読んだ。CLIとして実行していない。出力形式がMarkdown/JSONと指定されているため、HTMLは作らない。

対象はR04の二つの独立調査、固定task/cases/interface/test-freeze/test_batch_flow、既存B-IU-001–008、moduleのSKILLと4参照本文、PR2重複記録である。調査入力の検証結果は原典保存の整合性であり、アプリケーション試験の結果ではない。

| 原典ID | 直接読んだ箇所・位置 | 保存表現と限界 |
| --- | --- | --- |
| B-S401 | Graph JSON batching：local 48、114–119、244–246、251–285、294–300 | 公式repoのMarkdown全体を保存した調査。成功の混在例はreadで、任意writeのcommit/rollback契約を証明しない。 |
| B-S402 | Graph throttling：local 80–95、104–108 | 公式repo Markdown。429の待機・再試行とSDKの範囲。実SDKの実行ではない。 |
| B-S403 | Graph known issues：local 175–183／web L172–L180、local 248–251／web L245–L248 | webツール抽出。依存制限と503後に作成済みになる特定endpointの反例。 |
| B-T501 | AIP-233：web L82–L86、L129–L145、L151–L158 | 返却された抽出ブロック。同期/非同期、部分成功、元request index。全APIの規範ではない。 |
| B-T502 | BatchWriteItem：web L10–L15、L21–L28、L285–L296、L386、L456–L463 | 返却された抽出ブロック。非原子的batchとUnprocessedItems。個別条件付きupdateのadapterではない。 |
| B-T503 | TransactWriteItems：web L7–L15、L234–L238、L450–L461 | 返却された抽出ブロック。原子的処理、全体の冪等性、個別診断。 |
| B-T504 | AIP-155：web L43、L67–L74、L80–L81 | 返却された抽出ブロック。request_idの冪等性目的とAPIごとの保持窓。 |
| B-T505 | DynamoDB errors：web L188–L190、L201–L202、L215–L227 | 返却された抽出ブロック。writeの500、診断ID、SDK/client差。 |
| 既存B-S104 | Operation.done/result 133–155、CancelOperation 88–105 | 既存001/003の終端・取消判断を再利用。 |
| 既存B-T301 | web L41–L58、L63–L80 | 既存004の補償の範囲・失敗を再利用。 |

R1のcapture_fileは絶対パス、R2は `private/B/round04/researcher2/` を基準とする相対パスである。位置は原典内web lineと保存ファイルlocal lineを混同しない。R2の重複抽出ブロックは保存されたままで、同じweb lineが複数local lineに現れる。

原典8件のhash確認は親の `parent-source-check.json` にある。R1のverificationは保存/引継ぎ整合性PASS。R2は初回の比較手順で内部ブロック境界へLFを足したためFAILとなり、その記録を `verification-initial.json` に残している。原典を変更せずraw tool JSONと末尾の宣言済みLFを比較し直し、`exact-byte-verification.json` は5/5一致、訂正後verificationは146/146である。これを行動試験の合格へ読み替えない。

## 2. 分解 — この単位で取り出す仕事

受け取るものは、固定選択S、確認済み変更、API契約、項目別の観測、実在する回復能力である。返すものは、元Sに対応する項目台帳、実行時の回復対象集合、結果に忠実な集約である。

原子性分類、固定scope、結果相関、再試行subset、集約を別ユニットに分けると、たとえば原子的な失敗診断へ項目別再送を適用したり、欠落行をtotalから落としたりする。この依存を保つために1件へまとめる。一方、既存の一般的なunknown/retry/cancel/reviewを複写して独立スキルを装わない。

| 再利用する単位 | 接続する条件 | 今回の追加分 |
| --- | --- | --- |
| 001 結果の証拠 | 欠落、受付、照会、通信喪失 | 固定選択の全項目へ適用し、未解決行を落とさない。 |
| 002 安全な同一操作の再送 | retry/replay | 項目subsetと論理意図・各識別の対応。 |
| 003 取消 | 未確定項目の取消 | 適格な指定項目だけへ取消を限定する。 |
| 004 Undo/補償 | 成功済み作用を戻す場合だけ | blockedの未実行と補償を分ける。 |
| 005/006 修正・review | 回復で内容や判断が変わる | 元scope・成功履歴を保ち、必要な再判断へ接続する。 |
| 007/008 復帰・競合・旧応答 | actor、権限、版、応答contextが変化 | 元操作の結果保持と現在の項目試行への採用を分ける。 |

PR2の重複記録も確認した。元のunknown/同一意図/review等の概念は既存作業であり、今回の価値は条件付きの接続と凍結済み検査への対応である。PR2は変更しない。

## 3. 理解 — 原典が直接示すことと、設計上の推論

### 直接の事実

1. Graphではbatchの外側200が内側すべての成功を意味せず、内側応答順も要求順と一致しなくてよい。idはcase-insensitiveかつbatch内一意の相関値である。永続lookupを保証する値ではない。［B-S401:48,114–119］
2. Graphの429は項目別に扱い、その要求のRetry-Afterに従う。まとめて再試行する場合は対象群の最長delayを待てる。待っても再度429になり得る。［B-S402:80–95,106］
3. Graphのknown issueは、1要求の先行依存を単一の他要求および記載されたパターンへ制限する。また特定externalConnectionは503でも作成済みになり得る。［B-S403:175–183,248–251］
4. AIP-233の同期batch createは原子的、非同期は原子的/部分成功を選べる。部分失敗mapのキーは元requests配列のindexであり、server retryで成功し得る途中エラーを同mapへ入れない。［B-T501:L82–L86,L129–L133］
5. BatchWriteItemは個別Put/Deleteが原子的でもbatch全体は非原子的。UnprocessedItemsは未処理要求を示し、200内にも残り得る。完全な有効応答で未処理集合が空であることと、応答を失って集合を知らないことは違う。［B-T502:L10–L15,L285–L296,L456–L463］
6. TransactWriteItemsはall-or-nothingで、CancellationReasonsは要求順の診断である。Noneは個別エラーがないという記載であり、全体が失敗した際の個別commit成功とは読み取れない。後半の判断は二つの仕様を合わせた推論である。［B-T503:L8,L14–L15,L450–L461］
7. AIP-155のrequest_idは同一要求の冪等性を保証する目的で、resource IDとは別である。APIごとに有効窓があり得る。［B-T504:L43,L67–L74］
8. DynamoDBのwriteの500は成功/失敗のどちらもあり得る。応答Request IDは診断用であり、一部の高レベルSDKは未処理項目を自動再試行する。全SDK/clientで同じ挙動ではない。［B-T505:L188–L190,L202,L223–L227］

### 今回の設計推論

固定した利用者選択を返却行数から独立させること、結果台帳、実行時のeligible subset、finished/allSucceededの分離は、このCampaignの設計判断である。GraphやAWSがこのfixtureのview schema、利用者確認画面、itemId+requestId、lookup/cancel APIを要求しているという意味ではない。

`decision_rules` はこの接続を実行可能な指示文にした。D10のみGraph throttlingに限ったsource_guidanceで、その他は複数の事実と固定taskを接続するcampaign_inferenceとした。APIごとの直接要件は上の事実欄および各ruleの位置参照で区別する。

### 必ず残す判断境界

- **原子的API：** 項目別回復の非適用分岐。全体失敗内のNoneを成功にしない。応答喪失ではall-or-noneの可能性だけが分かり、all-unappliedへ飛ばない。
- **B03：** fixtureの順不同replyを到着位置で割り当てない。明示されたAIPの元index→選択ID対応は利用できる。
- **B05/B06：** unknownへ新attemptを作るfixture retryを許さない。一方、002の契約を満たす同一key・同一意図の安全なreplayと、既承認scope内のSDK継続は許容される。毎HTTP再送の確認義務を作らない。
- **IDの役割：** Graph batch id、AIP request_id、DynamoDB診断Request ID、fixture requestIdは同じ役割ではない。fixtureだけが相関とdurable lookupを兼ねる。
- **HTTP失敗：** 未適用の証明にならない。503後作成済みは特定endpointの反例であって、全503の結果規則ではない。
- **依存：** 初回batch内の依存処理と、blocked後のretry前提を分ける。固定B13は前提成功までretryを止める検査であり、任意DAGの実装許可ではない。
- **回復能力：** lookup/cancelがないAPIにendpointを発明しない。実在する経路が未確認なら、その操作だけを未提供/未解決に残す。
- **完了：** 成功、確定未適用、取消がすべて終端でも、全変更成功とは別。未知や未確定の効果が残る行を、単なるfailed文字列で成功または確定未適用へ丸めない。

## 4. 溶解 — 配置やAPI表現を変えても残す条件

| 元の具体形 | 維持する条件 | 変えられる範囲・要確認点 |
| --- | --- | --- |
| Graph responsesのid | 正しい要求と結果の相関 | wire形式は契約に応じて変換。case規則を他APIへ強制しない。 |
| AIP failed_requestsのindex | 元送信順への固定対応 | UIの並べ替えや到着順へ付け替えない。 |
| DynamoDB UnprocessedItems | 有効応答で確定した未処理subset | 個別成功行のない契約も扱える。応答喪失時に空mapを補わない。 |
| fixture itemId+requestId | 選択項目と該当試行の対応 | 別APIではoperation参照/冪等性キーを別に持てる。 |
| Retry-After / nextRetryAt | 最小待機条件と現在の適格性 | 時刻換算・backoffはC。成功予定時刻へ読み替えない。 |
| dependsOn / blocked | 前提未成立による未実行 | 実APIの依存形状と初回submit契約を保つ。成功済み作用の補償とは分ける。 |
| cancel receipt | 取消要求と元結果を分ける | 同期的に取消終端を保証するAPIなら追加pollは不要。 |
| total/counts/finished/allSucceeded | 元Sに対する忠実な件数と終端/成功の区別 | 表示形式は変更できる。Sの切捨て、欠落行の除外、成功の水増しはしない。 |

指示本文は `units.json` のD01–D14とprocedureである。解説だけを返したものではない。API・保存・権限・回復能力が未提示の適用先まで独立して実行できる完成スキルとは扱わない。

## 5. 規則と固定13ケースの対応

| 固定ケース | 主に対応する規則 | 観測対象 |
| --- | --- | --- |
| B01 混在結果 | D01/D05/D14 | 3状態、元total、実際の副作用。 |
| B02 envelope受付 | D01/D05/D14 | 受付から成功・完了を作らない。 |
| B03 相関 | D03/D04/D06 | 順不同replyと正しいID対応。 |
| B04 欠落 | D02/D05/D06/D07/D14 | 欠落行unknown、元参照・total。 |
| B05 retry subset | D08/D09/D10 | 最小時刻、指定と適格性、成功の非再送。 |
| B06 元操作照合 | D03/D07/D09 | 同じ参照のlookupとwrite回数。 |
| B07 mixed終端 | D05/D12/D14 | finishedとallSucceededの差。 |
| B08 空選択 | D02/D14 | submitなし、total0、成功捏造なし。 |
| B09 曖昧相関 | D04/D06 | 重複矛盾・未選択IDと台帳の保全。 |
| B10 応答喪失 | D02/D07 | start再操作と全件replayの抑止。 |
| B11 取消scope | D12 | 対象subset、receipt、元操作の終端。 |
| B12 回復後集約 | D07/D08/D09/D14 | 必要な効果だけ一度、結果と集約一致。 |
| B13 依存未実行 | D08/D11 | 前提成功前の抑止と成功後の明示retry。 |

すべて**PROPOSED_UNTESTED**。固定ケースを変更していない。D13の復帰/review/権限/競合は既存単位への接続であり、この13ケース内の新しい合格実績を持たない。

### 固定13の外に残る重要点

- **G01/G02：適用先への移植。** 原子的transaction、AIPの元index、完全なUnprocessedItems応答、vendor固有のID/lookup/cancel/SDKは未検証。固定fixtureから保証を広げない。
- **G03：同時retry。** 同じ適格項目への重なる呼出しで二重submitが起きないか。固定試験は逐次呼出しであり、この危険を直接検査しない。
- **G04：旧試行と確定後の遅い応答。** 旧requestIdや古いpendingが現在試行・既知終端を上書きしないか。B03/B09は十分な代替にならない。一般原則は007/008を再利用する。
- **G05：外部変更。** 呼出側itemsやview snapshotを変えても固定scopeと内部状態が保たれるか。interfaceの条件はあるが固定13の直接assertionはない。

G03–G05は親へ候補作成前の補足観点として連絡済み。後から固定基準へ追加せず、親/独立Criticが実行する場合も探索結果として分ける。

## 6. 境界・未確定事項・引継ぎ

Bが決めるのは、利用者の固定scope、item/taskの結果の意味、選べる回復、忠実な完了である。CがSDK/HTTP scheduling、時刻変換、chunking、data layer、focus/ARIA等を実装する。Dが人の理解・操作効率等を評価する。

今回の資料で必要な条件分岐を抽出できたため、追加調査は不要と判断した。欠落は実APIへの適用時に必要な契約入力であり、確認できていないendpointや保証を補完していない。

親への引継ぎは1ユニット・14規則・固定13への提案対応・追加未検証5区分である。新規原典は8件、既存原典の直接依存はB-S104/B-T301。原典写しは再配布しない。構造検査の結果だけを `verification.json` に記録し、候補の実行成績やUX改善を主張しない。
