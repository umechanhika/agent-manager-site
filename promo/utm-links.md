# UTM リンク一覧(コピペ用)

ルール: `https://agentmgr.app/?utm_source=<source>&utm_medium=<medium>&utm_campaign=launch-202607`

LP には GA4 導入済みのため、以下のURLを貼るだけで流入元別の計測ができる。

## チャネル別 完成URL

| 用途 | URL |
|------|-----|
| X ローンチスレッド(日本語) | `https://agentmgr.app/?utm_source=twitter&utm_medium=social&utm_campaign=launch-202607` |
| X PH連動投稿(英語) | `https://agentmgr.app/?utm_source=twitter&utm_medium=social&utm_campaign=launch-202607&utm_content=ph-launch` |
| X 小ネタストック | `https://agentmgr.app/?utm_source=twitter&utm_medium=social&utm_campaign=launch-202607&utm_content=followup` |
| Product Hunt(製品ページの Website リンク) | `https://agentmgr.app/?utm_source=producthunt&utm_medium=referral&utm_campaign=launch-202607` |
| Show HN(**コメント内リンクのみ**) | `https://agentmgr.app/?utm_source=hackernews&utm_medium=referral&utm_campaign=launch-202607` |
| Reddit r/ClaudeAI | `https://agentmgr.app/?utm_source=reddit&utm_medium=social&utm_campaign=launch-202607&utm_content=claudeai` |
| Reddit r/macapps | `https://agentmgr.app/?utm_source=reddit&utm_medium=social&utm_campaign=launch-202607&utm_content=macapps` |
| zenn 記事 | `https://agentmgr.app/?utm_source=zenn&utm_medium=article&utm_campaign=launch-202607` |
| note 記事 | `https://agentmgr.app/?utm_source=note&utm_medium=article&utm_campaign=launch-202607` |

## 注意

- **Show HN のタイトル横URL(submit の url 欄)には UTM を付けない**(素の `https://agentmgr.app/` を使う。UTM付きはHNで嫌われ、モデレーションで剥がされることもある)。HN からの流入はリファラ `news.ycombinator.com` で判別する。
- Product Hunt の製品URL欄も同様に素のURLが無難だが、PH は慣習的に UTM 許容。迷ったら素のURL+リファラ判別でよい。
- GitHub Releases の DMG 直リンクは計測不能。計測点は「LP到達」(GA4)と「トライアル開始」(Freemius ダッシュボード)の2点に置く。
- チェックアウト直リンクを投稿に貼らない(必ずLPを経由させる)。LPが説明と計測を担う。
