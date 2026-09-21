#!/usr/bin/env python3
"""utm.js が「自己参照 utm 付き URL」からの流入を正しい流入元に戻すことを検査する。

    python3 Tests/test_utm_self_referral_strip.py

背景（2026-09-21 の日次分析で検出）:

2026-08-28〜08-30 の不具合期間、utm.js は合成デフォルト（utm_source = ホスト名 /
utm_medium = website / utm_campaign = パス名）を history.replaceState でページ URL 自体に
書き込んでいた。書き込みは c9cbd08 で廃止したが、その期間に検索エンジンが索引した URL・
ブックマーク・共有リンクは外部に残るため、そこからの流入は今も自己参照として誤分類される。
GA4 実測では 2026-09-14 に 2 セッション・09-21 に 1 セッションが referrer = google.com
（オーガニック検索）なのに agentmgr.app / website に計上された（廃止の 15 日後・22 日後）。
GA4 の「除外する参照のリスト」は referrer ベースの判定のため utm 由来の誤分類には効かず、
着弾時に URL 側を直すのが唯一の対処になる。

検査する不変条件:

1. 合成デフォルトの署名（utm_source = 自ホスト **かつ** utm_medium = website）で着弾したら、
   その 3 キーをページ URL から除去する（gtag.js が page_view を組み立てる前に完了する）
2. utm 以外のパラメータ（ref= 等）・ハッシュ・パス名は保持する
3. 本物のキャンペーン utm は書き換えない（署名が片方しか一致しない場合も書き換えない）
4. 合成デフォルトのダウンロードリンクへの付与は従来どおり維持される（除去後の URL は
   「utm 無しの直接訪問」と同じ扱いに合流する）

ロジックは Python に写さず、Node で utm.js 本体を実行して検査する（写すと「コピー」を
検査するだけになり、utm.js の退行を捕まえられない）。Node は CI の ubuntu-latest に
プリインストールされている。見つからない場合は黙って飛ばさずエラーにする。
"""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UTM_JS = ROOT / "utm.js"
HARNESS = Path(__file__).resolve().parent / "utm_harness.js"

HOST = "agentmgr.app"
DMG = "https://github.com/umechanhika/agent-manager-site/releases/latest/download/AgentManager.dmg"

# 実際に GA4 に記録されていた汚染 URL のクエリ（utm_campaign=%2F は "/" のエンコード）。
POLLUTED_ROOT = "?utm_source=agentmgr.app&utm_medium=website&utm_campaign=%2F"


def node():
    exe = shutil.which("node")
    if exe is None:
        raise AssertionError(
            "node が見つかりません。utm.js 本体を実行して検査するため Node が必要です"
            "（CI の ubuntu-latest にはプリインストール済み）")
    return exe


def run_utm(path, links=(DMG,), hostname=HOST):
    """utm.js を差し替えコンテキストで実行し、結果の dict を返す。"""
    payload = json.dumps({"hostname": hostname, "path": path, "links": list(links)})
    out = subprocess.run(
        [node(), str(HARNESS), str(UTM_JS), payload],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


class TestSelfReferralStripping(unittest.TestCase):
    """汚染 URL で着弾したときにページ URL から自己参照 utm を落とすこと。"""

    def test_polluted_root_is_cleaned(self):
        r = run_utm("/" + POLLUTED_ROOT)
        self.assertEqual(r["replaced"], ["/"])
        self.assertEqual(r["finalSearch"], "")
        self.assertEqual(r["finalPath"], "/")

    def test_polluted_subpage_keeps_its_path(self):
        """ガイドページの汚染 URL（campaign にパス名が入る形）も実際に記録されていた。"""
        page = "/guides/ja/claude-code-hooks-session-status.html"
        r = run_utm(page + "?utm_source=agentmgr.app&utm_medium=website"
                           "&utm_campaign=%2Fguides%2Fja%2Fclaude-code-hooks-session-status.html")
        self.assertEqual(r["replaced"], [page])
        self.assertEqual(r["finalPath"], page)
        self.assertEqual(r["finalSearch"], "")

    def test_non_utm_params_and_hash_survive(self):
        r = run_utm("/?ref=producthunt&utm_source=agentmgr.app"
                    "&utm_medium=website&utm_campaign=%2F#pricing")
        self.assertEqual(r["replaced"], ["/?ref=producthunt#pricing"])
        self.assertEqual(r["finalSearch"], "?ref=producthunt")
        self.assertEqual(r["finalHash"], "#pricing")

    def test_cleaned_visit_still_tags_the_download_link(self):
        """除去後は「utm 無しの直接訪問」と同じ扱いに合流し、リンク付与は従来どおり。"""
        r = run_utm("/" + POLLUTED_ROOT)
        self.assertEqual(len(r["links"]), 1)
        self.assertIn("utm_source=agentmgr.app", r["links"][0])
        self.assertIn("utm_medium=website", r["links"][0])
        self.assertIn("utm_campaign=%2F", r["links"][0])
        self.assertTrue(r["links"][0].startswith("https://github.com/"))


class TestGenuineCampaignsAreUntouched(unittest.TestCase):
    """正規の流入 utm を取り違えて壊さないこと。"""

    def test_real_campaign_is_not_rewritten(self):
        q = "?utm_source=producthunt&utm_medium=referral&utm_campaign=launch-202607"
        r = run_utm("/" + q)
        self.assertEqual(r["replaced"], [])
        self.assertEqual(r["finalSearch"], q)
        self.assertIn("utm_source=producthunt", r["links"][0])
        self.assertIn("utm_medium=referral", r["links"][0])

    def test_self_host_source_with_other_medium_is_not_rewritten(self):
        """署名は 2 条件の AND。medium が website でなければ触らない。"""
        q = "?utm_source=agentmgr.app&utm_medium=email&utm_campaign=newsletter"
        r = run_utm("/" + q)
        self.assertEqual(r["replaced"], [])
        self.assertEqual(r["finalSearch"], q)

    def test_website_medium_from_other_source_is_not_rewritten(self):
        q = "?utm_source=partner.example&utm_medium=website&utm_campaign=banner"
        r = run_utm("/" + q)
        self.assertEqual(r["replaced"], [])
        self.assertEqual(r["finalSearch"], q)

    def test_clean_visit_is_not_rewritten(self):
        r = run_utm("/")
        self.assertEqual(r["replaced"], [])
        self.assertEqual(r["finalSearch"], "")
        self.assertIn("utm_medium=website", r["links"][0])


class TestPageUrlIsNeverDecorated(unittest.TestCase):
    """合成デフォルトをページ URL に書き足す退行（c9cbd08 で廃止した挙動）を禁じる。"""

    def test_clean_visit_never_gains_utm_in_page_url(self):
        for path in ("/", "/ja.html", "/guides/index.html"):
            with self.subTest(path=path):
                r = run_utm(path)
                self.assertEqual(r["replaced"], [], f"{path} でページ URL が書き換えられた")
                self.assertNotIn("utm_", r["finalSearch"])

    def test_only_download_links_are_selected(self):
        """ページ内リンク全般に utm を付けると内部遷移が自己参照流入になる。"""
        r = run_utm("/", links=(DMG, "https://agentmgr.app/ja.html"))
        self.assertTrue(
            all("AgentManager.dmg" in s for s in r["selectors"]),
            f"DMG リンク以外を対象にするセレクタがある: {r['selectors']}")
        internal = [h for h in r["links"] if "agentmgr.app/ja.html" in h]
        self.assertEqual(len(internal), 1)
        self.assertNotIn("utm_", internal[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
