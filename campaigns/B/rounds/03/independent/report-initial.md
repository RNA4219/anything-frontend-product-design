# B Round03 — 独立Criticの初期評価

## 結論

**判定は REVISE。固定テストは13/13合格だが、初期候補の例示実装には成功結果を失う2つの欠陥と、入力の送信状態を誤解させる文言がある。** 原典から規則への移植は、今回確認した範囲で概ね妥当。AAA/AA、HTTP If-Match/AIPのetag、現在view/元operationの事実、実装fixture/本番保証の境界は明示されている。

この評価は同じモデルによる別コンテキストのレビューである。人間の独立評価、異なるモデルの評価、利用者の理解度や操作効率の実測、Skill適用の因果効果を意味しない。

対象は初期候補のみ。評価時に公開候補は変更していない。親による修正が始まった後の負例生成は、事前保存された初期snapshotを使用した。固定13ケースは変更・追加していない。

## 評価対象と得点

| 証拠 | 実結果 | 解釈 |
| --- | --- | --- |
| 固定 `test_resume_conflict.mjs` | 13/13合格 | 記録済みhashと同一の13ケースを独立実行 |
| HTMLの代表経路 | 8/8合格 | jsdom 26.1.0で候補HTMLのclick/changeリスナーを実行 |
| 限定した故障注入 | 4/4検出 | account guard、request epoch、結果/currentの混同、read失敗による成功消去 |
| 追加の状態プローブ | 5/6合格 | X03で後着pendingによる既知成功の退行を検出 |
| 追加のDOMプローブ | 0/2合格 | E01で再開後の成功消失、E02で送信済み内容の未送信表示を検出 |
| 原典保存hash | 11/11一致 | 今回8capture＋既存依存3captureをcanonical記録と照合 |
| Registry checker | エラー0 | 8単位・27source。構造と参照の検証であり内容の正しさを自動判定したものではない |

固定点数は **13/13** のまま保存する。探索で見つかった3件を後付けで固定分母へ追加せず、合格点からも消さない。初期候補の13/13から、改善効果や生成baselineに対する優越は導けない。

| 初期候補 | SHA-256 |
| --- | --- |
| `examples/resume-and-conflict.mjs` | `342471207d315e3d307232d1be7b0b796cf8d139dcdf22140d60f5a68103719b` |
| `examples/resume-and-conflict.html` | `fb10fccac3ab6e788e17e212e82b5306cbc970884a90998cc3cb4ddb120db2a7` |
| `references/resume-and-conflict.md` | `b025e9bdaaa365cd5daabe1a96cc36ccf38787af905a9e7a7f04316613dc4491` |
| `registry/B/skills/B-IU-007.json` | `315997657470ecca1d691168632476da3e63cb05f619222138a49801cd846700` |
| `registry/B/skills/B-IU-008.json` | `7cfd3bfa832dc6df341bdb31e799b2f0ff11f56be92ad8f230eb3d81b1c5c3ae` |
| 固定テスト | `f2f52bfe67da04a680299ed771581b25b6e0004325cfea6128f7b34c5e68289f` |

完全な対象一覧は `artifact-hashes.json`。freezeのbytesを照合したが、記録された時刻の外部証明は行っていない。

## 修正が必要な点

### F1 — 確認済み成功がsnapshot再開で失われる

**重要度: medium。例示実装の採用を止める。**

位置は初期 `examples/resume-and-conflict.mjs` 9、27–30、58–61、90行、およびHTML 27行のreopen処理。`outcomes` に保持した結果と `operationOutcome` / `operationResult` はcontroller内だけにあり、`snapshot()` は `record` だけを返す。

実HTMLの再現手順:

1. 「保存した作業を開く・照合する」をclickする。
2. 「変更内容を確認する」「確認した条件で更新する」をclickする。
3. 対象操作の成功と `My draft title` の結果表示を確認する。
4. 「操作記録を照会できない状態にする」をONにする。
5. 「保存した作業で画面を開き直す」をclickする。

観測結果は `phase=unknown`、`operationOutcome=null`、`operationResult=null`。画面の成功結果は消え、「操作記録から結果を確認できません」と表示される。操作番号は保持され、成立した更新は1回のまま。重複更新は観測していない。

これは、既知の成功がなかった場合の照会missとは条件が異なる。`B-IU-007:007-D06` は、既に別証拠で確定した結果をrecord欠落だけで取り消さないと明記している。required inputsにも既知の結果を含めている。この例では同じページ内で取得済みの成功をsnapshot境界で落としている。

修正は、現在operationに正しく相関した確定結果を、owner・target・operation・payload等の対応が分かる形でsnapshotへ含め、適用先が認める保持・信頼契約の下で復帰すること。保存値の存在を認証や権威の代わりにしてはいけない。今回のin-memory模擬保存を、安全な永続storageの実装として扱う必要はない。

証拠: `dom-events.json:exploratory.results[E01-CONFIRMED-SUCCESS-REOPEN-EXPIRED]`、実行コード `dom-events.mjs`。固定R10/R12はこの成功確認後の再開条件を試していないため、13/13合格と両立する。

### F2 — 保持した終端成功より古いpending応答を優先する

**重要度: medium。例示実装の採用を止める。**

位置は初期mjs 27–34、52–53、60、78行。古いviewに相関した確定結果は `retainOutcome` で保持するが、`accept` が現在のpending応答を扱う際、その保持済み結果を参照しない。

実行した応答順序:

1. 同じowner/targetの編集をreviewしてcommitする。update応答を保留する。
2. 同じoperationでresumeを開始し、lookup応答も保留する。
3. updateの確定成功を先に返す。updateのepochは古いため現在viewへ直接採用しないが、成功結果はoutcomesへ保持される。
4. 先に観測していた `pending` のlookup応答を後から返す。

観測結果は `phase=pending`、`operationOutcome=null`、`operationResult=null`。controllerが正しく相関した成功を受け取っていても画面は処理中へ戻る。この順序は、成功より前に観測された照会応答の通信だけが遅いケースであり、別operationや別accountの結果を混ぜたテストではない。

根拠は `007-D07`、`008-D07`、reference 74–86行の「view採用と正しく相関した結果の保持を分ける」規則と、元操作の確定結果を未確認へ退行させない既存R01の境界。Reactのcleanup例自体を終端状態の規範とはしていない。

修正は、現在operationについて既に受け取った確定結果を、後着のnonterminal/照会missより優先すること。現在viewへ採用できるかの判定は引き続き別に行い、別accountへ表示しない。単純にepoch判定を削ると旧read・別account応答の問題が再発する。相反する終端結果が届く契約は今回未評価であり、勝手な時間順序を追加しない。

証拠: `edge-probes.json:results[X03-TERMINAL-SUCCESS-VS-INFLIGHT-STALE-PENDING]`、`edge-probes.mjs`。X02ではA→Bで到着した成功を隠し、Aへ戻った時に再照会なしで復帰する対照が通る。問題は「保持機構が全くない」ことではなく、後着の状態への優先関係にある。

### F3 — 成功後にも保持入力を無条件に「未送信」と説明する

**重要度: low。状態の意味を伝える例として修正を要求する。**

位置は初期HTML 7行、および22–24行のrender。作業sectionの説明文は全状態で同じまま残る。正常送信が成功した後にも、その入力を未送信と説明する一方、同じsectionには対象操作の成功結果が表示される。

実行したのは通常のresume→review→commitのDOM経路。`phase=completed`、`operationOutcome=succeeded`、更新1回で、操作結果にも入力欄にも `My draft title` がある。このとき静的な未送信説明が残る。操作のdisabled状態は正しく、重複送信は発生していない。

影響は、利用者が「この値はまだ送っていない」のか「送った入力を控えとして残している」のかを画面から判断しにくいこと。draftオブジェクトとoperation payloadを内部で別にする設計自体は妥当だが、それだけでは表示上の意味は分離されない。

修正は、未送信・送信済みで結果未確認・成功確認済みの状態に応じた説明を表示し、送った内容を保持している場合はその意味を明記すること。単に問題の一文を消したことだけで表現の十分性を判断せず、状態と文言を併せて確認する。

証拠: `dom-events.json:exploratory.results[E02-SENT-INPUT-NOT-LABELLED-UNSENT]`。根拠はtask acceptance 1–2、B-IU-007のdraft/送信済みoperation区別、およびSKILLの事実と未確認情報を分ける要求。

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

## 実行方法と証跡

固定suiteは候補module pathを指定してそのまま実行した。DOM検証では候補HTMLを読み込み、単一のES module importだけを同じhashの実module factoryへ置換し、HTML自身のclick/changeイベントリスナーを動かした。モデル関数だけを呼んだ結果をDOM試験とは記載していない。

代表DOM経路は未送信復帰、account不一致、失効→同account再認証、readonly、競合→新review、応答喪失→同operation再open、成功後のcurrent-read失敗、操作結果/current観測の不一致。account不一致ではprivate値・操作IDのDOM除去とquery数が増えないことを両方確認した。

追加状態プローブにはA→B→Aの古いread、古いviewの成功結果の保持、現在read/lookup能力なし、対象不一致、review後の入力変更も含めた。X03の1件以外は合格。期待を満たす側の対照もあるため、すべてを拒否するだけの実装を肯定していない。

負例は初期snapshotに限定変更を加え、固定suiteを実行した。原本を変更していない。N01はR03/R09、N02はR08、N03はR11/R12、N04はR12を検出した。これらは意図的な故障の検出実績であり、未知の全欠陥に対する検出率ではない。

主要ファイル:

- `frozen-suite.json`: 固定13の独立結果。
- `dom-events.mjs` / `dom-events.json`: 実HTMLイベント、各click/changeのtrace、状態と文言。
- `edge-probes.mjs` / `edge-probes.json`: 応答順序等の追加プローブ。
- `independent-checks.py` / `independent-checks.json`: source hash、freeze、負例生成・実行。
- `negative-controls/`: mutantコード、各実行JSON、log。
- `registry-checker.json`: 構造検証の結果。
- `artifact-hashes.json`: 評価対象と初期snapshotのhash。
- `verdict.json`: 機械可読判定。

## 未検証と次の判断

実ブラウザは既報のPlaywright起動制約があるため試していない。制約回避は行っていない。jsdomの結果を視覚表示、レイアウト、実キーボード、支援技術、読み上げ、人間理解、WCAG適合の証拠にはしない。実identity provider、server認可、永続storage、HTTP adapter、関連resource transactionも未検証。

F1/F2/F3を修正後、初期結果を保持したまま、既知欠陥の限定再確認を行えばよい。必要な初期coverageと欠陥再現を得たため、新たな網羅探索や任意試験はここで増やさない。公開、skill install、PR変更は行っていない。
