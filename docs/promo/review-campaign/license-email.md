# ライセンス受け取りメール（応募者向け）

キャンペーン応募者に Pro ライセンスの受け取り URL を送るメールの文面。手打ちで個別に送る前提。

## 差し込み項目

| プレースホルダ | 内容 |
| --- | --- |
| `{{受け取りURL}}` | Freemius で 100% オフクーポンを適用したチェックアウト URL |
| `{{期限}}` | このメールを送る日の 14 日後の日付 |
| `{{差出人名}}` | 署名に使う名前 |

## 送信前の確認

- **クーポンの使用回数に上限を設定する。** 100% オフの URL は踏めば誰でも使えるため、上限を設定しないまま拡散すると無制限に Pro が配られる。応募者ごとに 1 回限りのクーポンを発行するのが確実。
- **送信日を記録する。** 応募規約では期限を「ライセンス受け取りメールの送信日から 14 日以内」と定めているため、誰にいつ送ったかの記録がないと期限を判定できない。
- **宛名。** 応募フォームで氏名を取得している場合は、本文冒頭に宛名の行を足す。取得していない場合は現状のままでよい。

---

## 日本語

**件名:** 【AgentManager】Pro ライセンスの受け取りとレビューのお願い

```
Pro プラン モニターにご応募いただきありがとうございます。
Pro ライセンスの受け取りページをお送りします。

── 1. ライセンスを受け取る ──

次のページで受け取ってください。

{{受け取りURL}}

お支払いは発生しません。金額は $0 と表示され、カード情報の入力も不要です。
入力するメールアドレスは、応募時と同じものにしてください。レビューをいただいたときの照合に使います。

受け取りが完了すると、ライセンスキーが Freemius からメールで届きます。

── 2. アプリで有効化する ──

アプリをまだお持ちでない場合は、トップページからダウンロードしてください。

https://agentmgr.app/ja.html

アプリの設定画面でライセンスキーを入力すると、Pro プランが有効になります。

── 3. レビューを送る ──

実際にお使いいただいたうえで、100 字以上のレビューを次のフォームからお送りください。

https://forms.gle/R7Sw7Jbo4VUN3Tmn6

期限は {{期限}} です。
期限までにレビューが届かない場合、ライセンスは取り消しとなります。
取り消し後も、無料プランは引き続きお使いいただけます。

──

応募規約: https://agentmgr.app/review-campaign-ja.html
ご不明な点は、このメールにそのまま返信してください。

{{差出人名}}
AgentManager
```

---

## 英語

**Subject:** [AgentManager] Claim your Pro license

```
Thank you for applying to the Pro plan monitor program.
Here is the page to claim your Pro license.

── 1. Claim your license ──

Claim it from this page:

{{受け取りURL}}

There is no charge. The total shows as $0, and no card details are required.
Please enter the same email address you applied with. We use it to match your review.

Once you are done, Freemius will email you your license key.

── 2. Activate the app ──

If you do not have the app yet, download it from our home page.

https://agentmgr.app/

Enter the license key in the app's settings to activate Pro.

── 3. Send your review ──

After you have used the app, send a review of 100 characters or more through this form.

https://forms.gle/ABtTZ4Jr7gfBwt7E9

The deadline is {{期限}}.
If we do not receive your review by then, the license will be revoked.
You can keep using the free plan after that.

──

Terms: https://agentmgr.app/review-campaign.html
If you have any questions, just reply to this email.

{{差出人名}}
AgentManager
```
