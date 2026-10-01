#!/usr/bin/env python3
"""Generate the profile README banner (dark + light) into assets/.

    python3 scripts/build.py

The banner is a SIEM-style search: a query types itself, a timeline fills in,
and the profile comes back as result events. Edit QUERY / EVENTS below and
re-run. No dependencies. The SVGs use only SMIL animation and system
monospace fonts, so they render inside GitHub's <img> sandbox (no scripts,
no web fonts).
"""
import math
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

THEMES = {
    "dark": dict(surface="#15171A", field="#0E1012", line="#2B2F35", fg="#E6E7E9",
                 muted="#8B919A", accent="#F59E42", on_accent="#15171A"),
    "light": dict(surface="#FFFFFF", field="#F6F5F2", line="#DDDAD3", fg="#1C1D1F",
                  muted="#6A6F77", accent="#B4530A", on_accent="#FFFFFF"),
}

# The search that gets typed: (text, colour-key) segments.
QUERY = [("index=profile user=janyris ", "fg"), ("| fields", "accent"), (" role, focus, cert, location", "fg")]

# Result rows: (source, [(field, value, colour-key for the value), ...])
EVENTS = [
    ("whoami", [("role", '"IT professional"', "fg"), ("moving_to", '"SOC / blue team"', "fg")]),
    ("focus", [("area", '"cybersecurity"', "fg"), ("area", '"security operations"', "fg"), ("area", '"AI"', "fg")]),
    ("certs", [("name", '"CompTIA Security+"', "fg"), ("status", "in_progress", "accent"), ("eta", "2026-10", "fg")]),
    ("certs", [("name", '"Splunk Core User"', "fg"), ("status", "in_progress", "accent"), ("eta", "2026-10", "fg")]),
    ("geo", [("city", '"New York"', "fg"), ("state", "NY", "fg")]),
]

CYCLE = 16.0       # seconds for one full loop
HOLD = 0.965       # fraction of the loop after which everything clears


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def f(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")


def visible(start):
    """Opacity animation: hidden until `start` seconds, shown until the loop clears."""
    return (f'<animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="0;{f(start / CYCLE)};{HOLD};1" values="0;1;0;0"/>')


def grow(attr, start, end, lo, hi):
    """Animate `attr` from lo to hi between start and end seconds, then hold."""
    return (f'<animate attributeName="{attr}" dur="{CYCLE}s" repeatCount="indefinite" '
            f'keyTimes="0;{f(start / CYCLE)};{f(end / CYCLE)};{HOLD};1" '
            f'values="{f(lo)};{f(lo)};{f(hi)};{f(hi)};{f(lo)}"/>')


def banner(c):
    W, H, pad = 1180, 462, 24
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'role="img" aria-labelledby="t d" font-family="{MONO}">'
         '<title id="t">Search: index=profile user=janyris</title>'
         '<desc id="d">A SIEM-style search returning five events: IT professional moving to SOC / blue team; '
         'focus on cybersecurity, security operations and AI; CompTIA Security+ and Splunk Core User '
         'in progress, October 2026; New York, NY.</desc>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{c["surface"]}" stroke="{c["line"]}"/>']

    # search bar, time range, run button
    bar_x, bar_y, bar_h = pad, 24, 44
    btn_w, pill_w, gap = 52, 120, 12
    bar_w = W - 2 * pad - btn_w - pill_w - 2 * gap
    pill_x = bar_x + bar_w + gap
    btn_x = pill_x + pill_w + gap
    size = 16
    cw = size * 0.602                           # monospace advance width
    qx, qy = bar_x + 16, bar_y + 28
    qlen = sum(len(t) for t, _ in QUERY)
    t_type0, t_type1 = 0.5, 0.5 + 0.05 * qlen
    qw = qlen * cw + 4
    spans = "".join(f'<tspan fill="{c[k]}">{esc(t)}</tspan>' for t, k in QUERY)
    s.append(f'<defs><clipPath id="q"><rect x="{qx}" y="{bar_y}" height="{bar_h}" width="0">'
             f'{grow("width", t_type0, t_type1, 0, qw)}</rect></clipPath>'
             f'<clipPath id="h"><rect x="{pad}" y="100" height="90" width="0">'
             f'{grow("width", t_type1 + 0.3, t_type1 + 1.2, 0, W - 2 * pad)}</rect></clipPath></defs>')
    s.append(f'<rect x="{bar_x}.5" y="{bar_y}.5" width="{bar_w}" height="{bar_h}" rx="6" '
             f'fill="{c["field"]}" stroke="{c["line"]}"/>'
             f'<text x="{qx}" y="{qy}" font-size="{size}" clip-path="url(#q)" xml:space="preserve">{spans}</text>'
             f'<rect x="{qx}" y="{bar_y + 13}" width="2" height="19" fill="{c["accent"]}">'
             f'{grow("x", t_type0, t_type1, qx, qx + qw)}'
             '<animate attributeName="opacity" dur="1.1s" repeatCount="indefinite" calcMode="discrete" '
             'keyTimes="0;.5;1" values="1;0;0"/></rect>')
    s.append(f'<rect x="{pill_x}.5" y="{bar_y}.5" width="{pill_w}" height="{bar_h}" rx="6" '
             f'fill="{c["field"]}" stroke="{c["line"]}"/>'
             f'<text x="{pill_x + pill_w / 2}" y="{qy - 1}" text-anchor="middle" font-size="13" '
             f'fill="{c["muted"]}">All time</text>')
    mx, my = btn_x + btn_w / 2 - 2, bar_y + bar_h / 2 - 2
    s.append(f'<rect x="{btn_x}" y="{bar_y}" width="{btn_w}" height="{bar_h + 1}" rx="6" fill="{c["accent"]}"/>'
             f'<g fill="none" stroke="{c["on_accent"]}" stroke-width="2.2" stroke-linecap="round">'
             f'<circle cx="{mx}" cy="{my}" r="6.5"/><path d="M{mx + 5} {my + 5}l5.5 5.5"/></g>')

    # timeline histogram, wiped in left to right once the search "runs"
    t_hist = t_type1 + 1.2
    base, n = 180, 60
    step = (W - 2 * pad) / n
    hits = {7, 21, 33, 34, 52}                  # one accent bar per event
    bars = []
    for i in range(n):
        h = 10 + 42 * abs(math.sin(i * 1.7) * math.cos(i * 0.45 + 1))
        h = h + 14 if i in hits else h
        col, op = (c["accent"], "1") if i in hits else (c["muted"], ".32")
        bars.append(f'<rect x="{f(pad + i * step)}" y="{f(base - h)}" width="{f(step - 5)}" height="{f(h)}" '
                    f'rx="1.5" fill="{col}" opacity="{op}"/>')
    s.append(f'<g clip-path="url(#h)">{"".join(bars)}</g>'
             f'<path d="M{pad} {base + .5}H{W - pad}" stroke="{c["line"]}"/>')
    s.append(f'<text x="{pad}" y="96" font-size="12" opacity="0" fill="{c["muted"]}" xml:space="preserve">'
             f'{visible(t_hist)}<tspan fill="{c["accent"]}" font-weight="700">{len(EVENTS)} events</tspan>'
             '  ·  all time  ·  search complete</text>')

    # results table
    head_y, row_h = 208, 44
    col_n, col_src, col_ev = pad + 8, pad + 52, pad + 180
    s.append(f'<g font-size="11" letter-spacing="1.3" fill="{c["muted"]}">'
             f'<text x="{col_n}" y="{head_y}">#</text><text x="{col_src}" y="{head_y}">SOURCE</text>'
             f'<text x="{col_ev}" y="{head_y}">EVENT</text></g>'
             f'<path d="M{pad} {head_y + 10.5}H{W - pad}" stroke="{c["line"]}"/>')
    for i, (source, fields) in enumerate(EVENTS):
        y = head_y + 10 + i * row_h
        ev = "  ".join(f'<tspan fill="{c["muted"]}">{esc(k)}=</tspan><tspan fill="{c[col]}">{esc(v)}</tspan>'
                       for k, v, col in fields)
        rule = (f'<path d="M{pad} {y + row_h + .5}H{W - pad}" stroke="{c["line"]}" opacity=".6"/>'
                if i < len(EVENTS) - 1 else "")
        s.append(f'<g opacity="0" font-size="15">{visible(t_hist + 0.3 + i * 0.35)}'
                 f'<text x="{col_n}" y="{y + 28}" fill="{c["muted"]}">{i + 1}</text>'
                 f'<text x="{col_src}" y="{y + 28}" fill="{c["muted"]}">{esc(source)}</text>'
                 f'<text x="{col_ev}" y="{y + 28}" xml:space="preserve">{ev}</text>{rule}</g>')
    s.append("</svg>")
    return "".join(s)


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    for theme, colours in THEMES.items():
        (ASSETS / f"banner-{theme}.svg").write_text(banner(colours))
    print("wrote", *sorted(p.name for p in ASSETS.glob("*.svg")))
