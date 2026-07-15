# Product Hunt ローンチ — Day 6: 7/22(水)

## 時刻(重要)

- PH の1日は **00:01 PST/PDT** 起点。7月は夏時間(PDT = UTC-7)なので **JST +16時間**
- **7/22 のローンチ = JST 7/22(水) 16:01 開始 〜 7/23(木) 16:00 終了**
- 事前にローンチを 7/22 00:01 PDT でスケジュール設定しておく(当日手動投稿は事故のもと)
- 開始5分以内に maker first comment を投稿。JST 16:00〜24:00 は全コメント即応

## 基本情報(フォーム入力用)

| 項目 | 内容 |
|------|------|
| Name | AgentManager |
| Tagline | `Never miss a Claude Code session waiting for your input`(56字/60字以内) |
| Website | `https://agentmgr.app/?utm_source=producthunt&utm_medium=referral&utm_campaign=launch-202607` |
| Topics | Developer Tools / Mac / Artificial Intelligence(+入れられれば Productivity) |
| Pricing | Free trial → Paid($4.99/mo)を正直に選択(「Free」を選ばない) |
| Maker | 自分をメーカーとして登録 |

タグライン予備案(A/Bどちらでも可):

- `Your Claude Code sessions, always in view`(41字)— LPのH1と統一感
- `Know the moment a Claude Code session needs you`(47字)

## Description(製品説明・260字以内)

```
A floating macOS window for every Claude Code session. The moment one needs your input, it surfaces — and hides when all is clear. Jump to the exact terminal in one click. Native Swift, notarized, 7-day free trial.
```

(213字/260字以内)

## ギャラリー画像(この順序でアップ)

PH 推奨サイズは 1270×760。手元素材は 8:5(1270×794 相当)なので、上下を軽くトリミングするか、クリーム色 `#F4ECD8` の背景に載せて 1270×760 に書き出す。

| 順 | ファイル | 見せたいこと |
|----|---------|--------------|
| 1 | `screenshot-day.gif` | 第一印象: フローティングウィンドウ+猫部屋の全体像(GIFで動きを見せる) |
| 2 | `feature-autoshow.gif` | コア価値: 必要な瞬間だけ現れて消える |
| 3 | `feature-jump.png` | ターミナルへワンクリックジャンプ |
| 4 | `feature-catroom.gif` | 猫部屋(差別化・記憶に残す) |
| 5 | `feature-menubar.png` | メニューバー常駐の安心感 |
| 6 | `feature-simple.png` | シンプルモード(猫が苦手な人への回答) |

## Maker first comment(開始5分以内に投稿)

```
Hi Product Hunt! 👋

I'm a solo developer from Japan, and like many of you I run several Claude Code sessions in parallel. I kept doing the same dumb thing: kick off a session, switch to something else, and realize ten minutes later that Claude had been sitting there waiting for a single "yes" the whole time.

AgentManager is a native macOS app that fixes exactly that:

🐈 A floating window shows every session's state — running, waiting, done
⚡ It surfaces the moment a session needs your input, and hides when all is clear
🖱️ Click a row to jump straight to the right terminal (iTerm2 pane, Terminal tab, VS Code / Cursor window…)
🔔 Cat-meow alerts instead of Notification Center banners (mutable, promise)
🎨 Sessions live as pixel-art cats in a little room — day and night change with your clock. There's a Simple mode if cats aren't your thing.

A few things that matter to me:

• Native Swift, ~2.5 MB download, notarized by Apple
• Your session data (prompts, paths, names) never leaves your Mac
• 7-day free trial with no credit card. Then $4.99/mo or $48/yr.

I'd love your feedback — especially which terminals or IDEs you'd like better jump support for. I'll be here all day answering questions!
```

## 当日の動き

- [ ] JST 16:01 ローンチ確認 → first comment 投稿
- [ ] X 連動投稿([twitter-ph-launch-en.md](twitter-ph-launch-en.md))
- [ ] 全コメントに即返信([faq-responses.md](faq-responses.md) の英語回答を流用)
- [ ] upvote の直接依頼はどこにも書かない(PH規約)。「見に来て」まで
- [ ] Show HN とは相互リンクしない
- [ ] 終了後(7/23 JST 16:00)、結果を X で報告し、LP に PH バッジを貼るか検討(Top 10 に入った場合)

## 事前準備チェックリスト(Day 2–3 の土日に完了させる)

- [ ] PH アカウントのプロフィール整備(顔写真 or アイコン、bio、X リンク)
- [ ] ギャラリー画像 6点を 1270×760 に変換
- [ ] 製品ページ下書き作成 → スケジュール設定(7/22 00:01 PDT)
- [ ] first comment を下書き保存(このファイルからコピペできる状態に)
