// Tests/test_utm_self_referral_strip.py から呼ばれる utm-strip.js / utm.js の実行ハーネス。
//
// スクリプトをそのまま（コピーせず）読み込み、location / history / document を差し替えた
// コンテキストで実行して、結果を JSON で標準出力に出す。ロジックを Python 側へ写して
// 検査すると「写したコピー」を検査するだけになり、本体の退行を捕まえられない。
//
// 引数: <スクリプトのパス>... <入力 JSON>
//   スクリプトは渡した順に同じコンテキストで実行する（実ページの読み込み順を再現する。
//   utm-strip.js → utm.js の順で渡せば、除去後の URL を utm.js が読む）。
//   入力 JSON: { hostname, path（?query#hash を含む）, links（a.href の配列） }
//   出力 JSON: { replaced（history.replaceState に渡された URL の配列）,
//                finalSearch, finalPath, links（書き換え後の href）, selectors }
const fs = require('fs');
const vm = require('vm');

const scriptPaths = process.argv.slice(2, -1);
const input = JSON.parse(process.argv[process.argv.length - 1]);

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

const context = vm.createContext({ location, history, document, URL, URLSearchParams, console });
scriptPaths.forEach(function (p) { vm.runInContext(fs.readFileSync(p, 'utf8'), context); });

process.stdout.write(JSON.stringify({
  replaced: replaced,
  finalPath: current.pathname,
  finalSearch: current.search,
  finalHash: current.hash,
  links: links.map(function (l) { return l.href; }),
  selectors: selectors,
}));
