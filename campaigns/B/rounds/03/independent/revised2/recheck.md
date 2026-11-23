# R03 2回目修正版の限定再確認

**REVISEを継続。F2の照会通信エラー経路は修正済み。終端結果の優先処理が現在の再認証要求を覆い隠す直接回帰を検出した。**

評価module SHA-256: `cc52cf64d592ce78b9c473fb1a82858b9913885977705fae76c23e104b4edb41`。
HTML SHA-256: `84a92808062a8f903e2a64a9cb33041b367f9fcaff0102297cf6ce3f39779a9f`。

固定13/13、修正箇所のfocused RC01–RC03は3/3合格。RC01の通信エラー後も既知成功が残る。復帰証拠のowner/resource/op対応、状態別の実DOM文言も合格。

## F4 — 既知成功が現在のauth_requiredを上書きする

重要度medium、採用を止める。位置は修正版mjs 37–42行、58行。`accept` はcurrent epochを確認してから保存済みterminalへ `result` を置換し、その後で `auth_required` を調べる。この順序では、現在のlookupが伝えた認証失効を失う。

再現は同一operationに対する並行update/lookupの直接的な修正回帰確認であり、全般探索ではない。

1. 同じAの操作をreview→commit。update応答を保留。
2. resumeが同じoperationのlookupを開始。応答を保留。
3. 古いupdateの確定成功を返す。対応する成功がoutcomesに保持される。
4. 現在epochのlookupを `{status: 'auth_required'}` で返す。

期待は `reauthenticate`、private draft/result/operation IDをviewに出さず、認証前の追加private loadは0回。成功は内部に保持し、同account再認証後は元の成功へ復帰する。

実結果は `completed`、private draft/result/operation IDを表示、resource loadが初期1回から2回へ増加。APIが現在の認証要求を明示しているにもかかわらず、過去の操作成功から現在viewの許可を得てしまう。これは本番への侵入や実データ漏洩の証明ではなく、明示されたfixture契約内のtask状態の回帰である。

同じプローブを初期snapshotにも実行し、初期は合格・修正版は不合格を確認した。初期固定13の後付け得点には追加しない。

修正は、実際の応答がcurrent epochへ対応したことを確認した後、`auth_required` をterminal結果の優先処理より先に適用すること。確定成功を破棄せず、再認証後に再利用する。古いepochのauth応答で現在contextを止めない既存guardも維持する。

根拠はtask acceptance 4、B-IU-007 D03/D04/D07、referenceの認証状態/業務結果の分離。原典境界はB-T403 L484–L485/L512/L520/L523だが、この具体的優先順はtaskへの設計適用であり、OWASP自体のUI実装規範とは主張しない。

実行コードは `../recheck-authority.mjs`。証跡は `authority-recheck.json`、初期対照は `../initial-authority-check/authority-recheck.json`。以後の確認はこの直接回帰の修正に限定する。
