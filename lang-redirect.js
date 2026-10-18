// 日本語ブラウザで英語版トップ（index.html）を開いたときの ja.html への転送と、転送をまたいだ
// 参照元（document.referrer）の引き継ぎ。
//
// 本ファイルは index.html / ja.html の <head> の中で、Clarity と gtag.js の読み込みタグより前に、
// async / defer を付けずに読み込むこと。
//
// 転送を gtag.js より前に済ませる理由: 以前は <body> 末尾のスクリプトで転送していたため、
// 日本語ブラウザの訪問 1 回につき、英語版 "/" 側でも page_view・cta_variant_shown・
// section_view（hero）が送られてから ja.html へ移っていた。GA4 実測（2026-09-18〜10-17、
// LP プロパティ）では、言語 Japanese の "/" で page_view 20・cta_variant_shown 16・section_view 16 が
// 記録され、同じ期間の ja.html には参照元 https://agentmgr.app/ の page_view が 21 件あった。
// "/" の cta_variant_shown 66 件のうち 16 件（24%）は誰も見ていない英語版の分母で、
// CTA クリック率とセクション到達率が英語版・日本語版の両方で歪んでいた。
//
// 参照元を引き継ぐ理由: location.replace で移った先の document.referrer は転送元の
// "/" になる。そのままだと、Google 検索などから "/" に着地した日本語ブラウザの新規セッションが
// 自己参照として (direct) に落ちる（以前は "/" 側の page_view が元の参照元を持っていた）。
// 転送前の参照元を sessionStorage に預け、ja.html 側で window.amLangRedirectReferrer に戻して
// gtag('config') の page_referrer に渡す。utm_* はクエリとして URL に残るので別途運ばない。
//
// sessionStorage が使えない環境では setItem が例外を投げ、転送しない（英語版のまま表示され、
// 計測は "/" の 1 回だけになる）。参照元を失ったまま転送して流入元を誤分類させることはしない。
(function () {
  var KEY = 'am-lang-redirect';
  if (document.documentElement.lang === 'ja') {
    var raw = sessionStorage.getItem(KEY);
    if (raw === null) return;
    sessionStorage.removeItem(KEY);
    var handoff = JSON.parse(raw);
    // 自分が転送した直後の読み込みだけを対象にする（別経路で ja.html を開いた場合に古い値を使わない）。
    if (document.referrer === handoff.from) window.amLangRedirectReferrer = handoff.referrer;
    return;
  }
  var saved = '';
  try { saved = localStorage.getItem('am-lang') || ''; } catch (e) {}
  if (saved === 'en') return;
  var nav = (navigator.language || '').toLowerCase();
  if (!(saved === 'ja' || (!saved && nav.startsWith('ja')))) return;
  // from は転送先で document.referrer と照合する。referrer にはハッシュが載らないため外して預ける。
  sessionStorage.setItem(KEY, JSON.stringify({ from: location.href.split('#')[0], referrer: document.referrer }));
  // location.replace は呼んだ時点ではページを止めず、遷移が確定するまで後続の <head> の
  // スクリプトも実行される。gtag.js がキャッシュから先に届くと "/" の page_view が送られるため、
  // gtag.js 公式のオプトアウトフラグで "/" 側の送信を止める（測定 ID は index.html の gtag と同じ）。
  window['ga-disable-G-W72BR4X8Y6'] = true;
  // クエリとハッシュを引き継ぐ。引き継がないと日本語ブラウザで開いたキャンペーンリンクの
  // utm_* がこの遷移で消え、GA4 では流入元が失われて直接流入として計上されてしまう。
  location.replace('ja.html' + location.search + location.hash);
})();
