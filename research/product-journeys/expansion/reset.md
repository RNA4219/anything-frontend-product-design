# パスワードの再設定方法を探す

各行の入口と終点は「表示された操作要素数／文字の矩形面積率／中央の最長余白（CSS px）」の順。— は計測対象外。[対象と方法](README.md)

| 条件 | 区分 | 判定 | 入口 | 終点 |
| --- | --- | --- | ---: | ---: |
| [Adobe・PC](#reset-adobe-desktop) | 新規 | 表示不可 | — | — |
| [Adobe・スマホ](#reset-adobe-mobile) | 新規 | 終点確認 | 3／10.2%／239 | 9／22.9%／69 |
| [Apple・PC](#reset-apple-desktop) | 再訪 | 途中まで | 24／5.5%／67 | 24／5.5%／67 |
| [Apple・スマホ](#reset-apple-mobile) | 再訪 | 途中まで | 11／7.2%／41 | 11／7.2%／41 |
| [Dropbox・PC](#reset-dropbox-desktop) | 再訪 | 終点確認 | 25／5.3%／128 | 19／18.2%／52 |
| [Dropbox・スマホ](#reset-dropbox-mobile) | 再訪 | 途中まで | 14／10.7%／80 | 12／13.6%／71 |
| [GitHub・PC](#reset-github-desktop) | 新規 | 終点確認 | 30／12.9%／110 | 37／21.8%／53 |
| [GitHub・スマホ](#reset-github-mobile) | 新規 | 途中まで | 12／19.1%／115 | 12／16.0%／56 |
| [Google・PC](#reset-google-desktop) | 新規 | 終点確認 | 19／2.5%／143 | 10／15.9%／0 |
| [Google・スマホ](#reset-google-mobile) | 新規 | 終点確認 | 14／8.0%／49 | 10／48.7%／35 |
| [Microsoft・PC](#reset-microsoft-desktop) | 新規 | 途中まで | 27／12.6%／54 | 27／12.6%／54 |
| [Microsoft・スマホ](#reset-microsoft-mobile) | 新規 | 途中まで | 12／25.6%／39 | 7／40.1%／38 |

<a id="reset-adobe-desktop"></a>

## Adobe（PC幅）

公式サポートの開始URLでAccess Deniedが表示され、再設定案内へ進めなかった。

白地の上部にアクセス拒否の文言がある。

照合した表示　アクセス拒否

入口はアクセス制限、終点はアクセス制限。

[公式の入口](https://helpx.adobe.com/support.html)

<a id="reset-adobe-mobile"></a>

## Adobe（スマホ幅）

忘れたパスワードを再設定するには、Adobeのアカウント画面で「Get help signing in」を選ぶと記事に記載されている。情報は入力・送信していない。

地域を選んだ後、再設定記事の見出しと最初の手順が表示される。

照合した表示　Get help signing in の手順

記録した操作　タップ「United States」 → タップ「Change or reset your password」 → スクロール「再設定の手順へ移動」

入口は地域選択、終点はサイトの画面。

[公式の入口](https://helpx.adobe.com/support.html) · [到達URL](https://helpx.adobe.com/account/individual/sign-in-and-security/security-and-recovery/reset-adobe-password.html)

<a id="reset-apple-desktop"></a>

## Apple（PC幅）

サポートの再設定入口は表示されたが、今回の操作では画面遷移できず、方法は確認できなかった。

製品アイコンの並びと再設定への案内がある。

照合した表示　Apple Supportの入口

[公式の入口](https://support.apple.com/en-us) · [到達URL](https://support.apple.com/) · [前回の同じ条件](../walkthrough/reset.md#reset-apple-desktop)

<a id="reset-apple-mobile"></a>

## Apple（スマホ幅）

サポートの再設定入口は表示されたが、今回の操作では画面遷移できず、方法は確認できなかった。

製品アイコンの並びと再設定への案内がある。

照合した表示　Apple Supportの入口

[公式の入口](https://support.apple.com/en-us) · [到達URL](https://support.apple.com/) · [前回の同じ条件](../walkthrough/reset.md#reset-apple-mobile)

<a id="reset-dropbox-desktop"></a>

## Dropbox（PC幅）

ログイン画面で登録メールを入力して続行し、「パスワードを忘れた場合」を選んでメールを送信すると、再設定リンクが届くと記事に記載されている。情報は入力・送信していない。

Cookie通知を閉じた記事に番号付きの再設定手順が表示される。

照合した表示　ログイン画面からの再設定手順

記録した操作　クリック「Reset password」 → クリック「How to change or reset your Dropbox password - Dropbox Help」 → クリック「Cookie通知を拒否または閉じる」 → スクロール「パスワード再設定手順へ移動」

[公式の入口](https://help.dropbox.com/) · [到達URL](https://help.dropbox.com/ja-jp/security/password-reset) · [前回の同じ条件](../walkthrough/reset.md#reset-dropbox-desktop)

<a id="reset-dropbox-mobile"></a>

## Dropbox（スマホ幅）

Reset passwordから検索結果へ進み、Dropboxパスワードの再設定記事の候補が表示された。本文までは到達していない。

最初の検索結果に対象記事があり、画面下部にCookie通知が重なる。

照合した表示　再設定記事の検索結果

記録した操作　タップ「Reset password」

[公式の入口](https://help.dropbox.com/) · [到達URL](https://help.dropbox.com/ja-jp/search-results) · [前回の同じ条件](../walkthrough/reset.md#reset-dropbox-mobile)

<a id="reset-github-desktop"></a>

## GitHub（PC幅）

新しいパスワードの要求は専用ページへ進み、アカウントに紐づくメールアドレスを入力してリセットメールを送ると案内される。使用できるのはプライマリまたはバックアップのメールアドレス。情報は入力・送信していない。

記事の「新しいパスワードをリクエストする」に番号付き手順とメールアドレスの条件が表示される。

照合した表示　新しいパスワードの要求手順

記録した操作　クリック「認証」 → クリック「アカウント セキュリティ」 → クリック「アクセスの資格情報を更新する」 → クリック「アクセスの資格情報を更新する」 → スクロール「新しいパスワードの手順へ移動」

[公式の入口](https://docs.github.com/) · [到達URL](https://docs.github.com/ja/authentication/keeping-your-account-and-data-secure/updating-your-github-access-credentials)

<a id="reset-github-mobile"></a>

## GitHub（スマホ幅）

GitHub Docsの「認証」へ進んだが、未ログイン時のパスワード再設定手順には到達していない。

認証ドキュメントの見出しと概要、記事一覧が表示される。

照合した表示　認証ドキュメントの入口

記録した操作　タップ「認証」

[公式の入口](https://docs.github.com/) · [到達URL](https://docs.github.com/ja/authentication)

<a id="reset-google-desktop"></a>

## Google（PC幅）

パスワードの再設定は案内の手順からアカウントを復元し、本人確認の質問とメールを確認する。メールが届かない場合は迷惑メールフォルダなどを確認するよう記載されている。本人情報は入力・送信していない。

「パスワードの再設定」見出しの下に復元へのリンクとメールが届かない場合の案内がある。

照合した表示　パスワードの再設定とアカウント復元の手順

記録した操作　入力「reset password」 → キー「Enter」 → クリック「パスワードを変更または再設定する
ヘルプ記事 - Google アカウント
重要: Android 5.1 以降のデバイスをお使いの場合、パスワードを変更してから 24 時間は、出荷時の設定にリセットすることはできません。デバイスを保護する」 → スクロール「パスワードの再設定へ移動」

[公式の入口](https://support.google.com/) · [到達URL](https://support.google.com/accounts/answer/41078)

<a id="reset-google-mobile"></a>

## Google（スマホ幅）

パスワードの再設定は案内の手順からアカウントを復元し、本人確認の質問とメールを確認する。メールが届かない場合は迷惑メールフォルダなどを確認するよう記載されている。本人情報は入力・送信していない。

「パスワードの再設定」見出しの下に復元へのリンクとメールが届かない場合の案内がある。

照合した表示　パスワードの再設定とアカウント復元の手順

記録した操作　入力「reset password」 → キー「Enter」 → タップ「パスワードを変更または再設定する
ヘルプ記事 - Google アカウント
重要: Android 5.1 以降のデバイスをお使いの場合、パスワードを変更してから 24 時間は、出荷時の設定にリセットすることはできません。デバイスを保護する」 → スクロール「パスワードの再設定へ移動」

[公式の入口](https://support.google.com/) · [到達URL](https://support.google.com/accounts/answer/41078)

<a id="reset-microsoft-desktop"></a>

## Microsoft（PC幅）

Microsoftサポートトップは表示されたが、今回の自動操作は画面要素の切り替え中に停止し、再設定手順には進めなかった。

サポートのトップ画面に製品別の選択肢が並ぶ。

照合した表示　サポートトップ

[公式の入口](https://support.microsoft.com/) · [到達URL](https://support.microsoft.com/ja-jp/)

<a id="reset-microsoft-mobile"></a>

## Microsoft（スマホ幅）

Microsoftアカウントのヘルプを開いた。サインインできない場合の案内はあるが、再設定方法の手順を終点画像で確認できなかった。

アカウントのヘルプ見出しと、パスワード・個人情報に関する説明が表示される。

照合した表示　Microsoftアカウントのヘルプ

記録した操作　タップ「Microsoft アカウント」

[公式の入口](https://support.microsoft.com/) · [到達URL](https://support.microsoft.com/ja-jp/accounts-billing/manage/microsoft-account-help)
