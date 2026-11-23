# B Round03 — 独立Criticの最終評価

## 結論

**判定は ACCEPT。B-IU-007/008の原典に基づく条件規則と、このfixtureで検証した再開・競合フローの範囲で採用可能。未解消の採用阻害指摘はない。** 初期候補では成功結果保持2件と文言1件を検出しREVISEにした。修正確認中に同じ成功保持処理の例外経路と、現在の再認証要求を覆う直接回帰を検出したが、最終修正版で解消を確認した。

固定ケースの独立得点は初期・最終とも **13/13**。探索で見つかった欠陥は固定得点とは別に記録した。13/13の同点を改善効果の証拠とせず、探索の欠陥→修正という工学的な確認結果だけを述べる。

同じモデルの別コンテキストによるレビューであり、人間や別モデルの独立評価ではない。候補の出典レビュー、実行可能な固定/故障注入/追加試験、実HTMLイベントを実施したが、利用者の理解度・操作時間・認知負荷を測ったものではない。

## 採用範囲と対象

| 対象 | 判定 | 範囲 |
| --- | --- | --- |
| B-IU-007 v0.1.1 | ACCEPT | 現在の主体・能力と作業を結び直す条件、入力/送信済み操作/既知結果の区別 |
| B-IU-008 v0.1.2 | ACCEPT | reviewとvalidatorの対応、競合からの再判断、操作結果/現在観測/現在認証の分離 |
| controllerとHTML例 | ACCEPT | この明示されたin-memory契約と、以下の実行済み経路 |

Registryの公開ステータスは、この評価時点では親の採否記録待ちでREVISEのまま。Criticは公開候補やRegistryを変更していない。

最終module SHA-256は `c5130db7bd10a48bb586f30c689a40089deae648c966c372c0bc6e4c95bd41a4`、HTMLは `84a92808062a8f903e2a64a9cb33041b367f9fcaff0102297cf6ce3f39779a9f`。全対象hashは `revised3/artifact-hashes.json`。初期hashと初期REVISE判定は `artifact-hashes.json`、`report-initial.md`、`verdict-initial.json` に保存している。

## 実行結果と評価段階

| 評価段階 | 独立実行結果 | 判定 |
| --- | --- | --- |
| 初期候補 `342471207d…` | 固定13/13、代表DOM8/8、故障注入4/4検出。追加状態5/6、追加DOM0/2 | REVISE。F1/F2/F3 |
| 修正1 `8a08e09d10…` | 固定13/13、代表DOM8/8、追加状態6/6、追加DOM2/2。修正箇所focused2/3 | REVISE。lookup通信例外にF2が残る |
| 修正2 `cc52cf64d5…` | 固定13/13、focused3/3。新しいauth優先回帰は不合格 | REVISE。F4 |
| 修正3 `c5130db7bd…` | 固定13/13、focused3/3、authority probe1/1 | ACCEPT。指摘した経路を解消 |

代表DOM8経路と追加状態6経路の全体再実行は修正1まで。修正2/3では、コード差分を読んだうえで変更されたcatch/authority分岐、復帰証拠の対応、状態別の実DOM文言と固定13を確認した。すべての過去試験を最終hashで再実行したとは報告しない。

固定テストhashは `f2f52bfe67da04a680299ed771581b25b6e0004325cfea6128f7b34c5e68289f`。固定criteriaは不変。freezeの記録時刻を外部証明したわけではない。

## 検出した欠陥と修正確認

### F1 — 確認済み成功のsnapshot再開での消失【解消】

初期mjs 9、27–30、58–61、90行、HTML 27行。成功結果はcontroller内部にのみ残り、snapshotがoperation参照だけを保存していた。

実DOMのresume→review→commit成功→操作記録失効ON→reopenで、更新は1回のまま `phase=unknown`、`operationOutcome=null`、`operationResult=null` へ戻った。`007-D06`の既知結果をrecord欠落だけで失わせない条件に反する。重複更新は観測していない。

修正はsnapshotへ現在operationの確定証拠をowner/resource/operationに相関して保持し、復帰時に対応を検査するもの。修正1の同じDOM手順で成功保持を確認した。最終修正でも保持コードは変わらず、RC02でowner/resource/operationの各不一致が採用されないことを実行確認した。保存物の真正性・保持期限・本番storage保証は適用先契約のまま。

証拠: 初期 `dom-events.json:E01`、解消 `revised1/dom-events.json:E01`、binding確認 `revised3/focused-recheck.json:RC02`。

### F2 — 保持済み成功と後着の状態/照会失敗の優先不整合【解消】

初期mjs 27–34、52–53、60、78行。同一operationのcommit応答を遅らせ、resumeによるlookupも並行開始。commit成功を先に返し、その後に古いpendingを返すと、成功はoutcomesにあるのにviewはpending/nullへ戻った。

修正1でacceptが保持済みterminalを優先するようになり、初期X03は合格した。隣接するresume catchの直接リスクを確認したところ、pendingでなくlookup通信エラーを返すとunknown/nullへ退行した。この同じ不整合も修正2で解消し、最終RC01で再確認した。

最終実装はcurrent viewへの採否を確認したうえで、同じoperationに保持されたterminalを古いnonterminal/照会通信失敗から守る。epochを削って全応答を採用する修正ではない。相反するterminalを正当化する実service契約は未検証。

証拠: 初期 `edge-probes.json:X03`、修正1の残欠陥 `revised1/focused-recheck.json:RC01`、最終 `revised3/focused-recheck.json:RC01`。

### F3 — 成功後の保持入力を無条件に未送信と説明【解消】

初期HTML 7行、22–24行。正常なcommit成功後も保持入力の説明が未送信のままで、同じsection内の成功結果と意味が競合した。controlsは正しくdisabledで、重複送信は観測していないが、表示だけでは未送信入力と送信内容の控えを区別しにくい。

HTMLは `input-status` を導入し、入力復帰だけでは更新しない状態、送信済みで結果を確認する状態、成功確認済みの状態を分けた。最終RC03では実click/changeイベントを使い、未送信復帰→応答喪失→reopenで成功確認→account Bへ変更の文言と非表示を確認した。単なる旧文章の削除だけを合格条件にしていない。

証拠: 初期 `dom-events.json:E02`、修正1 `revised1/dom-events.json:E02`、最終 `revised3/focused-recheck.json:RC03`。

### F4 — terminal優先の修正が現在のauth_requiredを覆う回帰【解消】

修正2 mjs 37–42、58行。現在epochの結果をcached successへ置換した後にauth_requiredを検査していたため、同じ並行update/lookupで成功→現在のlookup auth_requiredの順に返すと、再認証待ちにならずcompletedへ進んだ。private draft/operation/resultを表示し、追加loadも発生した。

このプローブは初期snapshotでは合格、修正2では不合格だったため、修正が導入した直接回帰として記録した。本番認証への侵入や実漏洩を証明したという意味ではない。

最終修正ではcurrent epochを確認した後、実応答のauth_requiredをterminal置換より前に扱う。成功は内部に保持し、再認証前はprivate viewと追加loadを遮断する。同account再認証後は保持済み成功へ戻り、新規updateも追加lookupも作らない。RC04でこの全経路を確認した。

証拠: 初期対照 `initial-authority-check/authority-recheck.json`、回帰 `revised2/authority-recheck.json`、最終 `revised3/authority-recheck.json`。根拠はtask acceptance4、007-D03/D04/D07の認証状態と業務結果の分離。最終referenceと008-D07にもこの境界が追記された。

## 原典から主張への照合


保存された原文の該当箇所を直接読んだ。研究者のfindings/Analystのunitsだけから正しさを推定していない。保存表現がweb抽出のPARTIALである箇所を全文HTML取得として扱っていない。

| 主張 | 実際に確認した原典位置 | 判定と境界 |
| --- | --- | --- |
| 再認証後の活動継続 | B-S201 WCAG 2.2 §2.2.5、web L837–L844。B-T401 L2/L20/L32–L59 | AAAと明示。Understandingはinformative。AA一般義務、無期限保存、特定window方式へ拡大していない |
| 保存域はaccount/権限の権威ではない | B-T402 §12.2.2/12.2.3/12.3.1/12.4.2、web L391/L439/L534–L537/L571–L574 | origin/windowと保持削除の記述を確認。account照合はtaskからの設計推論として分離 |
| 認証と認可は別 | B-T403 L484–L485、L512/L520/L523 | 同accountの再認証からwrite権限を導かない。server側の期限/認可責務をfrontend guardの保証へ変換していない |
| opaque ETag、強比較、wildcard | B-S101 §8.8.3–8.8.3.2、§13.1.1、web L1848–L1886/L2730–L2756 | 順序を推測しない、HTTP If-Matchは強比較、*は存在条件という区別を保持 |
| 判定時点、412/2xx、保証範囲 | B-S101 §13.1/13.2.1、web L2725–L2727/L2889–L2903 | 実行直前評価と通常検査優先、既適用時の2xx例外を保持。target validatorから複数resource transactionを導かない |
| AIP resource.etagの別契約 | B-S301原本Markdown 40–57、92–106、112–121 | ABORTED/他エラー優先、省略可能性、strong/weak許容を確認。HTTP If-Matchの比較規則と同一視していない |
| Calendarの再取得例 | B-S302 L65–L68/L93–L108/L121 | 412後のsummary再設定sampleとcalendarListの例外を確認。人の再承認義務はsampleから導かず、task/B-IU-006の適用とする |
| 遅いreadの採用 | B-S303 L73–L75/L380–L424 | cleanup例はread適用の例。server取消、認証境界、operation結果の永続性は導かない |
| 元operationの結果の意味 | B-S104 `operations.proto` 77–86、88–116、133–155 | result削除と取消、処理終了と成功を区別。今回のlookup/load schemaと保持優先はtask側の設計である |
| 保持期限後の結果不明 | B-T201 L12/L28–L35/L48–L52/L63–L69 | v1固有の窓・同じキー/内容・再起動をまたぐ参照保持。24時間や再送手法を全APIへ一般化していない |
| 確認内容の変更 | B-S205 L390–L396/L410–L430 | 既入力の復帰、必要な追加質問、最終送信の明確さを確認。review/validatorの結合は適用上の推論と明示 |

新規規則の多くは `campaign_inference` であり、RFCやWCAGの直接要求を過大に作り出していない。固定R08はopaque値の順序誤用を試すが、HTTP adapterのweak/missing/*全適合を実証するテストではない。この差はreference 94–98行とRegistry limitationsに残されている。

`canRead` はこのfixtureでloadとlookupの双方を含むとreference 94行に明記されている。これを認証一般の規則とせず、実serviceで能力が別なら分離する説明は適切。snapshot再開も同一ページ内の模擬であり、保存・認証・認可の実装保証は主張していない。

## 既存概念との関係

ローカルArt Directionの実ファイルを確認した。`references/g-state-forms.md` のG-06には古い応答、`references/d-interaction.md` のD-38には再取得による上書き、D-41には画面復帰と書込み競合の観点が既にある。B-IU-007/008はこれらを既知の実装導線として参照し、独自counter/Reactを新しい規範として要求していない。

PR2については保存済み `campaigns/B/existing-pr-overlap.json` と研究者・Analystの重複整理を照合した。対象PR head objectをローカルgitで読もうとしたが、objectが利用できずPR本文/全差分の独立再取得は完了していない。この限界を隠さない。候補の `relationship_to_existing` はdraft/reopen/If-Match/conflictを新原則と数えず、条件の形式化と反例の精密化としているため、今回その主張を強める必要はない。


## 実行方法、負例、再現コード

固定suiteを実moduleに対して独立実行した。DOM検証ではHTML自身のclick/change handlerを動かし、jsdomが直接実行しない単一ES module importだけを同じ候補のfactory参照へ置換した。モデル関数のみの結果をDOM試験と呼んでいない。

代表DOM経路は未送信復帰、account不一致、失効→同account再認証、readonly、競合→新review、応答喪失→同operation再open、成功後のcurrent-read失敗、操作結果/current観測の不一致。account不一致ではprivate値・操作IDのDOM除去とquery数が増えないことを併せて確認した。

初期snapshotに限定変異を加えた4負例はすべて固定suiteで検出した。account guard欠落はR03/R09、epoch欠落はR08、操作snapshotによるcurrent上書きはR11/R12、read失敗で成功消去はR12が失敗。これは意図した故障への検出実績であり、全未知欠陥の検出率ではない。公開候補は編集していない。

共有用コードは `reproduce-dom-events.mjs`、`reproduce-edge-probes.mjs`、`reproduce-negative-controls.py`、`recheck-focused.mjs`、`recheck-authority.mjs`。repo rootはcwdまたは `B_REPO_ROOT`、jsdomは `B_DOM_JSDOM_PATH`、出力先は `B_CRITIC_OUTPUT_DIR` で指定できる。再現手順は `REPRODUCE.md`。環境固有の初期コードと出力も変更せず残した。

Source hash/claim reviewは `sources-actually-checked.json` と `independent-checks.json`。今回8capture＋依存する既存3captureの11/11でcanonical hash一致を確認した。Registry checkerは最終8単位・27source、エラー0。構造検証をUXや事実の自動判定とは扱わない。

## 限界と終了理由

実ブラウザは既報のPlaywright起動制約により未実行で、制約回避を行っていない。jsdom 26.1.0の結果は、視覚表示・レイアウト・native keyboard・支援技術・読み上げ・人間の理解・WCAG全体適合の証拠ではない。

本番identity provider、server認可、永続storage、HTTP weak/missing/wildcard adapter、関連resource transactionは未検証。`canRead`のload/lookup兼用やsnapshot再開は明示されたfixture契約に限定する。APIに現在認証や保存証拠の真正性の保証を追加したと報告しない。

初期候補と修正途中の不合格証拠を保存し、最終の具体的変更箇所で既知欠陥が解消したことを確認した。意味のあるcoverageを得たため、新しい全般探索や任意試験はここで止める。公開・skill install・PR変更は行っていない。
