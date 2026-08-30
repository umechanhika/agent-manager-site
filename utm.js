// LP → アプリのチャネルアトリビューション用 UTM 付与スクリプト。
//
// macOS はブラウザでのダウンロード時に「ダウンロード元 URL・ダウンロード時に開いていた
// ページ URL」をファイルの拡張属性（kMDItemWhereFroms）として記録し、AgentManager は
// 初回起動時にそこから utm_* を読んで GA4 の first_open に流入元
// （session_source / session_medium / session_campaign）を付与する。
// GitHub Releases はリダイレクトの 1 ホップ目でダウンロード URL のクエリを落とすため、
// 「ダウンロード時に開いていたページ URL」が実効的な運搬経路になる。
//
// - 流入 URL に utm_* があればそのまま維持・引き継ぐ（キャンペーンリンク → アプリまで貫通）。
//   この場合ページ URL には最初から utm_* が載っているため、書き換えは不要。
// - 無ければサイト自身を示すデフォルトを「ダウンロードリンクにのみ」付与する。
//
// ページ URL 自体は書き換えないこと。合成したデフォルト値を history.replaceState で
// 現在の URL に書き込むと、リモート取得の gtag.js（async）が到着して page_view を組み立てる
// 時点では既に書き換え後の URL になっており、GA4 が直接流入・オーガニック検索・SNS 参照を
// すべて「agentmgr.app / website」という偽の流入元として記録してしまう（同一オリジンの
// defer スクリプトである本ファイルの方が先に走るため、この順序が常態になる）。
// 流入 utm の無いダウンロードは、アプリ側が kMDItemWhereFroms のページ URL のホストを
// source、"referral" を medium とするフォールバックで LP 経由と判別する。
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
})();
