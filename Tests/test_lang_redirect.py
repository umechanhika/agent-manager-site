#!/usr/bin/env python3
"""lang-redirect.js が日本語ブラウザの転送で計測を二重にせず、参照元も失わないことを検査する。

    python3 Tests/test_lang_redirect.py

背景（2026-10-18 の日次分析で検出）:

日本語ブラウザで英語版トップ "/" を開くと ja.html へ転送するが、転送は <body> 末尾の
スクリプトで行っていたため、"/" 側でも page_view・cta_variant_shown・section_view（hero）が
送られてから ja.html へ移っていた。GA4 実測（2026-09-18〜10-17、LP プロパティ）では言語
Japanese の "/" に page_view 20・cta_variant_shown 16・section_view 16 が記録され、同じ期間の
ja.html には参照元 https://agentmgr.app/ の page_view が 21 件あった。"/" の
cta_variant_shown 66 件のうち 16 件（24%）が誰も見ていない英語版の分母だった。

検査する不変条件:

1. 日本語ブラウザ（または am-lang = ja）の "/" は、クエリとハッシュを保ったまま ja.html へ
   転送し、"/" 側の GA4 送信をオプトアウトフラグで止める
2. 転送前の参照元を預け、ja.html 側は自分が転送した直後の読み込みでだけ
   window.amLangRedirectReferrer に戻す（預けた値は 1 回で消す）
3. 英語ブラウザ・am-lang = en では転送もフラグも立てない
4. sessionStorage が使えない場合は転送しない（参照元を失ったまま転送しない）
5. index.html / ja.html は lang-redirect.js を async / defer 無しで、Clarity と gtag.js の
   読み込みタグより前に読み込み、gtag('config') に page_referrer を渡す。
   <body> 側に転送処理を残さない（残すと "/" 側の計測が再び走る）
6. オプトアウトフラグの測定 ID が index.html の gtag の測定 ID と一致する

ロジックは Python に写さず、Node で lang-redirect.js 本体を実行して検査する。Node が
見つからない場合は黙って飛ばさずエラーにする。
"""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "lang-redirect.js"
HARNESS = Path(__file__).resolve().parent / "lang_redirect_harness.js"
KEY = "am-lang-redirect"


def run(**inp):
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("node が見つからない（このテストは lang-redirect.js 本体を Node で実行する）")
    out = subprocess.run(
        [node, str(HARNESS), str(SCRIPT), json.dumps(inp)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(out.stdout)


def measurement_id():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    return re.search(r"googletagmanager\.com/gtag/js\?id=(G-[A-Z0-9]+)", html).group(1)


class EnglishPageTests(unittest.TestCase):
    def test_japanese_browser_is_redirected_with_query_and_hash(self):
        r = run(href="https://agentmgr.app/?utm_source=zenn&utm_medium=article#pricing",
                htmlLang="en", navLanguage="ja-JP", referrer="https://www.google.com/")
        self.assertIsNone(r["error"])
        self.assertEqual(r["replacedTo"], "ja.html?utm_source=zenn&utm_medium=article#pricing")
        self.assertEqual(r["gaDisabled"], ["ga-disable-" + measurement_id()])
        self.assertEqual(json.loads(r["session"][KEY]), {
            # document.referrer にはハッシュが載らないため、照合用の from もハッシュ無しで預ける
            "from": "https://agentmgr.app/?utm_source=zenn&utm_medium=article",
            "referrer": "https://www.google.com/",
        })

    def test_saved_ja_preference_redirects_even_on_english_browser(self):
        r = run(href="https://agentmgr.app/", htmlLang="en", navLanguage="en-US", localLang="ja")
        self.assertEqual(r["replacedTo"], "ja.html")

    def test_english_browser_is_not_redirected_and_keeps_ga(self):
        r = run(href="https://agentmgr.app/", htmlLang="en", navLanguage="en-US")
        self.assertIsNone(r["replacedTo"])
        self.assertEqual(r["gaDisabled"], [])
        self.assertEqual(r["session"], {})

    def test_saved_en_preference_wins_over_japanese_browser(self):
        r = run(href="https://agentmgr.app/", htmlLang="en", navLanguage="ja", localLang="en")
        self.assertIsNone(r["replacedTo"])
        self.assertEqual(r["gaDisabled"], [])

    def test_no_redirect_when_session_storage_is_unavailable(self):
        r = run(href="https://agentmgr.app/", htmlLang="en", navLanguage="ja", sessionThrows=True)
        self.assertIsNotNone(r["error"])
        self.assertIsNone(r["replacedTo"])
        self.assertEqual(r["gaDisabled"], [])


class JapanesePageTests(unittest.TestCase):
    def handoff(self, referrer):
        return {KEY: json.dumps({"from": "https://agentmgr.app/", "referrer": referrer})}

    def test_restores_referrer_after_own_redirect(self):
        r = run(href="https://agentmgr.app/ja.html", htmlLang="ja", referrer="https://agentmgr.app/",
                session=self.handoff("https://www.google.com/"))
        self.assertEqual(r["amLangRedirectReferrer"], "https://www.google.com/")
        self.assertEqual(r["session"], {})
        self.assertIsNone(r["replacedTo"])
        self.assertEqual(r["gaDisabled"], [])

    def test_restores_empty_referrer_for_direct_visits(self):
        r = run(href="https://agentmgr.app/ja.html", htmlLang="ja", referrer="https://agentmgr.app/",
                session=self.handoff(""))
        self.assertEqual(r["amLangRedirectReferrer"], "")

    def test_ignores_stale_handoff_from_another_navigation(self):
        r = run(href="https://agentmgr.app/ja.html", htmlLang="ja", referrer="https://www.google.com/",
                session=self.handoff("https://x.com/"))
        self.assertIsNone(r["amLangRedirectReferrer"])
        self.assertEqual(r["session"], {})

    def test_nothing_without_handoff(self):
        r = run(href="https://agentmgr.app/ja.html", htmlLang="ja", referrer="")
        self.assertIsNone(r["amLangRedirectReferrer"])
        self.assertIsNone(r["error"])


class PageWiringTests(unittest.TestCase):
    def test_pages_load_script_before_clarity_and_gtag(self):
        for name in ("index.html", "ja.html"):
            html = (ROOT / name).read_text(encoding="utf-8")
            with self.subTest(page=name):
                tag = '<script src="/lang-redirect.js"></script>'
                self.assertEqual(html.count(tag), 1)
                pos = html.index(tag)
                self.assertLess(pos, html.index("clarity.ms/tag"))
                self.assertLess(pos, html.index("googletagmanager.com/gtag/js"))
                self.assertLess(pos, html.index("</head>"))
                self.assertIn("page_referrer: window.amLangRedirectReferrer", html)
                self.assertNotIn("location.replace('ja.html'", html)


if __name__ == "__main__":
    unittest.main()
