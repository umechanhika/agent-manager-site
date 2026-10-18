// Tests/test_lang_redirect.py から呼ばれる lang-redirect.js の実行ハーネス。
//
// スクリプトをそのまま（コピーせず）読み込み、location / document / navigator / storage を
// 差し替えたコンテキストで実行して、結果を JSON で標準出力に出す。
//
// 引数: <lang-redirect.js のパス> <入力 JSON>
//   入力 JSON: { href, htmlLang, referrer, navLanguage, localLang（am-lang の値 or null）,
//                session（sessionStorage の初期内容）, sessionThrows（setItem が例外を投げる） }
//   出力 JSON: { replacedTo（location.replace の引数 or null）, session（実行後の内容）,
//                gaDisabled（ga-disable-* フラグの名前の配列）, amLangRedirectReferrer, error }
const fs = require('fs');
const vm = require('vm');

const scriptPath = process.argv[2];
const input = JSON.parse(process.argv[3]);
const url = new URL(input.href);

let replacedTo = null;
const location = {
  href: url.toString(),
  search: url.search,
  hash: url.hash,
  replace(to) { replacedTo = to; },
};
const session = Object.assign({}, input.session || {});
const sessionStorage = {
  getItem(k) { return Object.prototype.hasOwnProperty.call(session, k) ? session[k] : null; },
  setItem(k, v) {
    if (input.sessionThrows) throw new Error('SecurityError');
    session[k] = String(v);
  },
  removeItem(k) { delete session[k]; },
};
const localStorage = {
  getItem(k) { return k === 'am-lang' ? (input.localLang === undefined ? null : input.localLang) : null; },
};
const window = {};
const context = vm.createContext({
  window, location, sessionStorage, localStorage, JSON,
  navigator: { language: input.navLanguage || '' },
  document: { documentElement: { lang: input.htmlLang }, referrer: input.referrer || '' },
});
let error = null;
try {
  vm.runInContext(fs.readFileSync(scriptPath, 'utf8'), context);
} catch (e) {
  error = String(e.message || e);
}
process.stdout.write(JSON.stringify({
  replacedTo: replacedTo,
  session: session,
  gaDisabled: Object.keys(window).filter(function (k) { return k.indexOf('ga-disable-') === 0 && window[k] === true; }),
  amLangRedirectReferrer: Object.prototype.hasOwnProperty.call(window, 'amLangRedirectReferrer')
    ? window.amLangRedirectReferrer : null,
  error: error,
}));
