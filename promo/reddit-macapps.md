# Reddit r/macapps — Day 11: 7/27(月) JST 22:00–24:00(任意)

## 注意

- r/macapps は**サブスクへの風当たりが強い**。本文で先回りして「なぜサブスクか」を説明する(隠すと確実にコメントで刺される)
- 開発者であることを冒頭で明示(多くのサブレディットで自己宣伝ルールの必須要件)
- 余力がなければスキップしてよい(優先度: 任意)。r/ClaudeAI の反応が良かった場合のみ推奨
- flair 候補: `App Announcement` / `Self Promo`(実際にあるものを選ぶ)

## タイトル

```
AgentManager — native menu bar + floating window that watches your Claude Code sessions (dev here)
```

## 本文

```
Developer here, sharing my own app.

If you use Claude Code (Anthropic's coding agent CLI) and run more than one session at a time, you know the problem: one of them stops to ask permission, and you don't notice until you've wasted ten minutes.

AgentManager is a native macOS app (Swift, ~2.5 MB, notarized) that:

- Shows all sessions and their states in a floating window that only appears when something needs you
- Jumps to the right terminal on click (iTerm2 pane, Terminal tab, VS Code/Cursor window)
- Lives in your menu bar with per-state counts
- Optionally meows at you (it's themed around pixel-art cats; there's a Simple mode that turns all of that off)

Being upfront about the things r/macapps cares about:

- **Pricing**: $4.99/mo or $48/yr, 7-day free trial with no credit card. It's a subscription because the app tracks Claude Code's hook system, which changes constantly — this is ongoing maintenance, not a build-once app. I get that subs aren't for everyone; that's what the card-free trial is for.
- **Not on the App Store**: sandboxing would break the hook integration and terminal automation. Direct download, notarized, auto-updates with signature verification.
- **Privacy**: session data (prompts, paths, names) never leaves your Mac. Detection is all local files, no daemon.
- **License**: one license covers all your Macs.

macOS 13+, Apple Silicon & Intel. Requires Claude Code.

https://agentmgr.app/?utm_source=reddit&utm_medium=social&utm_campaign=launch-202607&utm_content=macapps

Happy to answer anything, including "why would I pay for this" — fair question, honest answers.
```

## 返信方針

- 「サブスク嫌い」 → 1回だけ理由を説明、平行線なら深追いしない。買い切り要望が多ければ「検討する」と記録(嘘は言わない)
- 「ニッチすぎる」 → その通りニッチ。Claude Code ユーザー以外には無用と正直に認める
- Claude Code を知らない人向け → 一言で説明(Anthropic の coding agent CLI)して深入りしない
