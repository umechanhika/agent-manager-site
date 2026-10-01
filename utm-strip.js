// 過去に出回った「自己参照 utm 付き URL」からの流入を正しい流入元に戻す。
//
// 2026-08-28〜08-30 の不具合期間、utm.js は合成デフォルト（source = ホスト名 /
// medium = website / campaign = パス名）をページ URL 自体へ書き込んでいた。書き込みは
// c9cbd08 で廃止したが、その期間に検索エンジンが索引した URL・ブックマーク・共有リンクは
// 外部に残り続けるため、そこからの流入は今も自己参照として誤分類される。
// GA4 の「除外する参照のリスト」は referrer ベースの判定で utm 由来の誤分類には効かないため、
// 着弾時に URL 側を直すのが唯一の対処になる。
//
// 本ファイルは <head> の中で gtag.js の読み込みタグ（<script async>）より前に、async / defer を
// 付けずに読み込むこと。除去は gtag.js が page_view を組み立てる前に終わっていなければ効かない。
// 以前は utm.js（defer）の中で除去していたが、async の gtag.js は取得が終わった時点で HTML の
// 解析途中でも実行されるため「defer が async より先」は保証されない。実測（2026-09-30）では
// gtag.js が先に走り、汚染 URL のまま session_start が agentmgr.app / website に計上されたうえ、
// 後から走った replaceState を拡張計測が履歴変更として拾い、汚染 URL を referrer とする
// page_view が二重に送られた。同期スクリプトなら、パーサーは本ファイルの実行が終わるまで
// 後続の gtag.js 読み込みタグに到達しないため、この順序が常に成立する。
//
// 除去するのは合成デフォルトが書いていた 3 キーだけ、かつ「utm_source が自ホスト」と
// 「utm_medium が website」が**両方**成立した場合に限る。本物のキャンペーンが自サイトの
// ホスト名を utm_source に使うことは無いため、正規の utm を取り違えて壊さない。
// ref= のような utm 以外のパラメータ・ハッシュ・パス名はそのまま残す。
(function () {
  var SYNTHESIZED_KEYS = ['utm_source', 'utm_medium', 'utm_campaign'];
  var arriving = new URLSearchParams(location.search);
  if (arriving.get('utm_source') === location.hostname
      && arriving.get('utm_medium') === 'website') {
    SYNTHESIZED_KEYS.forEach(function (key) { arriving.delete(key); });
    var rest = arriving.toString();
    history.replaceState(null, '', location.pathname + (rest ? '?' + rest : '') + location.hash);
  }
})();
