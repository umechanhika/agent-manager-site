# AgentManager 初回プロモーション計画(司令塔)

- 期間: **2026-07-16(木)〜 2026-07-29(水)の14日間**(投稿実働 約10日)
- 目的: 初回リーチ獲得 → 7日間トライアル開始 → Day7〜13 の課金転換までを1サイクルで観測する
- 対象製品: AgentManager https://agentmgr.app/ (v1.12.5、2026-07-15 正式リリース済み)

## なぜ14日間か

- トライアルが7日間(カード不要)のため、初日に獲得したユーザーの課金転換は Day 7〜13 に発生する。プロモの成否はトライアル転換率まで見ないと判定できず、最低2週間の観測窓が必要。
- Product Hunt と Show HN は同日に重ねない(相互リンクを両コミュニティとも嫌う+一人で返信対応が回らない)。チャネルを分散すると自然に実働10日前後になる。
- 土日は投稿なし(返信対応のみ)。個人で回せる現実的な負荷にする。

## 日別スケジュール

| Day | 日付 | アクション | 時刻(JST) | 使うファイル |
|-----|------|-----------|-----------|--------------|
| 0 | 7/16(木) | X 日本語ローンチスレッド投稿。Xプロフィールに製品URL追記+固定ポスト設定 | 20:00–21:00 | [twitter-launch-ja.md](twitter-launch-ja.md) |
| 1 | 7/17(金) | zenn 技術記事公開 → X で告知(スレッドにぶら下げ) | 朝8時台 | [zenn-article.md](zenn-article.md) |
| 2–3 | 7/18–19(土日) | 投稿なし。返信・エゴサ・PH素材の最終確認(ギャラリー画像変換) | — | [product-hunt.md](product-hunt.md) の素材チェックリスト |
| 4 | 7/20(月) | Reddit r/ClaudeAI 投稿(英語) | 22:00–24:00 | [reddit-claudeai.md](reddit-claudeai.md) |
| 5 | 7/21(火) | note 開発ストーリー公開 + X 告知。PH の下書き最終確認 | 昼〜夜 | [note-article.md](note-article.md) |
| 6 | 7/22(水) | **Product Hunt ローンチ**。00:01 PDT = **JST 16:01 開始**。開始直後に maker comment 投稿 → X で連動投稿(英語+日本語) | 16:01〜24:00 張り付き | [product-hunt.md](product-hunt.md) / [twitter-ph-launch-en.md](twitter-ph-launch-en.md) |
| 7 | 7/23(木) | PH 継続(JST 16:00 終了)。終了後 X で結果報告 | 終日ウォッチ | [twitter-ph-launch-en.md](twitter-ph-launch-en.md) の結果報告テンプレ |
| 8 | 7/24(金) | **Show HN 投稿** + 直後2〜3時間コメント即応 | 21:00–23:00 | [show-hn.md](show-hn.md) |
| 9–10 | 7/25–26(土日) | 返信対応のみ | — | [faq-responses.md](faq-responses.md) |
| 11 | 7/27(月) | Reddit r/macapps 投稿(余力があれば。任意) | 22:00–24:00 | [reddit-macapps.md](reddit-macapps.md) |
| 12–13 | 7/28–29(火水) | 小ネタ投稿ストック消化開始、初週メトリクス集計、振り返り | 随時 | [twitter-followups-ja.md](twitter-followups-ja.md) |

タイムゾーンの根拠:

- **Product Hunt の1日は PST/PDT 00:01 起点**。7月は夏時間(PDT = UTC-7)なので JST は +16時間。「7/22 のローンチ」= JST 7/22(水) 16:01 〜 7/23(木) 16:00。日本在住だと開始が夕方に来るため、最重要の初動数時間を夜に張り付けてちょうど良い。
- Show HN・Reddit は米国東部の朝(= JST 21時〜24時)に投稿すると初動が乗りやすい。
- zenn は朝8時台公開(通勤時間帯のトレンド・はてブに乗りやすい)。

順序の根拠:

- 初日に PH をやらない。まず X + zenn で日本語圏に出し、初期バグ・混乱ポイントを潰してから英語圏(Reddit → PH → HN)に出す。初期バグを踏んだ状態で PH/HN に出るのが最悪パターン。
- HN の投稿・コメント内で PH に言及しない(HN は PH 誘導を嫌う)。逆も同様。

## チャネル要否の判断(提案)

| チャネル | 判断 | 理由 |
|---------|------|------|
| X(日本語) | **必須** | 日本の Claude Code コミュニティは X に集中。猫GIFが最大の拡散フック。継続発信の基盤 |
| zenn | **必須** | 技術記事でエンジニアリーチ+はてブ+検索流入の資産化。実装の面白ネタが豊富にある |
| Reddit r/ClaudeAI | **必須** | ターゲット純度が最も高い(Claude Code ユーザーそのもの)。自作ツール共有の文化があり歓迎されやすい |
| Product Hunt | **推奨(実施)** | 英語圏への一斉露出+恒久的なバックリンク。dev tool は PH と相性が良い。上位入賞は運次第だが露出自体に価値 |
| Show HN | **推奨(実施)** | 低コスト(タイトル+コメントのみ)で、当たれば最大のリーチ。期待値は低めに設定し、外れても気にしない |
| note | **推奨(zennより低優先)** | 開発ストーリーでファン化・信頼形成。直接コンバージョンは期待しない。PH/HN の結果を後日追記して「ローンチ記録」として二次利用 |
| Reddit r/macapps | **任意** | Mac アプリ好きへのリーチだが、サブスクに厳しい文化。本文に「なぜサブスクか」の先回り回答を入れる前提で、余力があれば |
| 英語専用Xアカウント新設 | **不要** | フォロワー0のアカウントは効果ゼロで運用コストだけ増える。日本語アカウントから「英語本文+日本語一文」形式で投稿する |

## 日別チェックリスト

### Day 0(7/16 木)投稿前

- [ ] LP・チェックアウト・DMGダウンロードが正常動作するか最終確認
- [ ] X プロフィールの bio に「AgentManager 開発者 https://agentmgr.app/」等を追記
- [ ] [twitter-launch-ja.md](twitter-launch-ja.md) の1投稿目を 20:00–21:00 に投稿、スレッドを続けて投稿
- [ ] 1投稿目を固定ポストに設定
- [ ] 投稿後1時間はリプライ即応

### Day 1(7/17 金)

- [ ] zenn 記事を朝8時台に公開(スラッグ・topics は [zenn-article.md](zenn-article.md) 冒頭のメモ参照)
- [ ] X で記事リンクを投稿(Day 0 スレッドにぶら下げ + 単独投稿)
- [ ] はてブ・zenn コメントをウォッチ

### Day 2–3(土日)

- [ ] PH ギャラリー画像の変換(8:5 素材 → 1270×760 推奨サイズ。[product-hunt.md](product-hunt.md) 参照)
- [ ] PH の製品ページ下書きを完成させ、7/22 00:01 PDT のスケジュール設定(または Coming Soon ページ)を行う
- [ ] エゴサ(X検索: `AgentManager` / `agentmgr`)と全件返信

### Day 4(7/20 月)

- [ ] r/ClaudeAI へ JST 22時以降に投稿([reddit-claudeai.md](reddit-claudeai.md))
- [ ] 投稿後2時間はコメント即応(英語は [faq-responses.md](faq-responses.md) を流用)

### Day 5(7/21 火)

- [ ] note 記事公開 + X 告知
- [ ] PH 下書き最終確認(tagline / gallery / topics / maker comment)

### Day 6–7(7/22 水〜7/23 木)PH 当日

- [ ] JST 16:01 ローンチ開始を確認
- [ ] 開始5分以内に maker first comment を投稿([product-hunt.md](product-hunt.md))
- [ ] X で連動投稿([twitter-ph-launch-en.md](twitter-ph-launch-en.md))
- [ ] JST 16:00–24:00 は全コメントに即応(その後は起床後に対応)
- [ ] 7/23 16:00 終了後、結果を X で報告(順位穴埋めテンプレ)

### Day 8(7/24 金)Show HN

- [ ] JST 21:00–23:00 に投稿([show-hn.md](show-hn.md)。URL投稿+直後に first comment)
- [ ] 投稿後2〜3時間はコメント即応。技術質問には正直に、辛口には防御的にならない
- [ ] HN 内で PH に言及しない

### Day 11–13

- [ ] r/macapps(任意)
- [ ] [twitter-followups-ja.md](twitter-followups-ja.md) のストックを消化開始(週2〜3本ペース)
- [ ] メトリクス集計(下記)

## 計測

- 全チャネルのリンクは [utm-links.md](utm-links.md) のURLをコピペで使う(`utm_campaign=launch-202607`)
- LP には GA4 + Clarity 導入済み。追加の計測設定は不要
- 見る指標: ①LPセッション数(ソース別) ②Freemius トライアル開始数 ③Day7〜13 の課金転換数 ④DMGダウンロード(GitHub release のダウンロードカウント)
- HN はタイトル横URLに UTM を付けられない(リファラで判別)。コメント内リンクのみ UTM 付き

## 初週の運用ルール

- **バグ報告は最優先**。初週に1回パッチを出し「報告→修正が速い」実績を PH/Reddit のコメントで示すのが最良の宣伝
- PH 当日と Show HN 直後の返信速度がスレッドの伸びに直結。[faq-responses.md](faq-responses.md) を開いたまま対応
- 感想ポストには全件返信(エゴサ: `AgentManager`, `agentmgr`)
- upvote の明示的な依頼はしない(PH 規約グレー)。「見に来てください」の表現に留める

## 初回プロモ後の継続施策(メモ)

- 週次で KPI 確認(LPセッション/トライアル開始/転換/解約)
- Freemius のトライアル終了前リマインドメール設定を確認(転換率を左右する)
- 月1回のアップデート告知を X + 軽い記事で回す「リリースノート駆動」
- Claude Code 本体の大型アップデート時に「対応しました」を即日投稿(検索需要に相乗り)
- zenn 2本目(別トピック)を1〜2ヶ月後に
