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
