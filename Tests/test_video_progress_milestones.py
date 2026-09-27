#!/usr/bin/env python3
"""ヒーロー動画の video_progress しきい値が、日次レポート側の想定と揃っていることを検査する。

    python3 Tests/test_video_progress_milestones.py

しきい値の一覧は、アプリ側リポジトリ `agent-manager` の
`scripts/ga4-daily-report.py` の `VIDEO_MILESTONES` と**一対一で対応**する。
あちらは未知の `video_percent` を握り潰さず例外にする設計なので、LP 側だけ値を増やして
デプロイすると、翌日の日次レポートが動画セクションだけでなくスクリプトごと落ちる。
別リポジトリの定数はここから参照できないため、期待値をこのファイルに書き写して固定する。
値を変えるときは **先にアプリ側を更新してマージし、そのあとで両方をここに反映する**
（docs/spec/08-telemetry-sentry-ga4.md「しきい値を変えるときの順序」）。

5 / 10 を持つ理由: 動画は 50 秒で 25% は再生位置 12.5 秒。2026-09-27 時点の実測で、
過去 30 日の video_start 39 セッションに対し 25% 到達は 18（46%）しかなく、離脱の過半が
最初の 12.5 秒の内側で起きていた。2.5 秒（5%）と 5 秒（10%）がその区間の観測点になる。

検査する不変条件:

1. index.html / ja.html の双方にしきい値の配列がちょうど 1 つある
2. その中身が期待する一覧と完全に一致する（順序を含む。progress() は昇順を前提に
   from < line <= to で通過を判定する）
3. しきい値の送信が `video_progress` として行われている
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# agent-manager/scripts/ga4-daily-report.py の VIDEO_MILESTONES と一致させること。
EXPECTED_MILESTONES = ["5", "10", "25", "50", "75", "100"]

PAGES = ("index.html", "ja.html")

# progress() 内の `[5, 10, 25, ...].forEach(function(m) {` を拾う。
MILESTONE_RE = re.compile(r"\[([\d,\s]+)\]\.forEach\(function\s*\(m\)\s*\{")


def milestone_arrays(page: str):
    html = (ROOT / page).read_text(encoding="utf-8")
    return [
        [n.strip() for n in m.group(1).split(",") if n.strip()]
        for m in MILESTONE_RE.finditer(html)
    ]


class VideoProgressMilestonesTest(unittest.TestCase):
    def test_しきい値の配列がちょうど_1_つある(self):
        for page in PAGES:
            with self.subTest(page=page):
                found = milestone_arrays(page)
                self.assertEqual(
                    len(found), 1,
                    f"{page}: しきい値配列が {len(found)} 個見つかった（1 個であるべき）",
                )

    def test_しきい値がレポート側の想定と一致する(self):
        for page in PAGES:
            with self.subTest(page=page):
                self.assertEqual(
                    milestone_arrays(page)[0],
                    EXPECTED_MILESTONES,
                    f"{page}: しきい値が agent-manager の VIDEO_MILESTONES と食い違っている。"
                    " 先にアプリ側を更新してマージすること",
                )

    def test_英語版と日本語版で同じしきい値を送る(self):
        arrays = {page: milestone_arrays(page)[0] for page in PAGES}
        self.assertEqual(
            arrays["index.html"], arrays["ja.html"],
            f"言語で到達率の分母が変わってしまう: {arrays}",
        )

    def test_しきい値は_video_progress_として送られる(self):
        for page in PAGES:
            with self.subTest(page=page):
                html = (ROOT / page).read_text(encoding="utf-8")
                self.assertIn(
                    "track('video_progress', { video_percent: m })", html,
                    f"{page}: しきい値通過が video_progress として送られていない",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
