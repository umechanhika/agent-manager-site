# Show HN — Day 8: 7/24(金) JST 21:00–23:00

## 投稿方法

- https://news.ycombinator.com/submit で **url 欄に素の `https://agentmgr.app/`**(UTMなし)、title に下記タイトル
- 投稿直後に自分で first comment を投稿
- 投稿後2〜3時間はコメント即応(初動のスレッドの伸びが全て)。以降は翌朝まで放置でよい
- **PH に言及しない。再投稿しない**(不発なら1〜2週間後に1回だけ再挑戦可、HNの慣習上OK)
- 辛口コメントに防御的にならない。技術質問には具体的に答える(それがHNでの最大の宣伝)

## タイトル(80字以内・上から推奨順)

1. `Show HN: A macOS app that tells you when a Claude Code session is waiting`(74字)
2. `Show HN: AgentManager – See which Claude Code session is waiting for you`(73字)
3. `Show HN: Native macOS monitor for parallel Claude Code sessions`(64字)

## First comment(投稿直後に自分で)

```
Hi HN! Solo dev here. I run multiple Claude Code sessions in parallel, and I kept losing minutes to sessions that were silently blocked on a permission prompt while I was looking at another window. So I built a native macOS app that watches all sessions and surfaces the one that needs me.

How it works, briefly:

- It registers hooks in Claude Code's settings (with a .bak backup first). The hook writes each event to a per-session JSON file under ~/.claude/agent-manager/, and the app watches that directory with FSEvents. No daemon, no sockets, no network involved in detection.
- The tricky part was deciding "waiting" correctly: permission prompts and question dialogs arrive as Notification events, but tools like plan-approval never fire a Notification, so those are inferred from PreToolUse. Subagents get tracked separately so a parent session doesn't show "done" while its subagents are still running.
- Clicking a row jumps to the exact terminal. Precision varies by host: iTerm2 has stable session GUIDs (exact pane), Terminal.app is matched by TTY (tab), Ghostty by working directory, VS Code/Cursor/Zed via their CLIs (window). tmux is detect-only — the server daemonizes, so mapping a session back to the client terminal is unreliable and I'd rather not jump than jump wrong.

It's Swift (SwiftUI + AppKit), ~2.5 MB, notarized. Session data (prompts, paths, names) never leaves the machine; the only outbound traffic is anonymous crash reports / coarse feature-level usage events, and license validation.

Pricing, honestly: $4.99/mo (or $48/yr) after a 7-day trial with no card required. It's subscription because keeping up with Claude Code's changes is ongoing work, and I'd rather state that upfront than pretend it's one-and-done.

Happy to answer anything about the hook state machine, the terminal-jump hacks, or macOS floating-panel quirks.
```

## 想定される辛口質問と回答方針

**"Why is a status window $5/month?"**
> Fair. The honest answer: Claude Code changes fast and this app breaks the day I stop maintaining it, so I priced it as maintenance, not as a one-time artifact. The trial needs no card — if it doesn't save you its price in dead time, don't pay.

**"Why not open source?"**
> It's a paid product by a solo dev and I didn't want to run the open-core licensing dance for a v1. Not religious about it — if the project grows, opening parts of it (the hook state machine especially) is on the table.
> ※実際にOSS化の意向が無ければ後半を削る。嘘は書かない。

**"Why not the App Store?"**
> Sandboxing kills the two core features: registering Claude Code hooks and driving terminals via Automation. It's notarized and auto-updates with signature verification, which covers most of what the App Store would give you here.

**"Electron?"**
> No — Swift, SwiftUI + AppKit. The DMG is ~2.5 MB.

**"What exactly do you send home?"**
> Detection is fully local. Outbound: anonymous crash reports, ~a dozen coarse usage events (e.g. "jump used", host type only — no paths, no prompts, no session content), and license activation to the payment provider. There's no opt-out toggle for the usage events yet — fair ask, and it's on the list.
> ※現状オプトアウト設定は未実装(本体コードで確認済み)。「on the list」と書く以上、実際に対応する意思がなければこの一文を削ること。

**"Couldn't I do this with a shell script / tmux status bar?"**
> You absolutely could get 60% of it that way. The paid-for parts are the edge cases: correct waiting-detection across hook event types, subagent tracking, PID-reuse-safe orphan cleanup, and jumping to the right pane/tab/window across seven-ish terminal hosts.

**"Does it work with [terminal X]?"**
> Detection works everywhere (it's hook-based, terminal-agnostic). Jump precision varies — iTerm2 pane, Terminal/Ghostty tab, IDE window, everything else just gets brought to front.
