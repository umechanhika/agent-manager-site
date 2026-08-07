# 日次 KPI レポート Routine

毎朝 7:00 JST（UTC 22:00）に Claude Code Remote の Routine が新規セッションを起動し、
GA4 から前日までのデータを取得・分析して、完了通知（push / email）でレポートを届ける。

- 前提: [setup-ga4-daily-report.md](./setup-ga4-daily-report.md) のセットアップが完了していること
- 前提: このドキュメント群と `scripts/ga4_report.py` が **main ブランチにマージ済み**であること
  （Routine の新規セッションは main をクローンするため）

## Routine 設定値

| 項目 | 値 |
|---|---|
| cron | `0 22 * * *`（UTC。= JST 毎朝 7:00） |
| セッション | 毎回新規セッション（`create_new_session_on_fire: true`） |
| 通知 | push + email |

## プロンプト全文（再作成時はこれをそのまま使う）

```
あなたは AgentManager LP（リポジトリ umechanhika/agent-manager-site、https://agentmgr.app）の日次KPIレポート担当です。

前提:
- KGI/KPI の定義はリポジトリの docs/kpi-tree.md に書かれている。分析の前に必ず読むこと。
- GA4 の認証情報は実行環境の環境変数 GA4_SA_KEY_JSON / GA4_PROPERTY_ID に設定済み。

手順:
1. リポジトリルートで `python3 scripts/ga4_report.py` を実行し、KPIデータのJSONを取得する。
2. スクリプトが失敗した場合: エラー内容をそのまま最終メッセージで報告して終了する。
   代替手段（gcloud、別のAPI呼び出し等）を試みない。スクリプトや設定を書き換えない。
3. 成功した場合、docs/kpi-tree.md の定義に従って以下を分析する:
   (a) KGI 前日値 = cta_click のうち header_trial + hero_trial + pricing_trial + hero_download
       （トライアルCTA / ダウンロードの内訳付き。pricing_monthly / pricing_annual はKGI外の補助指標として併記）
   (b) 前日比と直近7日平均比
   (c) ファネル: sessions → section_view(pricing) 到達率 → pricing系CTAのCVR
   (d) チャネル別・OS別の変化点
   (e) 特異な動き（急増・ゼロ・新チャネルの出現など）
   (f) 改善アクションの示唆を1〜3個
4. 結果は簡潔な日本語レポートとして最終メッセージ本文に出力する（完了通知にそのまま載る）。
   ファイルの保存・コミット・push は行わない。

注意:
- GA4 のデータ反映は24〜48時間遅れることがある。前日の数値が異常に少ない場合は
  「APIエラー」と「データ未反映」を区別して報告する。
- 数値がゼロの日も正常なレポートとして報告する（初期は流入が少ないのが普通）。
```

## 運用

- 即時テスト実行: このリポジトリのセッションで `fire_trigger` を Claude に依頼する
  （「日次レポートのRoutineを今すぐ発火して」）
- 停止/再開・時刻変更・プロンプト修正: Claude に依頼（`update_trigger` / `delete_trigger`）
- レポート形式を変えたいとき: このファイルのプロンプトを編集した上で、
  Claude に「daily-report-routine.md の内容で Routine のプロンプトを更新して」と依頼する
