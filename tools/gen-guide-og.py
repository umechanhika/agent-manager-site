#!/usr/bin/env python3
"""ガイドページ用の OGP 画像 (1200x630) を生成する。

tools/og-guide-template.html のプレースホルダを記事ごとに差し替え、
Playwright (Chromium) のスクリーンショットで guides/og/ に PNG を書き出す。
タイトルを変えたら再実行する:

    python3 tools/gen-guide-og.py [--chromium /path/to/chromium]

依存: playwright (pip install playwright)。--chromium 未指定時は
Playwright 管理の Chromium を使う (playwright install chromium)。

注意: chromium 単体の --headless --screenshot は viewport の解釈が
ずれて下端が欠けるため使わない (Playwright は viewport を厳密に扱う)。
"""
import argparse
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "tools" / "og-guide-template.html"
OUT_DIR = ROOT / "guides" / "og"

# slug → (lang, タイトルHTML, タイトルfont-size)
# タイトルは 2〜3 行・アクセント 1 箇所を目安にする。
PAGES = {
    "manage-multiple-claude-code-sessions": (
        "en",
        'How to manage multiple<br>Claude Code sessions,<br><span class="accent">without losing track.</span>',
        60,
    ),
    "manage-multiple-claude-code-sessions.ja": (
        "ja",
        'Claude Code の複数セッションを<br><span class="accent">見失わずに管理する</span>',
        58,
    ),
    "claude-code-notifications-macos": (
        "en",
        'Claude Code notifications<br>on macOS —<br><span class="accent">never miss a prompt.</span>',
        60,
    ),
    "claude-code-notifications-macos.ja": (
        "ja",
        'Claude Code の完了・確認待ちに<br><span class="accent">気づける</span>、<br>macOS 通知設定ガイド',
        54,
    ),
    "claude-code-hooks-session-status": (
        "en",
        'Tracking Claude Code<br>session status <span class="accent">with hooks</span>',
        62,
    ),
    "claude-code-hooks-session-status.ja": (
        "ja",
        'Claude Code hooks で<br>セッション状態を<span class="accent">追跡する</span>',
        58,
    ),
}

LABELS = {
    "en": ("Waiting", "Running", "Done"),
    "ja": ("確認待ち", "処理中", "完了"),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chromium", default=None,
                    help="Chromium/Chrome 実行ファイルのパス (省略時は Playwright 管理版)")
    args = ap.parse_args()

    template = TEMPLATE.read_text(encoding="utf-8")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        launch_kw = {"args": ["--no-sandbox"]}
        if args.chromium:
            launch_kw["executable_path"] = args.chromium
        browser = pw.chromium.launch(**launch_kw)
        page = browser.new_page(viewport={"width": 1200, "height": 630})

        for slug, (lang, title_html, size) in PAGES.items():
            waiting, running, done = LABELS[lang]
            html = (template
                    .replace("{{LANG}}", lang)
                    .replace("{{TITLE_HTML}}", title_html)
                    .replace("{{TITLE_SIZE}}", str(size))
                    .replace("{{LABEL_WAITING}}", waiting)
                    .replace("{{LABEL_RUNNING}}", running)
                    .replace("{{LABEL_DONE}}", done))
            # ../logo-dark.svg の相対参照を効かせるため tools/ 配下に一時ファイルを置く
            with tempfile.NamedTemporaryFile(
                    "w", suffix=".html", dir=TEMPLATE.parent,
                    encoding="utf-8", delete=False) as f:
                f.write(html)
                tmp = Path(f.name)
            out = OUT_DIR / f"{slug}.png"
            try:
                page.goto(tmp.as_uri())
                page.screenshot(path=out)
            finally:
                tmp.unlink()
            print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size} bytes)")

        browser.close()


if __name__ == "__main__":
    main()
