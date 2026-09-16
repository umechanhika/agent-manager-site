#!/usr/bin/env python3
"""GA4 タグを持つ全ページが本番ホスト限定ガードを備えていることを検査する。

    python3 Tests/test_ga4_host_guard.py

README「計測（GA4）の適用範囲」のルールを実行可能な検査にしたもの。ルールは文章としては
存在していたが強制する仕組みが無く、リポジトリ外で作られたページ（未コミットの
review-campaign-ja.html）がガードを持たないままローカル配信され、127.0.0.1 からの
page_view / cta_click / section_view が本番プロパティに入った（2026-09-12・09-13）。
新しいページがコミットされる時点で落とすことで、同じ入り方を塞ぐ。

検査する不変条件（gtag.js を読み込むページのみ対象）:

1. `window['ga-disable-<測定ID>']` をホスト判定付きで立てている
2. そのガードが gtag.js の読み込みタグ **より前** にある
   （後ろだと gtag.js が先に走り、フラグが間に合わず送信が止まらない）
3. ガード・読み込みタグ・`gtag('config', ...)` の測定 ID が一致している
4. ガードが許可する本番ホストが CNAME と一致している
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LOADER_RE = re.compile(r"googletagmanager\.com/gtag/js\?id=(G-[A-Z0-9]+)")
GUARD_RE = re.compile(
    r"location\.hostname\s*!==\s*'([^']+)'\s*\)?\s*"
    r"window\[\s*'ga-disable-(G-[A-Z0-9]+)'\s*\]\s*=\s*true"
)
CONFIG_RE = re.compile(r"gtag\(\s*'config'\s*,\s*'(G-[A-Z0-9]+)'")


def production_host():
    """配信ホストの正は CNAME。ガードの判定先はこれと一致していなければならない。"""
    return (ROOT / "CNAME").read_text(encoding="utf-8").strip()


def audit_html(text, expected_host):
    """1 ページ分の HTML を検査し、問題の一覧を返す。gtag.js を読まないページは対象外。"""
    loader = LOADER_RE.search(text)
    if not loader:
        return []

    problems = []
    loader_id = loader.group(1)

    guard = GUARD_RE.search(text)
    if not guard:
        problems.append(
            f"gtag.js ({loader_id}) を読み込んでいるが "
            f"window['ga-disable-...'] のホストガードが無い"
        )
        return problems

    guard_host, guard_id = guard.group(1), guard.group(2)

    if guard.start() > loader.start():
        problems.append(
            "ホストガードが gtag.js の読み込みタグより後ろにある"
            "（gtag.js が先に走りフラグが間に合わない）"
        )
    if guard_id != loader_id:
        problems.append(
            f"ガードの測定 ID ({guard_id}) が読み込みタグ ({loader_id}) と違う"
        )
    if guard_host != expected_host:
        problems.append(
            f"ガードの本番ホスト ({guard_host}) が CNAME ({expected_host}) と違う"
        )

    config = CONFIG_RE.search(text)
    if config and config.group(1) != loader_id:
        problems.append(
            f"gtag('config') の測定 ID ({config.group(1)}) が "
            f"読み込みタグ ({loader_id}) と違う"
        )

    return problems


def html_files():
    return sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)


class TestRepositoryPages(unittest.TestCase):
    """リポジトリ内の全 HTML を実際に検査する。"""

    def test_every_tagged_page_has_host_guard(self):
        host = production_host()
        failures = []
        for path in html_files():
            text = path.read_text(encoding="utf-8")
            for problem in audit_html(text, host):
                failures.append(f"{path.relative_to(ROOT)}: {problem}")
        self.assertEqual(failures, [], "\n" + "\n".join(failures))

    def test_tagged_pages_are_actually_found(self):
        """検査対象が 0 件だと、常に成功するだけの空回りのテストになる。"""
        tagged = [p for p in html_files() if LOADER_RE.search(p.read_text(encoding="utf-8"))]
        self.assertGreater(len(tagged), 0, "gtag.js を読み込むページが 1 つも見つからない")


GOOD = """<head>
  <script>
    if (location.hostname !== 'agentmgr.app') window['ga-disable-G-W72BR4X8Y6'] = true;
  </script>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-W72BR4X8Y6"></script>
  <script>gtag('config', 'G-W72BR4X8Y6');</script>
</head>"""


class TestDetection(unittest.TestCase):
    """検査自体が壊れ方を捕まえられることを、合成 HTML で確かめる。"""

    def test_good_page_passes(self):
        self.assertEqual(audit_html(GOOD, "agentmgr.app"), [])

    def test_page_without_gtag_is_ignored(self):
        self.assertEqual(audit_html("<head><title>x</title></head>", "agentmgr.app"), [])

    def test_missing_guard_is_detected(self):
        """実際に混入を起こした形: ガードを持たないページ。"""
        text = GOOD.replace(
            "if (location.hostname !== 'agentmgr.app') "
            "window['ga-disable-G-W72BR4X8Y6'] = true;",
            "",
        )
        self.assertIn("ホストガードが無い", " ".join(audit_html(text, "agentmgr.app")))

    def test_guard_after_loader_is_detected(self):
        text = """<head>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-W72BR4X8Y6"></script>
  <script>
    if (location.hostname !== 'agentmgr.app') window['ga-disable-G-W72BR4X8Y6'] = true;
  </script>
</head>"""
        self.assertIn("より後ろにある", " ".join(audit_html(text, "agentmgr.app")))

    def test_stale_measurement_id_in_guard_is_detected(self):
        text = GOOD.replace("ga-disable-G-W72BR4X8Y6", "ga-disable-G-OLD12345")
        self.assertIn("測定 ID", " ".join(audit_html(text, "agentmgr.app")))

    def test_host_mismatch_with_cname_is_detected(self):
        self.assertIn("本番ホスト", " ".join(audit_html(GOOD, "example.com")))

    def test_generated_ja_html_attribute_style_is_accepted(self):
        """ja.html は gen-ja.py（BeautifulSoup）が async="" に正規化して出力する。"""
        text = GOOD.replace("<script async src=", '<script async="" src=')
        self.assertEqual(audit_html(text, "agentmgr.app"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
