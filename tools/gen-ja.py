#!/usr/bin/env python3
"""index.html から日本語版 ja.html を生成する。

各要素の data-ja 属性を表示コンテンツとして展開し、head のメタ情報を
日本語版に差し替える。日本語テキストを静的 HTML として検索エンジンに
インデックスさせるためのもの。index.html を編集したら再実行する:

    python3 tools/gen-ja.py

依存: beautifulsoup4 (pip install beautifulsoup4)
"""
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
DST = ROOT / "ja.html"

TITLE = "AgentManager — Claude Code セッション監視ツール for macOS"
DESCRIPTION = (
    "全 Claude Code セッションを監視する macOS 用フローティングウィンドウ。"
    "確認が必要な瞬間に自動で現れ、見逃しを防ぎます。無料で使えます。"
)
OG_DESCRIPTION = (
    "Claude Code の確認待ちをもう見逃さない。"
    "全セッションを監視する macOS 用フローティングウィンドウ。無料で使えます。"
)
OG_IMAGE_ALT = "AgentManager — 確認待ちのセッションを見逃さない。"
# 日本語版OG画像。tools/og-image-ja.html を Chromium (1200x630) でスクリーンショットして生成する。
OG_IMAGE = "https://agentmgr.app/og-image-ja.png"
JA_URL = "https://agentmgr.app/ja.html"


def die(msg: str) -> None:
    print(f"gen-ja.py: {msg}", file=sys.stderr)
    sys.exit(1)


def find_one(soup, name, **attrs):
    tags = soup.find_all(name, **attrs)
    if len(tags) != 1:
        die(f"expected exactly 1 <{name} {attrs}>, found {len(tags)}")
    return tags[0]


def main() -> None:
    soup = BeautifulSoup(SRC.read_text(encoding="utf-8"), "html.parser")

    if soup.html is None:
        die("no <html> element")
    soup.html["lang"] = "ja"

    # data-ja 属性を各要素の表示コンテンツとして展開する。
    # 属性値は HTML 断片（<br> や <em> を含む）なのでパースして差し替える。
    targets = soup.select("[data-ja]")
    if len(targets) < 50:
        die(f"only {len(targets)} [data-ja] elements found — source layout changed?")
    for el in targets:
        frag = BeautifulSoup(el["data-ja"], "html.parser")
        el.clear()
        for child in list(frag.contents):
            el.append(child)

    # head の日本語化
    find_one(soup, "title").string = TITLE
    find_one(soup, "meta", attrs={"name": "description"})["content"] = DESCRIPTION
    find_one(soup, "link", rel="canonical")["href"] = JA_URL
    og = {
        "og:url": JA_URL,
        "og:title": TITLE,
        "og:description": OG_DESCRIPTION,
        "og:image": OG_IMAGE,
        "og:image:alt": OG_IMAGE_ALT,
        "og:locale": "ja_JP",
        "og:locale:alternate": "en_US",
    }
    for prop, value in og.items():
        find_one(soup, "meta", attrs={"property": prop})["content"] = value
    for name, value in {
        "twitter:title": TITLE,
        "twitter:description": OG_DESCRIPTION,
        "twitter:image": OG_IMAGE,
    }.items():
        find_one(soup, "meta", attrs={"name": name})["content"] = value

    # JSON-LD の説明文を日本語化
    ld = find_one(soup, "script", type="application/ld+json")
    data = json.loads(ld.string)
    data["description"] = DESCRIPTION
    data["inLanguage"] = "ja"
    ld.string = json.dumps(data, ensure_ascii=False, indent=2)

    # 言語トグルの active 状態を JA 側へ
    btn_en = find_one(soup, "button", id="btn-en")
    btn_ja = find_one(soup, "button", id="btn-ja")
    btn_en["class"] = [c for c in btn_en.get("class", []) if c != "active"]
    btn_ja["class"] = list(btn_ja.get("class", [])) + ["active"]

    # 日本語のみの要素（特商法リンク等）を表示状態に
    ja_only = soup.select(".ja-only")
    if not ja_only:
        die("no .ja-only elements found — source layout changed?")
    for el in ja_only:
        el["style"] = "display:inline"

    soup.html.insert_before(
        Comment(" generated from index.html by tools/gen-ja.py — 直接編集しない ")
    )
    soup.html.insert_before("\n")
    DST.write_text(str(soup), encoding="utf-8")
    print(f"wrote {DST} ({DST.stat().st_size} bytes, {len(targets)} elements translated)")


if __name__ == "__main__":
    main()
