#!/usr/bin/env python3
"""Generate the profile README graphics (dark + light) into assets/.

    python3 scripts/build.py

Edit LINES below and re-run. No dependencies. The SVGs use only
SMIL animation and system monospace fonts, so they render inside GitHub's
<img> sandbox (no scripts, no web fonts).
"""
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

THEMES = {
    "dark": dict(bg0="#070D14", bg1="#0B141D", panel="#0F1B26", line="#1F3140",
                 fg="#D7E3EC", muted="#7C8FA0", accent="#3DDC97",
                 accent2="#38BDF8", warn="#F5B84B"),
    "light": dict(bg0="#EEF2F6", bg1="#FFFFFF", panel="#F6F8FB", line="#D0D7E2",
                  fg="#1F2937", muted="#5B6779", accent="#0E8F68",
                  accent2="#0B7FA0", warn="#A86200"),
}

# Terminal session shown in the banner. ("cmd", text) is typed out;
# ("out", [(text, colour-key), ...]) appears underneath it.
LINES = [
    ("cmd", "whoami"),
    ("out", [("janyris", "accent2"), ("  IT professional → SOC / blue team", "fg")]),
    ("cmd", "cat focus.txt"),
    ("out", [("cybersecurity · security operations · AI", "fg")]),
    ("cmd", "certs --status"),
    ("out", [("CompTIA Security+ ....... ", "fg"), ("in progress", "warn"), (" · Oct 2026", "muted")]),
    ("out", [("Splunk Core User ........ ", "fg"), ("in progress", "warn"), (" · Oct 2026", "muted")]),
    ("cmd", "locate --self"),
    ("out", [("New York, NY", "fg")]),
]

CYCLE = 18.0       # seconds for one full banner loop
SWEEP = 6.0        # seconds per radar revolution


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")


def visible(start, end=0.965):
    """Opacity animation: hidden until `start` (0..1 of CYCLE), shown until `end`."""
    return (f'<animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="0;{f(start)};{f(end)};1" values="0;1;0;0"/>')


def radar(c, cx, cy, r):
    import math
    out = [f'<g fill="none" stroke="{c["line"]}">']
    for k in (1, 2 / 3, 1 / 3):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{f(r * k)}"/>')
    out.append(f'<path d="M{cx - r} {cy}H{cx + r}M{cx} {cy - r}V{cy + r}"/></g>')

    def wedge(deg, op):
        a = math.radians(-deg)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        return (f'<path d="M{cx} {cy}L{cx + r} {cy}A{r} {r} 0 0 0 {f(x)} {f(y)}Z" '
                f'fill="{c["accent"]}" opacity="{op}"/>')

    out.append('<g>' + wedge(70, ".07") + wedge(35, ".10") + wedge(12, ".14")
               + f'<path d="M{cx} {cy}H{cx + r}" stroke="{c["accent"]}" stroke-width="1.5"/>'
               + f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" '
                 f'to="360 {cx} {cy}" dur="{SWEEP}s" repeatCount="indefinite"/></g>')

    # Blips light up as the sweep passes, then fade. (angle°, radius fraction)
    fade = 0.45
    for ang, frac in [(38, .55), (118, .82), (160, .38), (232, .66), (305, .46), (338, .86)]:
        a = math.radians(ang)
        x, y = cx + r * frac * math.cos(a), cy + r * frac * math.sin(a)
        t0 = ang / 360
        level = lambda t: max(0.0, 1 - (((t - t0) % 1) / fade))
        keys = sorted({0.0, max(t0 - 0.001, 0.0), t0, (t0 + fade) % 1, 1.0})
        vals = [0.0 if abs(k - (t0 - 0.001)) < 1e-9 else (1.0 if k == t0 else level(k)) for k in keys]
        if keys[-1] == 1.0:
            vals[-1] = vals[0]
        out.append(
            f'<circle cx="{f(x)}" cy="{f(y)}" r="3.5" fill="{c["accent"]}" opacity="0">'
            f'<animate attributeName="opacity" dur="{SWEEP}s" repeatCount="indefinite" '
            f'keyTimes="{";".join(f(k) for k in keys)}" values="{";".join(f(v) for v in vals)}"/></circle>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="{c["accent"]}"/>')
    return "".join(out)


def banner(c):
    W, H = 1180, 500
    px, py, pw, ph = 35, 88, 380, 374          # left panel
    tx, tw = 435, 710                          # right panel
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'role="img" aria-labelledby="t d" font-family="{MONO}">'
         '<title id="t">janyris: SOC console</title>'
         '<desc id="d">Animated terminal: IT professional moving into SOC / blue team, '
         'studying for CompTIA Security+ and Splunk Core User, New York.</desc>',
         f'<rect width="{W}" height="{H}" rx="18" fill="{c["bg0"]}"/>',
         f'<rect x="13" y="13" width="{W - 26}" height="{H - 26}" rx="13" fill="{c["bg1"]}" stroke="{c["line"]}"/>',
         f'<path d="M13 62H{W - 13}" stroke="{c["line"]}"/>',
         '<circle cx="38" cy="38" r="6" fill="#FF5F57"/><circle cx="59" cy="38" r="6" fill="#FEBC2E"/>'
         '<circle cx="80" cy="38" r="6" fill="#28C840"/>',
         f'<text x="{W / 2}" y="43" text-anchor="middle" fill="{c["muted"]}" font-size="13" '
         'letter-spacing=".4">soc-console --live</text>']

    # left: radar scope
    s.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="6" fill="{c["panel"]}" stroke="{c["line"]}"/>'
             f'<path d="M{px} {py + 36}H{px + pw}" stroke="{c["line"]}"/>'
             f'<text x="{px + 14}" y="{py + 23}" fill="{c["accent"]}" font-size="13" font-weight="700" '
             'letter-spacing="1.2">SCOPE.SWEEP</text>'
             f'<circle cx="{px + pw - 58}" cy="{py + 19}" r="3.5" fill="{c["accent"]}">'
             '<animate attributeName="opacity" dur="1.6s" repeatCount="indefinite" values="1;.25;1"/></circle>'
             f'<text x="{px + pw - 14}" y="{py + 23}" text-anchor="end" fill="{c["muted"]}" font-size="11">LIVE</text>')
    x0, y0, x1, y1 = px + 14, py + 50, px + pw - 14, py + ph - 14
    s.append(f'<path d="M{x0} {y0}h12M{x0} {y0}v12M{x1} {y0}h-12M{x1} {y0}v12M{x0} {y1}h12M{x0} {y1}v-12'
             f'M{x1} {y1}h-12M{x1} {y1}v-12" fill="none" stroke="{c["accent"]}" opacity=".55"/>')
    s.append(radar(c, px + pw // 2, (y0 + y1) // 2, 136))

    # right: terminal session
    s.append(f'<rect x="{tx}" y="{py}" width="{tw}" height="{ph}" rx="6" fill="{c["panel"]}" stroke="{c["line"]}"/>'
             f'<path d="M{tx} {py + 36}H{tx + tw}" stroke="{c["line"]}"/>'
             f'<text x="{tx + 14}" y="{py + 23}" fill="{c["accent"]}" font-size="13" font-weight="700" '
             'letter-spacing="1.2">SESSION</text>'
             f'<text x="{tx + tw - 14}" y="{py + 23}" text-anchor="end" fill="{c["muted"]}" '
             'font-size="11">janyris@blue-team:~</text>')

    size, lh, lx, ly = 16, 30, tx + 22, py + 72
    cw = size * 0.602                           # monospace advance width
    t, defs = 0.6, []
    for i, (kind, body) in enumerate(LINES):
        y = ly + i * lh
        if kind == "cmd":
            dur = 0.25 + 0.07 * len(body)
            a, b = t / CYCLE, (t + dur) / CYCLE
            width = len(body) * cw + 6
            defs.append(f'<clipPath id="c{i}"><rect x="{lx + 2 * cw}" y="{y - 20}" height="28" width="0">'
                        f'<animate attributeName="width" dur="{CYCLE}s" repeatCount="indefinite" '
                        f'keyTimes="0;{f(a)};{f(b)};1" values="0;0;{f(width)};{f(width)}"/></rect></clipPath>')
            s.append(f'<g opacity="0">{visible(a)}'
                     f'<text x="{lx}" y="{y}" font-size="{size}" fill="{c["accent"]}" font-weight="700">$</text>'
                     f'<text x="{lx + 2 * cw}" y="{y}" font-size="{size}" fill="{c["fg"]}" '
                     f'clip-path="url(#c{i})" xml:space="preserve">{esc(body)}</text></g>')
            t += dur + 0.35
        else:
            spans = "".join(f'<tspan fill="{c[k]}">{esc(txt)}</tspan>' for txt, k in body)
            s.append(f'<text x="{lx}" y="{y}" font-size="{size}" opacity="0" xml:space="preserve">'
                     f'{visible(t / CYCLE)}{spans}</text>')
            nxt = LINES[i + 1][0] if i + 1 < len(LINES) else "cmd"
            t += 0.25 if nxt == "out" else 0.9
    y = ly + len(LINES) * lh
    s.append(f'<g opacity="0">{visible(t / CYCLE)}'
             f'<text x="{lx}" y="{y}" font-size="{size}" fill="{c["accent"]}" font-weight="700">$</text>'
             f'<rect x="{f(lx + 2 * cw)}" y="{y - 14}" width="9" height="17" fill="{c["fg"]}">'
             '<animate attributeName="opacity" dur="1.1s" repeatCount="indefinite" calcMode="discrete" '
             'keyTimes="0;.5;1" values="1;0;0"/></rect></g>')
    s.insert(2, "<defs>" + "".join(defs) + "</defs>")
    s.append("</svg>")
    return "".join(s)


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    for theme, colours in THEMES.items():
        (ASSETS / f"banner-{theme}.svg").write_text(banner(colours))
    print("wrote", *sorted(p.name for p in ASSETS.glob("*.svg")))
