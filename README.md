# agent-manager-site

## 日本語ページ（ja.html）は生成物

`ja.html` は `index.html` から `tools/gen-ja.py` が生成する。**直接編集しない。**
日本語の文言は `index.html` 側に書く。表示テキストは `data-ja` 属性、href や aria-label のように
属性値が言語ごとに変わるものは `data-ja-<属性名>` 属性に書き、生成し直す。

```
python3 tools/gen-ja.py
```

`index.html` を編集したら必ず実行し、生成された `ja.html` も同じコミットに含める。
依存は beautifulsoup4（`pip install beautifulsoup4`）。

直接編集する、あるいは再生成を忘れると、日本語ページだけが古い内容のまま公開される。
過去にキャンペーンページへのリンクで `data-ja-href` を書かずに `ja.html` を手で辻褄合わせして
いたため、再生成した時点で日本語ページのリンク 4 本がすべて英語ページを指す状態になった。

このルールは CI が検査する。生成し直して `ja.html` に差分が出たら落ちる。手元で同じ確認をする:

```
python3 tools/gen-ja.py && git diff --exit-code -- ja.html
```

## テスト

```
python3 -m unittest discover -s Tests -p 'test_*.py'
```

CI（`.github/workflows/ci.yml`）が main への push と pull request で、上記の ja.html 検査と
あわせて実行する。

`Tests/test_utm_self_referral_strip.py` は `utm.js` 本体を Node で実行して検査するため Node が
必要（CI の ubuntu-latest にはプリインストール済み）。ロジックを Python 側へ写して検査すると
写したコピーを検査するだけになり、`utm.js` の退行を捕まえられないため実物を動かしている。

## 計測（GA4）の適用範囲

GA4 タグを持つ全ページは、`location.hostname` が本番ホスト `agentmgr.app`（CNAME で固定）の
ときだけ送信する。それ以外のホスト（`localhost` / `127.0.0.1` でのローカル確認、LAN の IP、
未公開ページのプレビュー）では gtag.js 公式のオプトアウトフラグ
`window['ga-disable-<測定ID>']` を立てて送信を止める。

- フラグは gtag.js 本体が到着する前に立てる必要があるため、`<script async src=...gtag/js...>`
  より前のインラインスクリプトに置く。
- ローカル確認ぶんが本番プロパティに混ざると、母数が小さいぶん CTR もチャネル内訳も
  そのまま歪む。特に `cta_variant_shown`（CTA クリック率の分母）は 1 ページビューにつき
  1 回送るため、ページを開くたびに分母だけが増える。
- 配信ホストを変える場合はこの判定も合わせて変える。判定に漏れると計測が丸ごと止まる。

このルールは `Tests/test_ga4_host_guard.py` が検査する。gtag.js を読み込むページにガードが無い /
ガードが読み込みタグより後ろにある / 測定 ID や本番ホスト（CNAME）と食い違う場合に落ちる。
ガードを持たないページをローカル配信すると、その page_view や CTA クリックがそのまま本番
プロパティに入る。

## 流入元の UTM（utm.js）

`utm.js` は全ページに読み込まれ、LP → アプリのチャネルアトリビューションを運ぶ。

- 流入 URL に `utm_*` があればそのまま維持し、ダウンロードリンクにも引き継ぐ。
- `utm_*` が無い訪問では、サイト自身を示す合成デフォルト（`utm_source` = ホスト名 /
  `utm_medium` = `website` / `utm_campaign` = パス名）を**ダウンロードリンクにのみ**付与する。
- **ページ URL 自体には合成デフォルトを書き足さない。** 書き込むと、リモート取得の gtag.js
  （async）が到着して `page_view` を組み立てる時点では既に URL が書き換わっており、直接流入・
  オーガニック検索・SNS 参照がすべて「`agentmgr.app` / `website`」という偽の流入元として
  記録される（同一オリジンの defer スクリプトである `utm.js` の方が先に走るため、この順序が常態）。
- 逆向きに、**合成デフォルトの署名で着弾した URL からはその utm を除去する。** 判定は
  `utm_source` が自ホスト **かつ** `utm_medium` が `website` の AND で、除去するのは
  合成デフォルトが書いていた 3 キーだけ。`ref=` 等の非 utm パラメータ・ハッシュ・パス名は残す。

最後の除去が必要な理由: 2026-08-28〜08-30 の不具合期間はページ URL への書き込みを行っていた。
書き込みは廃止したが、その期間に検索エンジンが索引した URL・ブックマーク・共有リンクは外部に
残り続けるため、そこからの流入は今も自己参照として誤分類される。GA4 実測では 2026-09-14 に
2 セッション・09-21 に 1 セッションが referrer = google.com（オーガニック検索）なのに
`agentmgr.app` / `website` に計上された（廃止の 15 日後・22 日後）。GA4 の「除外する参照の
リスト」は referrer ベースの判定で utm 由来の誤分類には効かないため、着弾時に URL 側を
直すのが唯一の対処になる。

このルールは `Tests/test_utm_self_referral_strip.py` が検査する。アプリ側の対応する仕様は
agent-manager の `docs/spec/08-telemetry-sentry-ga4.md`「新規ユーザー計測とチャネル
アトリビューション（app_first_open / UTM）」にある。
