# 原典索引 — Product Design / Information Architecture

確認日: 2026-11-23。20件を採用。原典の主張を下に要約し、Skillで導いた実装契約と区別する。原典の全文は同梱しない。各原則の Sources からも直接開ける。

種別の区別: 公式ガイド/専門家の方法論は助言、実証研究/本人の調査は記載条件での観察である。複数の文献があっても、このSkill全体の効果が検証されたとは限らない。

18Fは旧公式文書の保存版。Kierasは1997年版と同一視せずV2公開原稿を参照。Feature Fatigueは刊行誌の書誌を確認し、本文の主張は公開working paper版で確認。WAI supplementalはWCAG適合の必須条件ではない。

<a id="s01"></a>
## S01 — 6.2 Requirements Management — NASA Systems Engineering Handbook

- **URL**: [6.2 Requirements Management — NASA Systems Engineering Handbook](https://www.nasa.gov/reference/6-2-requirements-management/)
- **該当箇所**: 6.2.1.2.3 Conduct Expectations and Requirements Traceability / 6.2.1.2.4
- **確認日 / 種別**: 2026-11-23 / official_method
- **原典の主張** (author_guidance): 親要件と子要件を双方向に追跡し、親要件の未充足、追跡漏れ、受け入れ可能な自己導出要件、過剰要件を区別する。
- **制約・版・未確認**: システム要件管理の方法。UI機能の自動削除アルゴリズムではない。元の審査制度を小さなUI変更へ一律追加しない。
- **接続する原則**: A02, A03。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s02"></a>
## S02 — User stories — 18F

- **URL**: [User stories — 18F](https://guides.18f.org/methods/decide/user-stories/)
- **該当箇所**: How to do it
- **確認日 / 種別**: 2026-11-23 / archived_official_method
- **原典の主張** (author_guidance): 利用者・目標・理由を表し、見積り・開発・テスト可能な単位へ分け、受入条件を付ける。
- **制約・版・未確認**: 旧公式文書の保存版。1 story=1画面ではない。非機能制約を全てこの書式に押し込まない。
- **接続する原則**: A01。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s03"></a>
## S03 — Design hypothesis — 18F

- **URL**: [Design hypothesis — 18F](https://guides.18f.org/methods/decide/design-hypothesis/)
- **該当箇所**: What / How to do it
- **確認日 / 種別**: 2026-11-23 / archived_official_method
- **原典の主張** (author_guidance): 出荷した機能と意図した成果を区別し、仮説と観測指標を結び、結果で修正する。
- **制約・版・未確認**: 統計的合格値・自動昇格条件を規定しない。
- **接続する原則**: A02, A10。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s04"></a>
## S04 — Make research actionable — 18F

- **URL**: [Make research actionable — 18F](https://guides.18f.org/ux-guide/research/make-research-actionable/)
- **該当箇所**: Insights into action / Making decisions based on the research
- **確認日 / 種別**: 2026-11-23 / archived_official_method
- **原典の主張** (author_guidance): 調査からstory・ticketへ追跡し、影響と労力を比較する。サービス提供側の影響や少数者の文脈も検討する。
- **制約・版・未確認**: 低労力だけの優先や高労力な必須機能の削除を正当化しない。
- **接続する原則**: A04。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s05"></a>
## S05 — Task flow analysis — 18F

- **URL**: [Task flow analysis — 18F](https://guides.18f.org/methods/decide/task-flow-analysis/)
- **該当箇所**: Why / How to do it
- **確認日 / 種別**: 2026-11-23 / archived_official_method
- **原典の主張** (author_guidance): 目標ごとのシナリオ、利用者/システムのタスク、判断点、依存を明示し、利用者/専門家と辿る。
- **制約・版・未確認**: タスクモデルの箱をそのまま画面に変換する規則ではない。
- **接続する原則**: A01, A07。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s06"></a>
## S06 — Card sorting — 18F

- **URL**: [Card sorting — 18F](https://guides.18f.org/methods/validate/card-sorting/)
- **該当箇所**: How to do it / Open card sort / Closed card sort
- **確認日 / 種別**: 2026-11-23 / archived_official_method
- **原典の主張** (author_guidance): 自由分類では利用者のグループ・名称・理由を得る。既存分類への割当にはclosed card sortを用いる。
- **制約・版・未確認**: 分類の理解は実画面の探索成功やタスク完了を証明しない。普遍的なカテゴリ数上限はない。
- **接続する原則**: A05, A10。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s07"></a>
## S07 — Sprint 5: Interaction model June 2016 — 18F/C2

- **URL**: [Sprint 5: Interaction model June 2016 — 18F/C2](https://github.com/18F/C2/wiki/Sprint-5:-Interaction-model-June-2016)
- **該当箇所**: Research Plan / Card sorting activity / Learnings: Workflow
- **確認日 / 種別**: 2026-11-23 / first_party_case_study
- **原典の主張** (empirical_observation): C2の11人の質的調査で、件数と仕事により分類・検索・ソートの需要が変わると記録。
- **制約・版・未確認**: 特定サービスの観察。検索導入の件数閾値や全利用者への因果効果を示さない。
- **接続する原則**: A05, A09。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s08"></a>
## S08 — Progress easily — U.S. Web Design System

- **URL**: [Progress easily — U.S. Web Design System](https://designsystem.digital.gov/patterns/complete-a-complex-form/progress-easily/)
- **該当箇所**: When to use this pattern / Guidance: What to do and What not to do
- **確認日 / 種別**: 2026-11-23 / official_pattern
- **原典の主張** (author_guidance): 複雑フォームでは意味のある小話題へ分け、重要な説明を別画面のリンクの背後へ隠さない。
- **制約・版・未確認**: 主に負荷・機微情報の多い複雑フォーム。比較表や専門家の作業面に一画面一項目を要求しない。
- **接続する原則**: A07, A08。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s09"></a>
## S09 — Global header — IBM Carbon Design System

- **URL**: [Global header — IBM Carbon Design System](https://www.carbondesignsystem.com/building-blocks/core/patterns/global-header)
- **該当箇所**: Header and panel persistence / Task hierarchy / Navigation: Local / Organizational schemes
- **確認日 / 種別**: 2026-11-23 / official_pattern
- **原典の主張** (author_guidance): global/localの持続範囲とsystem/productのタスク範囲を区別し、一連の仕事を完了する領域をまとめる。
- **制約・版・未確認**: IBM製品群の文脈。具体的なブランド/位置指定は移植しない。無制限に増える対象をshellへ列挙しない。
- **接続する原則**: A06。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s10"></a>
## S10 — Make Short Critical Paths — W3C/WAI

- **URL**: [Make Short Critical Paths — W3C/WAI](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o5p02-short-paths/)
- **該当箇所**: What to Do / Examples
- **確認日 / 種別**: 2026-11-23 / official_supplemental_guidance
- **原典の主張** (author_guidance): 完了に必要な経路から任意の追加ステップを分ける。
- **制約・版・未確認**: 認知/学習障害向けのWorking Group Note由来の補足ガイダンス。WCAG適合必須要件ではなく必要な確認や法的要件の削除を許さない。
- **接続する原則**: A06, A08。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s11"></a>
## S11 — David Kieras — Task Analysis and the Design of Functionality（第2版向け公開原稿、刊行年未確定）

- **URL**: [David Kieras — Task Analysis and the Design of Functionality（第2版向け公開原稿、刊行年未確定）](https://web.eecs.umich.edu/~kieras/docs/TA_Modeling/TaskAnalysisV2.pdf)
- **該当箇所**: Introduction; The Critical Role of Task Analysis and Design of Functionality; Task properties of both types of systems; Level of detail; high-level GOMS と ECAD事例。PDF pp.1–5, 10–11, 15–21。Web抽出 L112–118, L158–168, L653–663, L721–743, L935–949。
- **確認日 / 種別**: 2026-11-23 / 本人・研究者によるハンドブック原稿。方法論、既存研究、事例を含む。
- **原典の主張** (author_guidance): Kierasは、ユーザーが達成する仕事を理解してからシステム要件と機能を選ぶよう提案する。全体システム、操作者の役割、個別タスクを区別し、機能設計を具体的なUI操作の設計と分けて扱う。
- **制約・版・未確認**: 単一の新規実験の報告ではない。高水準のタスクモデルから画面数やメニュー構造が一意に決まるとは述べていない。CMU読書リストと著者の旧索引は1997年版だが、今回読んだV2は第2版向け原稿で2003年文献を含むため、1997年版と同一版扱いしない。正確な刊行年と最終版との一致は未確定。
- **接続する原則**: A01, A03, A07。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s12"></a>
## S12 — Clayton Lewis and John Rieman（1993/1994）— Task-Centered User Interface Design

- **URL**: [Clayton Lewis and John Rieman（1993/1994）— Task-Centered User Interface Design](https://hcibib.org/tcuid/chap-2.html)
- **該当箇所**: Chapter 2: §2.2 Learning About the Users’ Tasks; §2.3 Using the Tasks in Design; HyperTopic: Integrating Task-Centered Design and Traditional Requirements Analysis。Web抽出 L41–80, L99–115, L131–145。
- **確認日 / 種別**: 2026-11-23 / 本人による公開教科書。著者の開発事例と方法論を含む。
- **原典の主張** (author_guidance): LewisとRiemanは、設計に依存しない具体的な代表タスクを集め、特定設計での実行をシナリオとして検討する方法を示す。抽象的な機能要件と、一連の現実のタスクは相互補完として扱っている。
- **制約・版・未確認**: サンプルタスクを処理できることだけでは一般的な妥当性は保証できない。ユーザーの現在の要望も将来利用の完全な予測ではない。本文の交通モデル開発は本人の事例であり、全製品を比較した実験ではない。
- **接続する原則**: A01, A10。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s13"></a>
## S13 — Debora Viana Thompson, Rebecca W. Hamilton, and Roland T. Rust（2005）— Feature Fatigue: When Product Capabilities Become Too Much of a Good Thing

- **URL**: [Debora Viana Thompson, Rebecca W. Hamilton, and Roland T. Rust（2005）— Feature Fatigue: When Product Capabilities Become Too Much of a Good Thing](https://thearf-org-unified-admin.s3.amazonaws.com/MSI/2020/06/MSI_Report_05-101.pdf)
- **該当箇所**: Study 3: Contrasting Evaluations Made before and after Product Use; General Discussion; Managerial Implications。PDF pp.11–15, 18–20。Web抽出 L798–840, L988–1022, L1346–1393。
- **確認日 / 種別**: 2026-11-23 / 実証研究。全文確認はMSI公開working paper。刊行版はJournal of Marketing Research 42(4), 431–442（書誌・抄録を確認）。
- **原典の主張** (empirical_observation): 利用前後で能力と使いやすさの評価上の重みを調べた研究。公開版では、利用後に使いやすさの重みが増えるというH4bは、満足度では支持されたが総合製品評価では不変であり、部分支持と記載されている。
- **制約・版・未確認**: 大学生、音声・動画プレーヤー、単一の実験セッションが中心。長期の習熟や回避行動の変化は将来研究。機能数を減らすほど常に良いという一般則ではない。MSI版は正式な学術査読を経ていない版と明記され、査読刊行版全文との一致は未確認。
- **接続する原則**: A04。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s14"></a>
## S14 — Joanna McGrenere and Gale Moore（2000）— Are We All In the Same “Bloat”?

- **URL**: [Joanna McGrenere and Gale Moore（2000）— Are We All In the Same “Bloat”?](https://www.dgp.toronto.edu/~joanna/papers/gi_2000_bloat.pdf)
- **該当箇所**: §3 Methods; §4 Quantitative Method; §5 Qualitative Method; §7 Bringing it All Together: Directions for Design。PDF pp.3–6, 9。Web抽出 L284–303, L504–524, L894–946。
- **確認日 / 種別**: 2026-11-23 / 論文・測定あり。Graphics Interface 2000の著者公開採択原稿。Torontoの研究。
- **原典の主張** (empirical_observation): Word利用者53人の質問紙と聞き取りで、使っていない機能をすべて除去したいという回答は少数で、新しい機能を発見したい利用者もいた。著者は多数の人が使わない機能と、個人が使わず望まない機能を区別している。
- **制約・版・未確認**: 利用情報は自己申告で操作ログではない。一つのアプリの利用者調査。削除の閾値はアプリに依存すると著者も限定している。カナダの研究であり米国機関の研究とは区別する。
- **接続する原則**: A03。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s15"></a>
## S15 — Joanna McGrenere, Ronald M. Baecker, and Kellogg S. Booth（2002）— An Evaluation of a Multiple Interface Design Solution for Bloated Software

- **URL**: [Joanna McGrenere, Ronald M. Baecker, and Kellogg S. Booth（2002）— An Evaluation of a Multiple Interface Design Solution for Bloated Software](https://www.dgp.toronto.edu/~joanna/papers/JMcGrenere_CHI_2002.pdf)
- **該当箇所**: Quantitative Results; Approach to Using Two Interfaces; Limitations and Constraints; Conclusions and Future Work。PDF pp.5–8。Web抽出 L386–438, L643–657, L688–710。
- **確認日 / 種別**: 2026-11-23 / 論文・測定あり。ACM CHI 2002の著者公開採択原稿。Toronto/UBCの研究。
- **原典の主張** (empirical_observation): 20人で個人用UIと全機能UIの切替を現場評価した。ログのある19人のうち14人はPersonal利用期間の半分以上を個人用UIで過ごした。一方、個人化に必要な時間を不満として途中でやめた利用者もいた。
- **制約・版・未確認**: 一つのアプリでの評価で、長期の再現確認と利用順のカウンターバランスに制約がある。主観的な学習容易性等を客観的タスク時間の改善に置き換えない。カナダの研究。
- **接続する原則**: A03, A08。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s16"></a>
## S16 — Jakob Nielsen（2006）— Progressive Disclosure

- **URL**: [Jakob Nielsen（2006）— Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/)
- **該当箇所**: Usability Criteria for Progressive Disclosure; Staged Disclosure: One Step at a Time。Web抽出 L85–106。
- **確認日 / 種別**: 2026-11-23 / 本人・専門家の設計助言。記事自体は新規実験の方法や標本を報告する論文ではない。
- **原典の主張** (author_guidance): Nielsenは、初期表示と二次表示の分け方、二次表示への明瞭な操作とラベル、観察による利用統計の補完を求める。重要度によるprogressive disclosureと、タスクの順番によるstaged disclosureを区別している。
- **制約・版・未確認**: 2段を超える構造への懸念は実務指針であり普遍的画面数上限ではない。根拠リンクのTraining Wheels紹介までは到達したが、Carrollらの原研究への旧ACMリンク2件は403で、紹介された効果量を原研究本文と照合していない。
- **接続する原則**: A08。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s17"></a>
## S17 — Jen Cardello（2014）— The Difference Between Information Architecture (IA) and Navigation

- **URL**: [Jen Cardello（2014）— The Difference Between Information Architecture (IA) and Navigation](https://www.nngroup.com/articles/ia-vs-navigation/)
- **該当箇所**: What Is Website Information Architecture?; What Is Website Navigation?; Define the IA Before Designing Navigation。Web抽出 L60–92。
- **確認日 / 種別**: 2026-11-23 / 本人・専門家の定義と設計助言。独立した比較実験ではない。
- **原典の主張** (author_guidance): Cardelloは、IAを内容・機能の同定とその構造・関係・命名、navigationを到達のためのUIとして区別する。内容量と複雑さを把握するIA初稿をナビゲーション形式の選択より先に用意するよう助言している。
- **制約・版・未確認**: IAの完全確定を待つ直列工程を要求していない。定義と実務上の助言であり、この順序の効果量を測った比較実験ではない。
- **接続する原則**: A05, A06。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s18"></a>
## S18 — Edward Scott / Baymard（2023）— Overcategorization of the Product Catalog Can Lead to Abandonment

- **URL**: [Edward Scott / Baymard（2023）— Overcategorization of the Product Catalog Can Lead to Abandonment](https://baymard.com/research-articles/ecommerce-over-categorization)
- **該当箇所**: How Overcategorization Harms Users’ Ability to Navigate the Product Catalog; How Using Filters Instead for Product Types with Shared Attributes Alleviates These Issues; How to Get Started Evaluating the Site Catalog。Web抽出 L139–147, L161–202, L224–257。
- **確認日 / 種別**: 2026-11-23 / 本人研究・観察あり・宣伝あり。試験観察、サイトベンチマーク、設計助言を含む。
- **原典の主張** (empirical_observation): 共通属性を持つ候補が別カテゴリに分かれると、試験参加者は比較や一覧把握に苦労し、商品を見落とす場合があったとBaymardは報告する。共通属性で比較する候補をフィルタとして扱う方法を提案している。
- **制約・版・未確認**: 属性群が異なる商品、専門店と総合店、件数の違いによって適切な分け方は変わる。10–30件は著者も必ずではない兆候と限定する。見出しの75%はベンチマークサイトの実装比率で、離脱率ではない。
- **接続する原則**: A05。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s19"></a>
## S19 — Mark Crowley / Baymard（2022）— Product Comparison UX: Always Provide Comparison Features for Spec-Driven Industries

- **URL**: [Mark Crowley / Baymard（2022）— Product Comparison UX: Always Provide Comparison Features for Spec-Driven Industries](https://baymard.com/research-articles/provide-comparison-features)
- **該当箇所**: Why Comparing Spec-Driven Products in Product Lists Is Difficult; How to Facilitate Easy Selection of Products for Comparison。Web抽出 L117–140, L174–207。特にL207の推奨改訂。
- **確認日 / 種別**: 2026-11-23 / 本人研究・観察あり・宣伝あり。
- **原典の主張** (empirical_observation): 多属性商品の一覧と別ページの往復には比較の負担があったと報告する。比較チェックボックスをhover時だけ出す従来推奨を、後の試験に基づいて常時表示へ変更したと明記している。
- **制約・版・未確認**: 仕様比較中心の商品が対象。67%は同社の特定試験での比較機能利用率であり、全サイトの利用率や売上改善率ではない。チェックボックス常時表示の助言を、すべての機能の常時表示へ拡張しない。
- **接続する原則**: A08, A09。原則のProcedure/JSON契約は、別に明記した本Skillの導出。

<a id="s20"></a>
## S20 — Iva Olah / Baymard（2023）— Product Listing UX: What Information to Display in Product Listings

- **URL**: [Iva Olah / Baymard（2023）— Product Listing UX: What Information to Display in Product Listings](https://baymard.com/research-articles/product-listing-information)
- **該当箇所**: 導入の観察結果; Provide 5 Essential Product Attributes; Provide Category-Specific Product Attributes for Spec-Driven Products。Web抽出 L117–143, L195–225, L226以降。
- **確認日 / 種別**: 2026-11-23 / 本人研究・観察あり・宣伝あり。
- **原典の主張** (empirical_observation): 一覧の属性が欠けることで、適合する商品を飛ばしたり、各商品の詳細ページを往復したりする参加者を観察したと報告する。共通属性とカテゴリ固有属性を区別している。
- **制約・版・未確認**: 記事の5属性をあらゆる業務画面に転用する根拠はない。小規模・DTCサイトでのレビューや、商品種別ごとのバリエーション表示には記事内でも例外がある。50%はサイトのベンチマーク値で、ユーザー失敗率ではない。
- **接続する原則**: A09。原則のProcedure/JSON契約は、別に明記した本Skillの導出。
