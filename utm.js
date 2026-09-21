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
// - 過去に出回った自己参照 utm 付き URL で着弾した場合は、その utm をページ URL から除去する。
//
// ページ URL に合成デフォルトを書き足してはいけない。合成した値を history.replaceState で
// 現在の URL に書き込むと、リモート取得の gtag.js（async）が到着して page_view を組み立てる
// 時点では既に書き換え後の URL になっており、GA4 が直接流入・オーガニック検索・SNS 参照を
// すべて「agentmgr.app / website」という偽の流入元として記録してしまう（同一オリジンの
// defer スクリプトである本ファイルの方が先に走るため、この順序が常態になる）。
// 流入 utm の無いダウンロードは、アプリ側が kMDItemWhereFroms のページ URL のホストを
// source、"referral" を medium とするフォールバックで LP 経由と判別する。
(function () {
  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];

  // 過去に出回った「自己参照 utm 付き URL」からの流入を正しい流入元に戻す。
  //
  // 2026-08-28〜08-30 の不具合期間、上記の合成デフォルト（source = ホスト名 /
  // medium = website / campaign = パス名）をページ URL 自体へ書き込んでいた。書き込みは
  // c9cbd08 で廃止したが、その期間に検索エンジンが索引した URL・ブックマーク・共有リンクは
  // 外部に残り続けるため、そこからの流入は今も自己参照として誤分類される。実測: 2026-09-14 に
  // 2 セッション・09-21 に 1 セッションが referrer = google.com（オーガニック検索）なのに
  // GA4 では agentmgr.app / website に計上された（修正の 15 日後・22 日後）。
  // GA4 の「除外する参照のリスト」は referrer ベースの判定で utm 由来の誤分類には効かないため、
  // 着弾時に URL 側を直すのが唯一の対処になる。除去は gtag.js 本体が到着して page_view を
  // 組み立てる前に完了する（汚染が成立したのと同じ「defer が async より先」の順序を使う）。
  //
  // 除去するのは合成デフォルトが書いていた 3 キーだけ、かつ「utm_source が自ホスト」と
  // 「utm_medium が website」が**両方**成立した場合に限る。本物のキャンペーンが自サイトの
  // ホスト名を utm_source に使うことは無いため、正規の utm を取り違えて壊さない。
  // ref= のような utm 以外のパラメータはそのまま残す。
  var SYNTHESIZED_KEYS = ['utm_source', 'utm_medium', 'utm_campaign'];
  var arriving = new URLSearchParams(location.search);
  if (arriving.get('utm_source') === location.hostname
      && arriving.get('utm_medium') === 'website') {
    SYNTHESIZED_KEYS.forEach(function (key) { arriving.delete(key); });
    var rest = arriving.toString();
    history.replaceState(null, '', location.pathname + (rest ? '?' + rest : '') + location.hash);
  }

  // 除去後の URL を読む。自己参照 utm だけが載っていた URL はここで「utm 無し」になり、
  // 通常の直接訪問と同じ扱い（ダウンロードリンクにのみ合成デフォルトを付与）に合流する。
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
