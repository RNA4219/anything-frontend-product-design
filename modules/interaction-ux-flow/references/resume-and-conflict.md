# 再開する作業と、現在の判断条件を結び直す

対象は B-IU-007 / B-IU-008。保存した入力、送信済み操作、現在の資源状態を分けて扱う。
リロード・再認証・競合からの復帰が発生したときに使う。保存API、認証方式、キャッシュや
React Effectの実装はCの担当であり、この手順がサーバー認可や安全な保存を保証するものではない。

## 必要な入力

| 入力 | 判断すること |
| --- | --- |
| 保存作業のowner・tenant・対象ID | 誰の、どの作業を復帰するか。保存値自体の信頼条件も確認する |
| 信頼できる現在identity・必要capability | 同一利用者か、今も閲覧・結果照会・変更が許されるか |
| 未送信draftと、実際に送った操作の参照 | 入力の復帰か、既存操作の結果照合か |
| 最終観測値・validator・観測時点 | 以前確認した内容を、現在確認済みの内容と混同しない |
| 現在の観測値と、判断に関わる変更項目 | どの比較・再確認が必要か |
| 条件付き更新・照会・保持期限の契約 | 不一致、結果不明、記録消失をどう判定するか |

同じoriginやtabに保存recordが残っていても、現在のログインaccountとの一致は分からない。
WHATWGの保存範囲の定義を認可の証拠にはしない。ownerを照合するBの設計判断と、実際に
アクセスを制御するバックエンドの責務を分ける。[S4][S5]

## 1. 復帰前に、現在の作業条件を確かめる

1. 現在identityと保存作業のbindingを照合する。accountや対象が違えば、旧作業のprivateな
   内容を新accountの画面へ表示・照会する前に止め、適切なaccount／作業への復帰経路を示す。
2. 認証が切れている場合は、保持契約の範囲で入力と元操作の参照を保つ。認証待ちだけから
   業務操作の失敗・取消・成功を導かない。再認証後にidentityと現在capabilityを確認する。
3. 閲覧、結果照会、変更に必要な能力をそれぞれ確認する。再認証できたことは、以前と同じ
   編集権限がある証拠ではない。許された次の操作だけを示す。
4. 確実に未送信のdraftなら入力と段階を復帰し、未保存と表示する。復帰だけで送信しない。
5. 送信済み／結果未確認なら、[B-IU-001/002](async-outcomes.md)へ同じ操作参照を渡す。
   記録の欠落・期限切れ・lookupのmissは、未適用の証拠にしない。

WCAG 2.2の2.2.5は、再認証後にデータを失わず活動を継続できることを扱う**AAA**の規準。
AA一般義務には読み替えない。今回の復帰手順はタスクの要件としても採用している。
Understandingは説明資料であり、特定の保存方式だけを要求してはいない。[S6][S7]

## 2. 競合を、入力を失わせず再判断へ戻す

1. そのAPIのvalidator契約を特定する。HTTP ETagはopaqueであり、文字列の大小や数値変換で
   新旧を決めない。HTTP If-Matchは強比較なので、weak値の `W/` を削って一致扱いにしない。
   `If-Match: *` は存在の条件であり、reviewした版の一致確認の代わりにならない。[S1]
2. 利用者が確認した対象・変更内容・具体validatorを対応付け、サーバーが更新を判断する時点で
   条件を検査する。クライアントだけで版を比べても、その後の変更は防げない。[S1][S2]
3. 更新の条件不一致が確定したら、利用者draftと観測した新しい値を残して比較へ戻す。
   条件を外す、`*`へ替える、新tagを旧payloadへ付ける、といった自動再送を復帰策にしない。
4. 最新readで、対象・金額・効果など判断に必要な事実が変わったら、影響するreviewを無効にする。
   [B-IU-006](forms-and-review.md)に従って新しい内容で選択を確定する。最新readの成功は承認ではない。
5. 新しい選択の確定後、そのpayloadとvalidatorで条件付き更新する。再び競合すれば比較へ戻す。
   送信後の未知結果や再送の判断はB-IU-001/002を使う。

手順3〜5のreviewと更新を結び付ける部分は、このCampaignの設計推論である。
Calendarの412後に再取得するsample自体が、人の再承認を要求する規範ではない。[S2]
判断に無関係な変更、利用者が明示的に選んだmerge方針、同時編集を処理する既存契約があれば、
毎回全画面を確認し直す必要はない。適用先で「判断に関わる項目」と処理方針を定義する。

HTTP If-Matchの条件不一致は通常、新しい変更を実行せず412になるが、既に適用された変更と
確認できる場合の2xx例外もある。未知の元操作と、新しく不一致になった要求を同一視しない。[S1]
AIP-154のresource.etag、ABORTED、認可エラー優先やetag省略規則もHTTPと混同しない。
AIPは設計指針であり、適用先serviceの実契約を別途確認する。[S3]

対象recordのvalidatorが一致しても、関連する在庫・予約枠・別recordまで成立しているとは
限らない。その保証には関連条件を扱うservice側の契約が必要になる。このSkillのfixtureは
複数resourceの原子的更新を検証していない。

## 3. 遅い応答を採用する条件を分ける

現在viewへの応答採用は、現在のaccount・対象・発行contextと照合する。古いreadを後から
採用して、新しく確認した値を巻き戻さない。同じAへ戻ったA→B→Aでも、古い発行が現在の
要求に対応するとは限らない。request世代や既存data layerの保証など、Cと実装方法を合わせる。
既存Art Directionの `references/g-state-forms.md#g-06`、
`references/d-interaction.md#d-38` / `#d-41` と重複するReact規則は追加しない。[S8]

一方、owner・対象・操作に正しく相関した確定結果は、古いviewで発生したという理由だけでは
無効にならない。現在viewへの適用と元操作の結果保存を分け、権限・保持契約に従う。
再開用recordには必要な確定結果の証拠も結び付けて保持する。operation IDだけを残し、
再照会の期限切れで既知の成功を失わせない。同じ操作の古いpending応答で確定結果を
上書きしない。保持する結果の真正性・相関・保持期限はserviceと保存方式の契約に従う。
この結果の保持は、現在の認証・権限を代替しない。現在の応答が再認証を求めた場合は、
既知の成功を内部に保持したまま必要なprivate表示・照会を止める。再認証と能力確認の後に
許された元結果へ復帰する。成功か認証待ちかを、一つだけ選ぶ排他的な状態にしない。

| 確認できたこと | 保持・表示する事実 | そこから導かないこと |
| --- | --- | --- |
| 操作時点の成功snapshot | その操作が成功した結果 | 現在の資源も同じ値のままである |
| 後から取得した資源状態 | そのreadで観測した値 | 過去の操作結果が失敗だった |
| 成功確認後に現在readが失敗 | 操作成功と、現在状態の照合失敗 | 操作をunknownへ戻す、新しく再送する |
| account変更後に旧応答が届く | 許可された範囲の元操作の証拠 | 新accountへ旧private情報を表示する |

これは操作結果と資源readが別の事実を返す契約に対する手順である。単一応答で必要な両事実を
権威的に確認できる契約なら、追加lookupを一律に要求しない。「現在」は最終観測の意味であり、
次の更新が起きない保証ではない。

## 試験と適用限界

`tests/test_resume_conflict.mjs`の固定13ケースで、未送信復帰、同じ操作の照合、account不一致、
再認証と権限差、serverでの条件不一致、再review、遅延応答、record消失、操作結果と資源観測を確認する。
`examples/resume-and-conflict.html`は操作可能なin-memoryの例である。

- この例の `canRead` は資源readと操作lookupの両方を許す契約。実serviceで能力が別なら分ける。
- 「保存した作業を再び開く」は同一ページ内のsnapshotからcontrollerを作り直す模擬操作。
  永続storage、実ログイン、信頼境界や保持期限の実装を検証したことにはしない。
- 固定13ケースはHTTPのweak／missing／wildcard adapter、関連resourceのtransaction、
  実ブラウザ・支援技術・人間の理解度を網羅しない。具体serviceへ適用するときはその契約を追加する。

## 原典

文書全体の規則を各原典の直接要求とみなさない。条件ごとの事実／推論、保存範囲とlocatorsはRegistryに保持する。

- [S1 RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) — §8.8.3、§13.1.1、§13.2.1、§15.5.13。B-S101。
- [S2 Google Calendar: Get specific versions of resources](https://developers.google.com/workspace/calendar/api/guides/version-resources) — conditional modification。B-S302。
- [S3 AIP-154](https://google.aip.dev/154) — etag、mismatch、permission precedence。B-S301。
- [S4 WHATWG Web Storage](https://html.spec.whatwg.org/multipage/webstorage.html) — §12.2.2、§12.2.3、§12.4.2。B-T402。
- [S5 OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) — authentication / authorization、Web Storage。B-T403。
- [S6 WCAG 2.2](https://www.w3.org/TR/WCAG22/#re-authenticating) — SC 2.2.5、AAA。B-S201。
- [S7 Understanding Re-authenticating](https://www.w3.org/WAI/WCAG22/Understanding/re-authenticating.html) — informative guidance。B-T401。
- [S8 React useEffect](https://react.dev/reference/react/useEffect) — cleanupと古いfetch応答。B-S303。操作結果保存への展開はCampaignの推論。
