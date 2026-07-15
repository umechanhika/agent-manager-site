# 想定Q&A回答集(日英併記・コメント返信の弾薬庫)

全チャネル共通。コピペ後、文体だけ場に合わせて調整する(HN/Reddit は防御的にならない・正直に、が鉄則)。

---

## Q. なぜサブスク? 買い切りにしないの? / Why a subscription?

**EN:**
> Fair question. AgentManager tracks Claude Code's hook events, and Claude Code itself changes fast — new events, new behaviors, new terminals to support. Keeping up with that is ongoing work, not a one-time build. The subscription funds that maintenance. There's a 7-day free trial (no credit card), so you can decide whether it earns its keep before paying anything.

**JA:**
> Claude Code 本体の進化が速く(新しいイベント、新しい挙動、新しいターミナル対応)、追従し続けるのが継続的な作業になるため、サブスクにしています。7日間の無料トライアル(カード登録不要)で、払う価値があるか先に判断してもらえます。

## Q. なぜ App Store で配布しないの? / Why not on the Mac App Store?

**EN:**
> App Store sandboxing would break the core features — reading Claude Code's hook events and jumping to your terminal. The app is notarized by Apple and updates itself automatically, so you still get signature-verified installs and updates.

**JA:**
> App Store のサンドボックスでは中核機能(Claude Code のフック連携、ターミナルへのジャンプ)が実現できないためです。アプリは Apple の公証(notarization)済みで、アップデートも署名検証付きで自動配信されます。

## Q. セッションをどうやって検知しているの? / How does it detect sessions?

**EN:**
> It registers hooks in Claude Code's `~/.claude/settings.json` (a `.bak` backup is created first, and it only touches the `hooks` key — your formatting, comments, and symlinks are preserved). Hook events are written to local JSON files under `~/.claude/agent-manager/`, and the app watches that directory. No daemon, no network — everything stays on your Mac.

**JA:**
> Claude Code のフック機能を使っています。`~/.claude/settings.json` に自動登録され(登録前に `.bak` バックアップを作成、`hooks` キー以外は一切変更しません)、イベントはローカルのJSONファイル経由でアプリに渡ります。デーモンもネットワーク通信も無く、すべて Mac の中で完結します。

## Q. セッションのデータは外部に送られる? / Does my session data leave my machine?

**EN:**
> No. Prompts, file paths, and session names never leave your Mac. The only things sent out are anonymous crash reports and basic usage stats (feature-level events only — no paths, no prompts, no session content), and license activation with the payment provider.

**JA:**
> 送られません。プロンプト・パス・セッション名が Mac の外に出ることはありません。外部送信されるのは匿名のクラッシュレポートと機能単位の利用統計(パスやプロンプト等の中身は含まない)、およびライセンス認証の通信のみです。

## Q. Electron 製? / Is this Electron?

**EN:**
> No — native Swift (SwiftUI + AppKit). The DMG is about 2.5 MB.

**JA:**
> いいえ、Swift 製のネイティブアプリです(SwiftUI + AppKit)。DMG は約 2.5MB です。

## Q. 動作要件は? / Requirements?

**EN:**
> macOS 13 Ventura or later, Apple Silicon or Intel. You need Claude Code (the `claude` CLI) installed — AgentManager is a companion app for it.

**JA:**
> macOS 13 Ventura 以降、Apple Silicon / Intel 両対応です。Claude Code(`claude` CLI)が別途必要です。

## Q. どのターミナルに対応? / Which terminals are supported?

**EN:**
> Detection works in any terminal (it's hook-based). Jump precision varies: iTerm2 jumps to the exact pane, Terminal.app and Ghostty 1.3+ to the tab, VS Code / Cursor / Zed / JetBrains IDEs to the project window, and others (Warp, kitty, WezTerm, Alacritty) bring the app to front. tmux sessions are detected but jump is not supported.

**JA:**
> 検知はフック経由なので全ターミナルで動きます。ジャンプの精度はターミナルごとに異なり、iTerm2 はペイン単位、Terminal / Ghostty 1.3+ はタブ単位、VS Code / Cursor / Zed / JetBrains 系はプロジェクトウィンドウ、その他(Warp / kitty / WezTerm / Alacritty)はアプリ前面化です。tmux は検知のみ対応です。

## Q. 権限は何が必要? / What permissions does it need?

**EN:**
> Detection needs no permissions at all. Jumping asks for Automation permission (for iTerm2 / Terminal / Ghostty) or Accessibility (for some IDEs) the first time you use it — and only for the apps you actually jump to.

**JA:**
> 検知は権限不要です。ジャンプ機能を使うときだけ、対象アプリに応じてオートメーション権限(iTerm2 / Terminal / Ghostty)またはアクセシビリティ権限(一部IDE)を初回に求めます。

## Q. 猫の鳴き声、仕事中に困らない? / Cat sounds at work?

**EN:**
> You can mute the meow (and it never uses macOS notification banners, so nothing pops up in Notification Center). There's also a Simple mode that hides the pixel-art room entirely.

**JA:**
> 鳴き声はミュートできます(通知センターも使わないのでバナーは出ません)。ピクセルアートの部屋ごと隠すシンプルモードもあります。

## Q. ライセンスは何台まで? / How many Macs per license?

**EN:**
> One license covers all your Macs — activate and deactivate per device as needed.

**JA:**
> 1ライセンスで複数の Mac で使えます。端末ごとに有効化・解除できます。

## Q. 解約・返金は? / Cancellation and refunds?

**EN:**
> Cancel anytime from the license portal. The trial requires no credit card, so there's nothing to forget to cancel. Payments are handled by Freemius (the merchant of record) — refund requests go through them and I honor reasonable ones.

**JA:**
> いつでもキャンセルできます。トライアルはカード登録不要なので「解約し忘れ」も起きません。決済は Freemius(販売事業者)経由で、返金のご相談にも対応します。

## Q. 価格情報 / Pricing quick facts

- 7-day free trial, no credit card, all features / 7日間無料・カード不要・全機能
- $4.99/month or $48/year (≈$4/month) / 月額$4.99、年額$48(実質$4/月)
- Checkout: LP のボタンから(直リンクは貼らない)

## Q. tmux 対応の予定は? / tmux support?

**EN:**
> Detection already works with tmux. Jump is intentionally disabled for tmux because the tmux server daemonizes, which detaches sessions from the client terminal — jumping would hit the wrong window too often. If there's a reliable way to do it, I'm open to it.

**JA:**
> 検知は tmux でも動きます。ジャンプは、tmux サーバがデーモン化していてクライアントの端末と紐付かず誤爆しやすいため、意図的に非対応にしています。確実な方法があれば対応したいです。

---

## 返信の基本姿勢

- バグ報告 → 最優先で御礼+再現確認+修正予告。修正したら必ず本人に返信
- 批判(価格・サブスク) → 防御しない。理由を1回だけ説明し、平行線なら「フィードバックありがとう」で締める
- 競合ツールとの比較質問 → 相手を貶さない。「◯◯は△△が得意。AgentManager は待ち状態の自動表示とターミナルジャンプに全振りしている」の形
- 機能要望 → 「いいアイデア。検討リストに入れた」+実現可否の正直な見込み
