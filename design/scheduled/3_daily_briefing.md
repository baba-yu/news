1. future-predictionに今日の日付のfuture-prediction-yyyyddmm.mdがあるか確認。なかったら以降のステップは中止。



2. READMEを以下の構成でアップデート。今日を含めて3日分含めること。前日のものはコピペOK.その前の日のものはプッシュアウト。

  ---

  # repo名

repo情報（編集不要）

  ## 日付

  ### ニュース

  newsのサマリ（バレットポイント）+mdへのリンク

  ### 答え合わせ

  future-predictionのサマリ（バレットポイント）+mdへのリンク

  ---



3. `app\update_pages.bat`を実行。失敗したら下のフォールバックを試して、それでもダメなら作業ログをそのまま貼ってタスク中止。

[フォールバック]



* エラー出力を読んでクリアな原因か判断 (parser エラー / sqlite locked / git push 拒否 / etc)

* parser や schema 起因なら app\src\ を直して再実行

* sqlite が locked なら app\data\analytics.sqlite を削除して再実行 (DB 再構築)

* cd app && python -m pytest -q で 21/21 通ることだけは確認



4. 本日分を `git add -A` で全部 add して commit. README.md / docs/data/ / report/ / future-prediction/ に加え、別ジョブ (4_weekly_memory / 5_weekly_theme_review) が書いた `memory/dormant/` や `memory/theme-review/` の新規ファイルも漏れなく拾うこと (それらのジョブが sandbox の .git/in