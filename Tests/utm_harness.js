// Tests/test_utm_self_referral_strip.py から呼ばれる utm.js の実行ハーネス。
//
// utm.js をそのまま（コピーせず）読み込み、location / history / document を差し替えた
// コンテキストで実行して、結果を JSON で標準出力に出す。ロジックを Python 側へ写して
// 検査すると「写したコピー」を検査するだけになり、utm.js 本体の退行を捕まえられない。
//
// 引数: <utm.js のパス> <入力 JSON>
//   入力 JSON: { hostname, path（?query#hash を含む）, links（a.href の配列） }
//   出力 JSON: { replaced（history.replaceState に渡された URL の配列）,
//                finalSearch, finalPath, links（書き換え後の href）, selectors }
const fs = require('fs');
const vm = require('vm');

const src = fs.readFileSync(process.argv[2], 'utf8');
const input = JSON.parse(process.argv[3]);

const origin = 'https://' + input.hostname;
const current = new URL(origin + input.path);

const location = {
  hostname: input.hostname,
  get pathname() { return current.pathname; },
  get search() { return current.search; },
  get hash() { return current.hash; },
};

const replaced = [];
const history = {
  replaceState(state, title, url) {
    replaced.push(url);
    // 実ブラウザと同じく、以降の location 読み取りに書き換え後の値が見えるようにする。
    const next = new URL(url, origin);
    current.pathname = next.pathname;
    current.search = next.search;
    current.hash = next.hash;
  },
};

const links = (input.links || []).map(function (href) {
  return { href: new URL(href, origin).toString() };
});
const selectors = [];
const document = {
  querySelectorAll(selector) {
    selectors.push(selector);
    // utm.js は DMG リンクだけを対象にする。セレクタに合う href だけ渡す。
    const needle = (selector.match(/href\*="([^"]+)"/) || [])[1];
    return links.filter(function (l) { return needle ? l.href.indexOf(needle) !== -1 : true; });
  },
};

vm.runInNewContext(src, { location, history, document, URL, URLSearchParams, console });

process.stdout.write(JSON.stringify({
  replaced: replaced,
  finalPath: current.pathname,
  finalSearch: current.search,
  finalHash: current.hash,
  links: links.map(function (l) { return l.href; }),
  selectors: selectors,
}));
