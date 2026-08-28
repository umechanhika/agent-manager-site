// LP → アプリのチャネルアトリビューション用 UTM 付与スクリプト。
//
// macOS はブラウザでのダウンロード時に「ダウンロード元 URL・ダウンロード時に開いていた
// ページ URL」をファイルの拡張属性（kMDItemWhereFroms）として記録し、AgentManager は
// 初回起動時にそこから utm_* を読んで GA4 の first_open に流入元
// （session_source / session_medium / session_campaign）を付与する。
// GitHub Releases はリダイレクトの 1 ホップ目でダウンロード URL のクエリを落とすため、
// 「ダウンロード時に開いていたページ URL に utm を必ず載せる」ことが確実な運搬経路。
//
// - 流入 URL に utm_* があればそのまま維持・引き継ぐ（キャンペーンリンク → アプリまで貫通）
// - 無ければサイト自身を示すデフォルトを付与する（直接訪問も LP 経由と判別できるようにする）
(function () {
  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
  var incoming = new URLSearchParams(location.search);
  var utm = {};
  var hasIncoming = false;
  UTM_KEYS.forEach(function (key) {
    var value = incoming.get(key);
    if (value) { utm[key] = value; hasIncoming = true; }
  });
  if (!hasIncoming) {
    utm = {
      utm_source:   location.hostname,
      utm_medium:   'website',
      utm_campaign: location.pathname
    };
  }

  // ダウンロードリンクへ付与（クエリを保持する配布ホストへ変えた場合はそのまま届く）。
  document.querySelectorAll('a[href*="AgentManager.dmg"]').forEach(function (link) {
    var url = new URL(link.href);
    Object.keys(utm).forEach(function (key) { url.searchParams.set(key, utm[key]); });
    link.href = url.toString();
  });

  // ページ URL 側にも utm を反映する（kMDItemWhereFroms に記録される実効経路）。
  var pageUrl = new URL(location.href);
  Object.keys(utm).forEach(function (key) {
    if (!pageUrl.searchParams.get(key)) pageUrl.searchParams.set(key, utm[key]);
  });
  if (pageUrl.toString() !== location.href) {
    history.replaceState(history.state, '', pageUrl.toString());
  }
})();
