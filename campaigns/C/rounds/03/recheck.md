# SESSION C round 03 — 修正後の独立再検査

## 結論

**純粋な入力モデルprecheckは限定採用（ACCEPT）を提案する。C-UI-008とC-UI-009のUnit全体はHOLDを維持する。** 修正版に初回と同じ127ケースを、同じ入力・同じ期待値・同じ検査sourceで適用し、127一致・0不一致となった。初期の9不一致・4欠陥群はすべて再現ケース上で解消した。

初期 `critic.md` / `critic.json` のREVISE判断と、`initial-results.json` の失敗出力はそのまま保持した。この文書が修正版への追加判断である。

## 何を同じ条件で再検査したか

| 項目 | 初期 | 修正版 |
| --- | ---: | ---: |
| 異なる入力ケース | 127 | 127 |
| 期待と一致 | 118 | 127 |
| 期待と不一致 | 9 | 0 |
| Critic独立作成 | 124 | 124 |
| 親発見巨大指数の再現 | 3 | 3 |

ケースID、入力bytesのSHA-256、期待値object、検査sourceのSHA-256が一致した。初期不一致の9ケースだけを別の緩い期待値へ差し替えていない。初回一致の118ケースも引き続き一致した。初期のUnicode出力bytes採取2回を含めたCLI総起動は256回だが、異なる検査ケース数は127である。

修正版 `layout.py` SHA-256：`453e5e072fee99dcf412ea475aca278094b6405de53e4d0d8f79581e8e237c24`。

検査source SHA-256：`49ca022700f7c533ab3acd3958da8930d7b4f821d80639255aa0fed83d20275f`。

実行前後に候補hashの変化はなかった。初期との差分は `layout.py`、`test_layout.py`、`references/layout-contracts.md` の3ファイルだけで、親が説明した修正範囲と一致した。Criticは実装を編集していない。

## 4群の修正確認

| 初期指摘 | 修正後の実結果 | 関連する反対条件 |
| --- | --- | --- |
| C03-CR-01：UA片側矛盾をHOLDへ消し込む | `author_resized=true`だけ、`ua_determined=false`だけでも`MODEL_FAIL`。例外は`CONDITIONS_CONTRADICT_CLAIM` | 成立可能だが片側不明の条件はHOLDのまま。条件が整った例外も実質審査のHOLDを維持 |
| C03-CR-02：既知欠落を空refでHOLDへ消し込む | `availability=missing`は空/空白refでも`FAIL_REQUIRED_ITEM_LOST`。`evidence_ref_present=false`を別欄に保持 | `unknown`と必須item未提出はHOLDのまま |
| C03-CR-03：巨大指数の未捕捉例外 | 正指数・負指数・ゼロ指数の3入力は`INPUT_ERROR`、終了値2、Tracebackなし | 既存の有限値・数値上限・型検査も同じ127ケースで再確認 |
| C03-CR-04：孤立surrogateの出力破損 | high/lowとも有効UTF-8 JSON。decode後のcontext IDは入力と一致 | `MODEL_PASS`は入力モデルの関係だけで、`ui_status=HOLD`、WCAG未評価、実行フラグfalseを維持 |

修正に直接関係する出力確認を含む18の補足assertionも一致した。補足確認は保存済み初期/再検査結果を読み直したもので、新しい画面観測やCLIケース数には加算していない。補足コードとactual/expectedは `recheck.json` の `postcheck_source` / `postchecks` に残した。

## 限定採用の範囲

採用を提案するのは、`C-layout-model/1` で供給された入力の形式、明示的な保持・例外申告、同一座標系に属すると申告された充填軸平行矩形の正確な幾何precheckである。24/23.999、対角接触、円と全実矩形、幅広薄型、例外targetの障害物保持、不明形状、自己/循環同等target、不正条件型、局所reflow例外などは同じ検査集合で維持された。

証拠参照や例外理由の文章が本当に正しいか、矩形が実hit areaと一致するか、周辺targetの一覧が完全かは、このprogramは認証しない。この範囲を超えて採用すると、供給された申告の整合性を実画面の成功として読み替えてしまう。

## Unit全体のHOLDが必要な理由

実ブラウザの320/256における情報・操作保持、HTML試作の描画と実activation、DOM/視覚/Tab/AT順、focus遮蔽、実効target、実入力切替、文字拡大、AT発話が未観測である。合成モデル、持込測定申告、browser_observedという文字列のいずれでも、実行証跡は生成されない。したがってC-UI-008 / C-UI-009全体のHOLDは、今回の純検査成功と両立する。

source/Art Directionの照合と独立性の限界は初期 `critic.md` のとおりである。同一基盤モデルの別タスクであり、別モデルや人間による外部再現ではない。第三者原文は公開ファイルに転載していない。ブラウザ、サーバー、CDP、UI操作、DOM double、ATは起動しておらず、拒否された操作を別経路から行っていない。

## 再現

```sh
python3 campaigns/C/rounds/03/independent-probes.py --allow-revised --output recheck-repeat.json
```

出力先は新しいファイル名を使う。既存結果への上書きは検査器側で拒否する。全入力とactual outputsは `recheck-results.json`、対象全hash・初期ファイルの保存hash・補足確認・採否は `recheck.json` にある。
