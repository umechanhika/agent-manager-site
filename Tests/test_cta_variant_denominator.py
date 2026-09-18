#!/usr/bin/env python3
"""CTA を Mac / 非 Mac で出し分ける全ページが cta_variant_shown を送ることを検査する。

    python3 Tests/test_cta_variant_denominator.py

docs/spec/08-telemetry-sentry-ga4.md（アプリ側リポジトリ）「AgentManager LP プロパティ」の
ルールを実行可能な検査にしたもの。非 Mac 訪問者にはダウンロードボタンを隠すため、
cta_variant_shown が無いページでは「ダウンロードボタンが出ていたセッション」という
cta_click の分母が GA4 側に存在せず、クリック率として読めなくなる。

ルールは文章としては存在していたが強制する仕組みが無く、index.html / ja.html だけが送り、
ガイド 10 ページ（guides/*.html・guides/ja/*.html）は同じ出し分けをしながら送っていなかった。
その結果、2026-09-15 のガイド流入 6 ページビュー（オーガニック検索）に対して
cta_variant_shown が 0 件だった。新しいページがコミットされる時点で落とすことで、同じ穴を塞ぐ。

検査する不変条件（Mac / 非 Mac の出し分けをするページのみ対象）:

1. `gtag('event', 'cta_variant_shown', ...)` を送っている
2. その送信が `if (isMac) return;` の早期 return **より前** にある
   （後ろだと Mac 訪問者が送信前に抜け、分母が非 Mac ぶんだけになって逆に歪む）
3. 送る値が `isMac` 由来の `mac` / `nonmac` である
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 出し分けの判定そのもの。これを持つページだけが検査対象。
SWITCH_RE = re.compile(r"maxTouchPoints")
EARLY_RETURN_RE = re.compile(r"if\s*\(\s*isMac\s*\)\s*return\s*;")
SEND_RE = re.compile(
    r"gtag\(\s*'event'\s*,\s*'cta_variant_shown'\s*,\s*"
    r"\{\s*cta_variant\s*:\s*([^}]+?)\s*\}\s*\)"
)


def audit_html(text):
    """1 ページ分の HTML を検査し、問題の一覧を返す。出し分けをしないページは対象外。"""
    if not SWITCH_RE.search(text):
        return []

    send = SEND_RE.search(text)
    if not send:
        return [
            "Mac / 非 Mac で CTA を出し分けているが "
            "cta_variant_shown を送っていない（cta_click の分母が取れない）"
        ]

    problems = []

    value = send.group(1)
    if "isMac" not in value or "'mac'" not in value or "'nonmac'" not in value:
        problems.append(
            f"cta_variant の値 ({value}) が isMac 由来の 'mac' / 'nonmac' になっていない"
        )

    early_return = EARLY_RETURN_RE.search(text)
    if early_return and early_return.start() < send.start():
        problems.append(
            "cta_variant_shown の送信が `if (isMac) return;` より後ろにある"
            "（Mac 訪問者が送信前に抜け、分母が非 Mac ぶんだけになる）"
        )

    return problems


def html_files():
    return sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)


class TestRepositoryPages(unittest.TestCase):
    """リポジトリ内の全 HTML を実際に検査する。"""

    def test_every_switching_page_sends_cta_variant_shown(self):
        failures = []
        for path in html_files():
            text = path.read_text(encoding="utf-8")
            for problem in audit_html(text):
                failures.append(f"{path.relative_to(ROOT)}: {problem}")
        self.assertEqual(failures, [], "\n" + "\n".join(failures))

    def test_switching_pages_are_actually_found(self):
        """検査対象が 0 件だと、常に成功するだけの空回りのテストになる。"""
        switching = [
            p for p in html_files() if SWITCH_RE.search(p.read_text(encoding="utf-8"))
        ]
        self.assertGreater(
            len(switching), 0, "CTA を出し分けるページが 1 つも見つからない"
        )

    def test_guides_are_covered(self):
        """今回の穴はガイド 10 ページ。対象から外れていないことを明示的に固定する。"""
        guides = [
            p
            for p in html_files()
            if p.parent.name in ("guides", "ja") and "guides" in p.parts
        ]
        switching = [p for p in guides if SWITCH_RE.search(p.read_text(encoding="utf-8"))]
        self.assertGreater(len(switching), 0, "ガイドが 1 ページも検査対象になっていない")


GOOD = """<script>
  var isMac = ua.indexOf('Macintosh') !== -1 && navigator.maxTouchPoints <= 1;
  gtag('event', 'cta_variant_shown', { cta_variant: isMac ? 'mac' : 'nonmac' });
  if (isMac) return;
</script>"""


class TestDetection(unittest.TestCase):
    """検査自体が壊れ方を捕まえられることを、合成 HTML で確かめる。"""

    def test_good_page_passes(self):
        self.assertEqual(audit_html(GOOD), [])

    def test_page_without_switching_is_ignored(self):
        self.assertEqual(audit_html("<script>var x = 1;</script>"), [])

    def test_missing_send_is_detected(self):
        """実際に穴が空いていた形: 出し分けだけして分母を送らないページ。"""
        text = GOOD.replace(
            "gtag('event', 'cta_variant_shown', "
            "{ cta_variant: isMac ? 'mac' : 'nonmac' });",
            "",
        )
        self.assertIn("送っていない", " ".join(audit_html(text)))

    def test_send_after_early_return_is_detected(self):
        text = """<script>
  var isMac = ua.indexOf('Macintosh') !== -1 && navigator.maxTouchPoints <= 1;
  if (isMac) return;
  gtag('event', 'cta_variant_shown', { cta_variant: isMac ? 'mac' : 'nonmac' });
</script>"""
        self.assertIn("より後ろにある", " ".join(audit_html(text)))

    def test_constant_value_is_detected(self):
        text = GOOD.replace("isMac ? 'mac' : 'nonmac'", "'mac'")
        self.assertIn("cta_variant の値", " ".join(audit_html(text)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
