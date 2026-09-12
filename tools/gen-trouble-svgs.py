#!/usr/bin/env python3
"""困りごとセクション用の図版 (trouble-*.svg) を生成する。

機能画像 (feature-*.png, 600x375) と同じ配色・比率で、AgentManager が無い状態の
デスクトップを描く。テキストは英数のみ（index.html / ja.html で共用するため）。

    python3 tools/gen-trouble-svgs.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 600, 375
BG, WIN, BAR, BAR2 = "#0D1015", "#171B22", "#2A303A", "#3A414D"
BORDER = "rgba(255,255,255,.10)"
AMBER, BLUE, RED, GREEN, DIM, TEXT = "#F5A623", "#4E8BC8", "#DE5454", "#3BAD52", "#646C7A", "#E8EBF0"
MONO = "ui-monospace,SFMono-Regular,Menlo,monospace"


def window(x, y, w, h, focus=False):
    """ウィンドウの輪郭。focus=True のときだけアンバーの縁とにじみを付ける。"""
    g = []
    if focus:
        g.append(f'<rect x="{x-4}" y="{y-4}" width="{w+8}" height="{h+8}" rx="12" fill="{AMBER}" opacity=".14"/>')
    stroke = AMBER if focus else BORDER
    g.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{WIN}" stroke="{stroke}" stroke-width="{1.5 if focus else 1}"/>')
    g.append(f'<path d="M{x} {y+24} h{w}" stroke="{stroke}" opacity="{1 if focus else .8}"/>')
    return "\n".join(g)


def faint_bars(x, y, widths, gap=16):
    return "\n".join(f'<rect x="{x}" y="{y+i*gap}" width="{w}" height="6" rx="3" fill="{BAR}" opacity=".55"/>' for i, w in enumerate(widths))


def cursor(x, y, scale=1.6):
    p = "M0 0 l0 17 l4.5 -4 l3 7 l3.5 -1.5 l-3 -7 l6 -0.5 z"
    return f'<path transform="translate({x} {y}) scale({scale})" d="{p}" fill="#fff" stroke="#000" stroke-width="1" stroke-linejoin="round"/>'


def svg(body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">\n'
            f'<rect width="{W}" height="{H}" fill="{BG}"/>\n{body}\n</svg>\n')


# 図版はカード幅 ~215px（縮尺 0.36）で読む前提。焦点の文字は 30px 以上、それ以外は薄い線に落とす。

def cc_line(x, y, text, size=22, fill=DIM, weight="700", opacity="1"):
    return f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" font-weight="{weight}" fill="{fill}" opacity="{opacity}">{text}</text>'


def cc_prompt_box(x, y, w):
    """Claude Code の入力欄 (╭ > ╮) を輪郭で表す。"""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="40" rx="6" fill="none" stroke="{BORDER}"/>'
            + cc_line(x+14, y+28, "&gt;", size=22, fill=DIM))


# 1. 止まっているのに気づかない — 作業中のウィンドウの裏で、Claude Code が「Do you want to proceed?」のまま
def unnoticed():
    b = []
    b.append(window(16, 44, 444, 316, focus=True))
    b.append(cc_line(36, 262, "⏺ Bash(npm test)", size=20, fill=DIM))
    b.append(cc_line(36, 306, "Do you want to proceed?", size=28, fill=AMBER))
    b.append(cc_line(36, 344, "❯ 1. Yes", size=28, fill=TEXT))
    b.append(window(236, 16, 348, 262))
    b.append(faint_bars(258, 58, [220, 150, 250, 110, 200, 160]))
    b.append(f'<rect x="258" y="170" width="9" height="16" fill="{TEXT}" opacity=".8"/>')
    return svg("\n".join(b), "Claude Code asking Do you want to proceed, mostly hidden behind the window you are working in")


# 2. 見に行く手間 — 同じ窓を、カーソルが順番に巡回している
def checking():
    b = []
    cells = [(20, 24), (210, 24), (400, 24), (400, 200), (210, 200), (20, 200)]
    for x, y in cells:
        b.append(window(x, y, 180, 150))
    pts = " ".join(f"{x+90},{y+90}" for x, y in cells)
    b.append(f'<polyline points="{pts}" fill="none" stroke="{AMBER}" stroke-width="5" stroke-dasharray="14 12" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(cursor(100, 280, scale=2.4))
    return svg("\n".join(b), "Six identical windows with a dashed path looping through all of them and a cursor at the end: checking each one in turn")


# 3. 気付かぬ罠 — Claude Code が API エラーで落ちている。赤い 1 行だけ
def crash():
    b = []
    b.append(window(60, 24, 480, 326))
    b.append(cc_line(84, 74, "⏺ Bash(npm run build)", size=20, fill=DIM, opacity=".7"))
    b.append(faint_bars(84, 96, [300, 200]))
    b.append(cc_line(84, 186, "⏺ Edit(src/app.ts)", size=20, fill=DIM, opacity=".7"))
    b.append(cc_line(84, 252, "⎿  API Error: rate limited", size=28, fill=RED))
    b.append(cc_prompt_box(84, 290, 432))
    return svg("\n".join(b), "A Claude Code session that has stopped on a red API Error: rate limited line")


# 4. 途切れる記憶 — 出力の途中で圧縮が走り、前の文脈が切れている
def cutoff():
    b = []
    b.append(window(60, 24, 480, 326))
    b.append(cc_line(84, 74, "⏺ Read(src/app.ts)", size=20, fill=DIM, opacity=".7"))
    b.append(faint_bars(84, 96, [300, 200, 340]))
    b.append(cc_line(84, 190, "⏺ Edit(src/app.ts)", size=20, fill=DIM, opacity=".7"))
    b.append(f'<path d="M84 222 h432" stroke="{AMBER}" stroke-width="3" stroke-dasharray="10 10" opacity=".9"/>')
    b.append(cc_line(84, 268, "✻ Compacting…", size=28, fill=AMBER))
    b.append(faint_bars(84, 300, [260, 180]))
    return svg("\n".join(b), "A Claude Code session cut by a dashed line, with Compacting conversation in amber")


def main():
    for name, fn in (("trouble-unnoticed", unnoticed), ("trouble-checking", checking),
                     ("trouble-crash", crash), ("trouble-cutoff", cutoff)):
        out = ROOT / f"{name}.svg"
        out.write_text(fn(), encoding="utf-8")
        print("wrote", out.name, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
