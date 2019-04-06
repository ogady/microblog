# Anicolle blog
アニメに関する感想をシェアするサービスです。
SignUpして利用してください。

メニューバーにある”SIGNUP”からユーザー登録してください。
自分用の簡単な独り言ブログが使用できるようになります。
TEST用のユーザーも用意してるので試してみてください。
＜TEST用ユーザー＞

- email:test@gmail.com
- password:testzaq1zaq1

# 機能一覧
- 記事一覧表示機能
- 記事詳細表示機能
- 記事投稿機能（画像アップロード可能）
- サインアップ、サインアウト機能
- ログイン、ログアウト機能
- プロフィール詳細表示機能
- プロフィール編集機能（画像アップロード可能）
- アニメ検索機能（ShangriLa Anime APIを利用）
- コメント、コメント返信機能
- いいね機能

# 使用技術
- Python==3.7.0
- Django==2.1.7
- Pillow==5.4.1(画像アップロード用ライブラリ)
- django-heroku==0.3.1(Herokuデプロイ用ライブラリ)
- DB：SQLite3
- 本番環境：Heroku(GitHubと連携し、masterの更新をキックにbuild、deploy)
- エディタ：Atom
