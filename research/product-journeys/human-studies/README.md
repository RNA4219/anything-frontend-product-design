# 人が探す・押す・やり直すときの実測

21件の一次資料から、参加者が実際に行った課題の測定値を103件収録した。原典の集計表、図、著者による観察記録までたどれる。商品・店舗の検索、来館案内、返品、アカウント再設定に加え、タップや画面密度の効果を切り分ける実験も含む。

[測定値をCSVで開く](metrics.csv) · [参加者・端末・初見条件と原典URL](studies.json) · [同じ用件の自動操作記録](../README.md) · [実画面の余白・情報密度](../spacing/README.md)

## 実際の利用者がどこで迷ったか

| 用件 | 観察されたこと | 解釈に必要な条件 |
| --- | --- | --- |
| 美術館の開館時間 | マドリードの美術館では、7人全員が最初に来館案内を選び、4人が土曜夜の無料入館を見落とした。基本の開館時間を探すのに苦労したのは3人。 | 本人のスマホを使用。「最初に行くページ」と「最後に読み取れた条件」を別々に評価できる。[実施者の報告](https://ixd.prattsi.org/2026/05/streamlining-museum-trip-planning/) |
| 返品規約 | MUJIの規約を見つけたのはPCでもスマホでも3人中2人。スマホで到達した2人の時間は30秒、26秒。 | 同じ人がPCを先に操作し、スマホでは場所を覚えていた。端末間の発見しやすさをこの時間差から推定できない。[原図 pp.18–20](https://www.urvashibhorkar.com/_files/ugd/af2984_8eb80ea884a9449b82310c712b81b042.pdf) |
| クーポンを探す | IKEAの参加者8人中6人が、まず「Offers」を押した。クーポンの場所を見つけた5人のうち3人が途中で支援を受けた。 | 全員にサイトの閲覧経験があった。支援付きの到達件数も記録すると、自力で探せた人数との違いが分かる。[実施者の報告、Finding 3](https://uploads-ssl.webflow.com/5c2ed19d3ded38577c949b46/5c50c38c3c076f0aaa48fbf9_Final%20Report.pdf) |
| 画面の情報量と探索時間 | 指定リンクを探す実験で、平均は低複雑性の画面で4.2秒、高複雑性の画面で7.3秒だった。 | 165人を解析。実サイトの静止画を使い、表示から指定先を押すまでを測定した。誤クリック率と複雑さの関係は検出されなかった。余白だけの効果は分からない。[CHI原著](https://talaugust.github.io/assets/pdf/Baughan2020KeepIS.pdf) |
| 何度も戻って探す | 米国の経済センサスで、地域の売上を調べる方法に行き着いたのは7人中0人、2年分のデータが比較できるかを正しく調べたのは1人。各課題で観察者が数えた「戻る」は、7人合わせて21回、40回。 | 各人の押し直し回数や誤操作率に読み替えず、行き詰まった経路を再現するための手掛かりにする。[原典 Table 2・§3.1](https://www.census.gov/content/dam/Census/library/working-papers/2008/adrm/ssm2008-11.pdf) |

## 数字の読み方

- CSVの1行は、1原典・1課題・1条件について報告された1つの値。同じ標本の時間、達成、誤りは別行。人数の単純合算や、研究間の平均は出していない。
- `source_id` で調査条件を、`locator` で原典の表・図・節を引ける。`denominator` はその割合の母数、人数を数えた群の大きさ、または平均・中央値の対象数。値が表す単位は `unit` と `measure` に記載した。空欄は該当する数を確定できなかった箇所で、0とは異なる。
- 初回クリックは、その課題での最初の選択。サイトや製品の初利用を確かめたい場合は、各調査の `prior_exposure` を確認する。初見の条件が明記された例はByPass試作の初回利用、過去の閲覧経験が全員にある例はIKEA、試行順の影響を確認できる例はMUJI。
- 達成・自力での達成・支援付きの達成、断念までの時間・成功者の時間、実機でのタップ・スクリーンショットのクリックは原典の定義に従う。1人の押し直し事例やインストール数を参加者全体の割合に換算しない。
- 前回の29ブランド・施設との関係は用件単位で記録した。IKEAなど同じブランドを含む場合も、国・公開年・商品・課題まで一致するとは限らない。個々の初期画面の余白と参加者の行動を同時に取得したデータは今回のサイト再計測にはない。

## 原典別の収録範囲

### 実サービスの利用観察

| 原典 | 調査対象人数 | 収録値 | 前回と関連する用件 |
| --- | ---: | ---: | --- |
| [Streamlining Museum Trip Planning](https://ixd.prattsi.org/2026/05/streamlining-museum-trip-planning/)（2026） | 7 | 5 | 来館案内 |
| [Improving the National Gallery of Art’s Website for First-Time Visitors](https://ixd.prattsi.org/2026/05/case-study-improving-the-national-gallery-of-arts-website-for-first-time-visitors/)（2026） | 8 | 1 | 来館案内 |
| [MUJI Responsive Web Redesign – Research Report](https://www.urvashibhorkar.com/_files/ugd/af2984_8eb80ea884a9449b82310c712b81b042.pdf)（年不明） | 3 | 9 | 商品検索・返品条件 |
| [Final Report: IKEA Website](https://uploads-ssl.webflow.com/5c2ed19d3ded38577c949b46/5c50c38c3c076f0aaa48fbf9_Final%20Report.pdf)（2018） | 8 | 4 | 商品検索・検索の修正 |
| [Nordstrom.com Core Shopping Experience](https://static1.squarespace.com/static/5c2e3922a9e028aa96c590c0/t/64e6d82d3261ca69fa25a4e1/1692850232008/Nordstrom_FinalReport.pdf)（2022） | 9 | 4 | 商品条件・商品検索 |
| [A Usability and Eye-Tracking Evaluation of the Economic Census Web Site](https://www.census.gov/content/dam/Census/library/working-papers/2008/adrm/ssm2008-11.pdf)（2008） | 7 | 12 | 来館案内・店舗案内 |
| [A Usability and Eye-Tracking Evaluation of the Build-a-Table Web Site](https://www.census.gov/content/dam/Census/library/working-papers/2009/adrm/ssm2009-06.pdf)（2009） | 9 | 17 | 検索の修正・店舗案内 |
| [Final Report for Usability Testing of the Census Regional Website](https://www2.census.gov/library/working-papers/2011/adrm/ssm2012-02.pdf)（2011） | 13 | 20 | 店舗案内・来館案内 |
| [How to Turn User Videos into Insights](https://measuringu.com/user-videos-insights/)（2018） | 150 | 1 | 商品検索・商品条件 |

### 実サイトと静止画の比較

| 原典 | 調査対象人数 | 収録値 | 前回と関連する用件 |
| --- | ---: | ---: | --- |
| [Do Click Tests Predict Live Site Clicks?](https://measuringu.com/do-click-tests-predict-live-site-clicks/)（2023） | 130 | 3 | 返品条件 |
| [Do Click Tests Predict Clicks on Product Pages?](https://measuringu.com/do-click-tests-predict-clicks-on-product-pages/)（2023） | 306 | 3 | 商品検索・商品条件 |

### 試作・分類・研究サイトでの課題

| 原典 | 調査対象人数 | 収録値 | 前回と関連する用件 |
| --- | ---: | ---: | --- |
| [ByPass: Reconsidering the Usability of Password Managers](https://eudl.eu/pdf/10.1007/978-3-030-63086-7_24)（2020） | 20 | 2 | 再設定 |
| [A Comparative Long-Term Study of Fallback Authentication Schemes](https://maximiliangolla.com/files/2024/papers/chi24-sub9761-fallback-lt.pdf)（2024） | 97 | 3 | 再設定 |
| [Card Sorting + Tree Testing: The Science of Great Site Navigation](https://measuringu.com/cardsort-tree-test/)（2012） | 50 | 3 | 商品検索・商品条件 |

### 実機の操作・タップ研究

| 原典 | 調査対象人数 | 収録値 | 前回と関連する用件 |
| --- | ---: | ---: | --- |
| [Interaction and Recognition Challenges in Interpreting Children’s Touch and Gesture Input on Mobile Devices](https://lisa-anthony.com/wp-content/uploads/2012/09/anthony-et-al-tabletop20121.pdf)（2012） | 30 | 1 | 基礎的な操作・探索 |
| [Elderly User Evaluation of Mobile Touchscreen Interactions](https://opendl.ifip-tc6.org/db/conf/interact/interact2011-1/KobayashiHMAHI11.pdf)（2011） | 20 | 3 | 基礎的な操作・探索 |
| [100,000,000 Taps: Analysis and Improvement of Touch Performance in the Large](https://www.uni-ulm.de/fileadmin/website_uni_ulm/iui.inst.100/institut/Papers/Prof_Rukzio/2011/2011_henze_mobilehci2011.pdf)（2011） | 人数不明 | 1 | 基礎的な操作・探索 |
| [Can Capacitive Touch Images Enhance Mobile Keyboard Decoding?](https://arxiv.org/abs/2410.02264)（2024） | 16 | 2 | 検索の修正 |
| [Exploring Usability Issues of a Smartphone-Based Physician-to-Physician Teleconsultation App in an Orthopedic Clinic: Mixed Methods Study](https://humanfactors.jmir.org/2021/4/e31130)（2021） | 5 | 4 | 検索の修正 |

### 画面の密度・複雑さを変えた実験

| 原典 | 調査対象人数 | 収録値 | 前回と関連する用件 |
| --- | ---: | ---: | --- |
| [Keep it Simple: How Visual Complexity and Preferences Impact Search Efficiency on Websites](https://talaugust.github.io/assets/pdf/Baughan2020KeepIS.pdf)（2020） | 165 | 2 | 商品検索・来館案内・店舗案内 |
| [The Influence of Local Density and Link Color on Visual Search](https://www.cs.uoregon.edu/research/cm-hci/Text_Search/Text_Color_and_local_density_study.pdf)（2003） | 24 | 3 | 基礎的な操作・探索 |
