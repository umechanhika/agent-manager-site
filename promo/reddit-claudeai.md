# Reddit r/ClaudeAI — Day 4: 7/20(月) JST 22:00–24:00

## 投稿の作法

- 投稿前に r/ClaudeAI の最新ルール(サイドバー)を確認。自作ツール共有は一般に歓迎されるが、**開発者であることを本文冒頭で明示**する
- flair 候補: `Built with Claude` / `Showcase` / `Productivity`(実際にあるものを選ぶ。ツール共有系 flair が最優先)
- 形式: **GIF付き投稿(`screenshot-day.gif` をアップ)+本文**。GIFが使えない flair なら text post にして冒頭にリンク
- 投稿後2時間はコメント即応([faq-responses.md](faq-responses.md) の英語回答を流用)
- 同日に他のサブレディットへ投稿しない(クロスポスト連打はスパム判定されやすい)

## タイトル

```
I built a macOS app that tells you the moment one of your Claude Code sessions is waiting for input
```

予備案:

```
Tired of finding out a Claude Code session has been waiting 10 minutes for a "yes"? I built a monitor for that
```

## 本文

```
Hey r/ClaudeAI — solo dev here, and this is my own tool, so full disclosure upfront.

Like probably half this sub, I run several Claude Code sessions in parallel (multiple repos / worktrees). My recurring failure mode: a session hits a permission prompt, I'm deep in another window, and I discover it 10 minutes later just sitting there waiting for a single keypress.

So I built AgentManager, a native macOS app:

- A small floating window lists every session with its state (running / waiting / done) and how long it's been there
- The window only appears when a session actually needs you, and hides itself when everything is clear
- Click a session to jump to its terminal — exact pane in iTerm2, tab in Terminal/Ghostty, project window for VS Code / Cursor / IDE terminals
- Menu bar counts, an ⌥Space toggle, and (optionally) a cat meow when something needs attention instead of Notification Center banners
- Sessions show up as pixel-art cats in a tiny room. This part is 100% unnecessary and it's my favorite part. There's a Simple mode if it's not yours.

Technical notes since this sub will ask: detection is via Claude Code hooks (registered in settings.json with a backup, only the hooks key is touched). Everything is local JSON files — no daemon, no network. Session data never leaves your Mac.

It's paid ($4.99/mo or $48/yr) with a 7-day free trial, no credit card. macOS 13+, Apple Silicon & Intel.

https://agentmgr.app/?utm_source=reddit&utm_medium=social&utm_campaign=launch-202607&utm_content=claudeai

Genuinely looking for feedback — especially: which terminal/IDE do you run Claude Code in, and where does the jump land for you? That's the part with the most edge cases.
```

## 返信方針

- 「hooks を上書きされたくない」系の不安 → `.bak` バックアップ+hooksキー以外に触れない+symlink保全を具体的に説明
- 無料ツールとの比較 → 貶さない。「それで足りるならそれがいい。こちらは waiting 判定の精度とジャンプに全振りしている」
- tmux ユーザー → 検知は動く、ジャンプは誤爆回避のため意図的に非対応、と正直に
