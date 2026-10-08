#!/usr/bin/env python3
"""Generate a coverage badge SVG from coverage.json (stdlib only).

Usage: python scripts/make_badge.py backend/coverage.json docs/coverage-badge.svg
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def color_for(pct: float) -> str:
    if pct >= 80:
        return "#4c1"  # bright green
    if pct >= 60:
        return "#dfb317"  # yellow
    return "#e05d44"  # red


def make_svg(pct: float) -> str:
    label = "coverage"
    value = f"{pct:.0f}%"
    label_w, value_w = 76, 52
    total = label_w + value_w
    color = color_for(pct)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <rect rx="3" width="{total}" height="20" fill="#555"/>
  <rect rx="3" x="{label_w}" width="{value_w}" height="20" fill="{color}"/>
  <rect rx="3" width="{total}" height="20" fill="url(#s)"/>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{label_w / 2}" y="14">{label}</text>
    <text x="{label_w + value_w / 2}" y="14">{value}</text>
  </g>
</svg>
"""


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    coverage_path, output_path = Path(sys.argv[1]), Path(sys.argv[2])
    data = json.loads(coverage_path.read_text())
    pct = float(data["totals"]["percent_covered"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(make_svg(pct))
    print(f"badge written: {output_path} ({pct:.1f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
