# 製品評価票の記入例　予約変更

予約変更の試作A・Bを同じ7つの必須条件で判定する。下表は、確定操作の応答が途切れ、利用者が同じ変更を再試行したケース。環境はEdge、1280×800。

| 測定項目 | 事前の合格条件 | 案Aの実測 | 案Bの実測 |
| --- | --- | --- | --- |
| 再表示した予約の日付 | 12月10日 | 12月10日 | 12月10日 |
| 同じ変更が確定した件数 | 1回 | 2回 | 1回 |

日付は両案とも合格。案Aは同じ変更を二度確定しており、この必須条件を満たさなかった。7条件全体では案Aは4件合格・3件不合格で見送り、案Bは7件合格で試作の検証範囲では実施可。参加者の所要時間や使いやすさはこの記録からは分からない。[受入計画](../tests/fixtures/design-qa-evaluation/plan.json) · [観察A](../evidence/design-qa-evaluation/observations-a.json) · [観察B](../evidence/design-qa-evaluation/observations-b.json) · [判定スクリプト](../modules/design-qa-evaluation/scripts/check_evidence.py)
