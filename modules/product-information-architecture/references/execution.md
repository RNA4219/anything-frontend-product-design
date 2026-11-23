# 出力・検証・停止条件

## 4. 出力する

小変更は次の5項目を文章・表で返す。複数画面や自動検査では、[契約](plan-contract.md)に従って `brief.json` と `plan.json`（新規は契約1.1）にする。

1. **目標–要件–機能表**: ID、役割、完了条件、出典/仮定、必須性、対応機能。
2. **機能判断表**: 全要求の処置、優先度と根拠、統合先、依存・権限・保持の条件。
3. **IAと画面責務**: 正本、分類と属性、入口と行先、画面で行う判断、必要情報、段階的開示。
4. **引継ぎ**: Bへ操作・状態の設計箇所、Cへ部品/レスポンシブ/アクセシビリティ、Dへ評価課題、Art Directionへ同時参照・情報順序と維持する意図。
5. **検証と未確認**: 実行した検査、観察結果、仮定、役割ごとの残件。自作チェックと独立評価を区別する。

## 5. 検証してから渡す

このSkillディレクトリから実行する。checkerはPython標準ライブラリだけで動く。

```bash
python3 checks/validate_plan.py --brief /path/to/brief.json --plan /path/to/plan.json --output /path/to/result.json
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

機械検査は要件・ID・正本・依存・権限付き到達性・必須情報の存在を確認する。意味が正しい、ラベルが理解できる、実際に利用者が完了できるとは保証しない。

次に代表タスクで初回入口から目的情報へ辿り、正常系・異常系・境界条件を確認する。分類が不確かなら利用者のcard sortで仮説を得て、別の探索課題で行先の発見を確かめる。LLMを実利用者の代役と称さない。画面がある場合は実際に開き、必須情報の隠れとナビゲーションを確認する。

分類を比較するときは、候補に表示する属性、その順序、後続の操作、成功条件をそろえる。ラベルを比較するときは分類を固定する。候補の属性が重なる場合は、利用者が知っていて表示できる識別情報を確かめる。情報が足りなければ確定を保留できる経路を用意する。

[予約変更の共通課題](../../../tests/fixtures/booking-change.md)では、同じ予約を状態別・部屋別の入口から選び、確定後に対象の日時を読み直し、他の予約も照合する。次のコマンドはリポジトリのルートで実行する。元の時刻と予約番号が不明な場合は `--scenario unknown-time` を指定する。

```powershell
py -3.11 -X utf8 modules/product-information-architecture/examples/booking_choice.py --variant status
py -3.11 -X utf8 modules/product-information-architecture/examples/booking_choice.py --variant room
py -3.11 -m unittest discover -s tests -p test_product_information_architecture.py -v
```

[実行証跡](../../../evidence/product-information-architecture/execution.md)で、入口ごとの経路、取り違え、保留を照合できる。Bには対象IDと変更可否の条件、Dには成功・取り違え・保留の具体例を[担当間の受け渡し](../../../references/handoff.md)に沿って渡す。

問題は `location / symptom / basis / impact / correction / reproduction` を書き、`function / information_architecture / interaction / visual / implementation` を区別する。B/C/Dの問題をAの機能削除で解消しない。

## 6. 判断を止める条件

- 必須目標・要求・正本・権限の矛盾が残る: **HOLD**。場所と不足する事実を示す。
- 自動検査だけ通り、実利用または独立評価がない: **構造検査済み・効果未確認**。正式な品質PASSにしない。
- 削除が既存の業務・保持・契約へ影響するが根拠がない: 保持したまま候補を記録する。
- 意匠だけの変更: このSkillの機能再編を起動せず既存Art Directionへ渡す。
