#!/usr/bin/env python3
"""トップページの構造化データが、ブランドの実体を宣言し続けていることを検査する。

    python3 Tests/test_structured_data.py

背景: 検索の指名検索（クエリ `agentmanager`）が Search Console で 28 日間
14 表示・0 クリック・平均掲載順位 7.2 だった（2026-08-28〜09-24）。自社ブランド名の
検索で 7 位ということは、検索エンジンが agentmgr.app をブランドの本拠として
扱えていないことを示す。構造化データが `SoftwareApplication` 1 ノードだけで、
ブランドの実体（Organization）も、その実体と公式プロフィールを結ぶ `sameAs` も
宣言していなかったため、それらを追加した。

検査する不変条件（index.html / ja.html の両方）:

1. `<script type="application/ld+json">` がちょうど 1 つあり、JSON として妥当である
2. `@graph` に Organization / WebSite / SoftwareApplication の 3 ノードが揃っている
3. Organization の `@id` は **両ページで同一**（ページごとに別 @id を振ると、同じブランドが
   2 つの実体に割れて指名検索の集約が効かない）
4. WebSite / SoftwareApplication は `publisher` で Organization の `@id` を参照している
5. WebSite / SoftwareApplication の `@id` と `url` は **そのページ自身**を指す
   （英語版の @id のまま日本語版を出すと、url だけ違う同一 @id のノードが 2 つできて矛盾する）
6. `sameAs` に並ぶのは、このサイト内から実際にリンクしている公式プロフィールだけ
   （実在しない URL を書くと誤った実体に結び付く。サイト内リンクとの一致で担保する）
"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

ORGANIZATION_ID = "https://agentmgr.app/#organization"

# ページ -> そのページ自身を指す正規 URL
PAGES = {
    "index.html": "https://agentmgr.app/",
    "ja.html": "https://agentmgr.app/ja.html",
}


def graph_of(page: str) -> dict:
    html = (ROOT / page).read_text(encoding="utf-8")
    blocks = LD_RE.findall(html)
    if len(blocks) != 1:
        raise AssertionError(f"{page}: ld+json ブロックが {len(blocks)} 個（1 個であるべき）")
    data = json.loads(blocks[0])
    return {node["@type"]: node for node in data["@graph"]}


class StructuredDataTest(unittest.TestCase):
    def test_required_nodes_present(self):
        for page in PAGES:
            with self.subTest(page=page):
                nodes = graph_of(page)
                for required in ("Organization", "WebSite", "SoftwareApplication"):
                    self.assertIn(required, nodes, f"{page} に {required} ノードが無い")

    def test_organization_id_is_shared_across_pages(self):
        ids = {page: graph_of(page)["Organization"]["@id"] for page in PAGES}
        self.assertEqual(
            set(ids.values()),
            {ORGANIZATION_ID},
            f"Organization の @id がページごとに割れている: {ids}",
        )

    def test_organization_url_is_the_brand_home(self):
        for page in PAGES:
            with self.subTest(page=page):
                org = graph_of(page)["Organization"]
                self.assertEqual(org["url"], "https://agentmgr.app/")
                self.assertEqual(org["name"], "AgentManager")

    def test_nodes_are_published_by_the_organization(self):
        for page in PAGES:
            for kind in ("WebSite", "SoftwareApplication"):
                with self.subTest(page=page, kind=kind):
                    node = graph_of(page)[kind]
                    self.assertEqual(
                        node.get("publisher"),
                        {"@id": ORGANIZATION_ID},
                        f"{page} の {kind} が Organization を publisher に参照していない",
                    )

    def test_page_scoped_nodes_point_at_their_own_page(self):
        for page, url in PAGES.items():
            nodes = graph_of(page)
            for kind, fragment in (("WebSite", "#website"), ("SoftwareApplication", "#software")):
                with self.subTest(page=page, kind=kind):
                    node = nodes[kind]
                    self.assertEqual(node["url"], url, f"{page} の {kind}.url がページ自身を指していない")
                    self.assertEqual(
                        node["@id"], f"{url}{fragment}",
                        f"{page} の {kind}.@id がページ自身を指していない",
                    )

    def test_page_scoped_nodes_declare_their_language(self):
        expected = {"index.html": "en", "ja.html": "ja"}
        for page, lang in expected.items():
            nodes = graph_of(page)
            for kind in ("WebSite", "SoftwareApplication"):
                with self.subTest(page=page, kind=kind):
                    self.assertEqual(nodes[kind].get("inLanguage"), lang)

    def test_same_as_entries_are_linked_from_the_site(self):
        """sameAs の URL が、実際にサイト内からリンクしている先であることを確かめる。

        実在しない公式アカウントを書き足すと、検索エンジンが別の実体に結び付ける。
        「サイト内のどこかから実際にリンクしている」ことを機械的な裏付けにする。
        """
        html = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(ROOT.glob("*.html"))
        )
        for page in PAGES:
            with self.subTest(page=page):
                same_as = graph_of(page)["Organization"]["sameAs"]
                self.assertTrue(same_as, f"{page}: sameAs が空")
                for url in same_as:
                    self.assertIn(
                        url, html,
                        f"{page}: sameAs の {url} がサイト内のどこからもリンクされていない",
                    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
