# AgentManager LP: KGI / KPI 定義

agentmgr.app（AgentManager のランディングページ）の成果を数値で判断するための指標定義。
日次レポート（Routine）・GA4 での分析は、すべてこのドキュメントの定義に従う。

## KGI（最終目標指標）

**トライアル獲得アクション数 / 日**

LP の役割は「訪問者にトライアル開始またはアプリ入手のアクションを起こさせること」。
Freemius チェックアウト完了（実際のトライアル登録・購入）は外部ドメインのためスコープ外とし、
Freemius ダッシュボードで別途確認する。

```
KGI = cta_click のうち cta_location が以下のもの
      ├─ トライアルCTA: header_trial + hero_trial + pricing_trial
      └─ ダウンロード:   hero_download
```

**KGI 集計定義（ホワイトリスト）**

| 区分 | cta_location | 設置場所 |
|---|---|---|
| KGI（トライアル） | `header_trial` | ヘッダー「Free trial」 |
| KGI（トライアル） | `hero_trial` | ヒーロー主CTA「Start 7-day free trial」 |
| KGI（トライアル） | `pricing_trial` | 料金表 無料トライアル |
| KGI（DL） | `hero_download` | ヒーロー副CTA「Download App」※Mac のみ表示 |
| 補助指標（KGI外） | `pricing_monthly` | 料金表 月額 $4.99 |
| 補助指標（KGI外） | `pricing_annual` | 料金表 年額 $48 |

- `pricing_monthly` / `pricing_annual` は「直接購入クリック」として補助的に追うが KGI に**含めない**。
- `producthunt_click` / `faq_toggle` / `hero_toggle` / `section_view` は行動指標であり KGI に**含めない**。

## KPI ツリー

KGI を 3 つのドライバーに分解する:

```
KGI（トライアル獲得アクション数）
  = ① 流入量 × ② 検討到達率 × ③ CTA転換率
```

### ① 流入（Acquisition）

| KPI | GA4 指標 / ディメンション |
|---|---|
| セッション数 | `sessions` |
| ユーザー数 / 新規ユーザー数 | `totalUsers` / `newUsers` |
| チャネル別流入 | `sessions` × `sessionDefaultChannelGroup` |
| 参照元別流入 | `sessionSource` / `sessionMedium` |
| OS 別セッション | `sessions` × `operatingSystem` |

★ ダウンロードボタン（`hero_download`）は Mac 以外では非表示になるゲートがあるため、
DL クリック率の**真の分母は「Macintosh セッション数」**。全セッションで割ると Mac 比率の変動に引きずられる。

### ② 検討到達（Engagement）

| KPI | 定義 | GA4 イベント |
|---|---|---|
| エンゲージメント率 | GA4 標準 | `engagementRate` |
| 機能理解率 | `section_view(features)` / sessions | `section_view` |
| **料金検討到達率 ★中間KPIの本命** | `section_view(pricing)` / sessions | `section_view` |
| 不安解消行動 | `section_view(faq)` 到達 + `faq_toggle(open)` 数 | `section_view` / `faq_toggle` |
| 完読率 | `scroll`(90%) / `page_view` | 拡張計測の `scroll` を流用 |
| 猫部屋関心 | `hero_toggle(cat)` / sessions | `hero_toggle` |

### ③ CVR（Conversion）

| KPI | 定義 |
|---|---|
| 総合 CVR | KGI クリック / sessions |
| CTA 位置別構成比 | `cta_location` 別クリック数（どの位置が効いているか） |
| 段間 CVR | `section_view(pricing)` 到達 → `cta_click(pricing_*)` |
| 外部評判確認 | `producthunt_click`（購入前の比較検討シグナル） |

### 基本ファネル

```
page_view → section_view(features) → section_view(pricing) → cta_click(KGI)
```

各段の通過率を見て、どこで離脱しているかで打ち手を決める:

- 流入が少ない → チャネル施策（Product Hunt、X、記事など）
- features 到達が低い → ヒーローのコピー・第一印象
- pricing 到達が低い → 機能訴求の説得力・ページ中盤の構成
- pricing 到達は高いが CTA 転換が低い → 価格・プラン・CTA 文言

## イベント設計

| イベント名 | パラメータ | 発火条件 | 実装 |
|---|---|---|---|
| `cta_click`（既存） | `cta_location`（上表 6 値） | `a[data-cta]` クリック | document 委譲リスナー。**KGI 専用として温存し、新規要素に `data-cta` を追加しない** |
| `section_view` | `section_id`: `pain` / `features` / `cat_mode` / `pricing` / `setup` / `faq` / `footer` | セクション上端がビューポート上部 70% 帯に初めて入った時。1 ページロードにつき各 1 回。※`footer` のみ例外: ページ最下部かつ背が低く 70% 帯に入れないため「少しでも可視になった＝最下部到達」で発火 | IntersectionObserver（`threshold: 0` + `rootMargin: '0px 0px -30% 0px'`、footer は rootMargin なし、発火後 `unobserve`） |
| `producthunt_click` | なし | Product Hunt バッジのクリック | document 委譲リスナー |
| `faq_toggle` | `faq_id`（スラッグ）、`faq_action`: `open` / `close` | FAQ `<details>` の開閉 | 各 details に個別 `toggle` リスナー（toggle はバブリングしないため） |
| `hero_toggle` | `hero_view`: `simple` / `cat` | スクショ切替で**状態が実際に変わった時のみ** | `showSimple` / `showCat` 内 |

※ ヒーローセクションは初期表示で常に可視のため `section_view` の対象外（`page_view` が代替）。

### GA4 拡張計測との整理

- `scroll`(90%): 温存。ページ全体の完読率として利用。スクロール深度の自作はしない。
- outbound `click`（自動計測）: Freemius / GitHub Releases / PH バッジで発火するが、分析には意味付けされた
  カスタムイベント（`cta_click` / `producthunt_click`）を使う。自動 `click` は生ログのバックアップ扱い。
- `file_download`: `.dmg` は GA4 デフォルト対象拡張子に含まれないため発火しない。
  `cta_click{hero_download}` が唯一の DL シグナルであり重複なし。

## GA4 側の設定（イベント実装のデプロイ直後に実施）

1. カスタムディメンション（イベントスコープ）を登録:
   `cta_location` / `section_id` / `faq_id` / `faq_action` / `hero_view`
   ※ **登録以降のデータしか Data API・探索レポートで参照できない**ため、デプロイ後すぐ実施する。
2. `cta_click` をキーイベント（Key Event）に指定。

## 日次レポートでの見方

毎朝の Routine レポートは以下を報告する:

- (a) KGI 前日値（トライアル CTA + DL の内訳付き）
- (b) 前日比・直近 7 日平均比
- (c) ファネル通過率（sessions → pricing 到達率 → pricing 系 CTA の CVR）
- (d) チャネル別・OS 別の変化点
- (e) 特異な動き（急増・ゼロ・新チャネル）
- (f) 改善アクションの示唆 1〜3 個

※ GA4 のデータ反映は 24〜48 時間遅れることがある。前日値が異常に少ない場合は
「計測エラー」ではなく「未反映」の可能性をまず疑う。
