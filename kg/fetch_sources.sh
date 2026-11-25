#!/usr/bin/env bash
# Download the demo corpus from ti.com and split it into per-page text (needs poppler-utils).
set -euo pipefail
cd "$(dirname "$0")/../sources"
for d in spruj26a spruio7 sprt755 sszt350 sszt464 sszt496; do
  [ -f "$d.pdf" ] || curl -sSL -A "Mozilla/5.0" -o "$d.pdf" "https://www.ti.com/lit/pdf/$d"
  pdftotext -layout "$d.pdf" "$d.txt"
  python3 - "$d" <<'PY'
import os, sys
d = sys.argv[1]
os.makedirs(f"pages/{d}", exist_ok=True)
for i, p in enumerate(open(f"{d}.txt").read().split("\f"), 1):
    if p.strip():
        open(f"pages/{d}/p{i:03d}.txt", "w").write(p)
PY
  echo "$d ok"
done
