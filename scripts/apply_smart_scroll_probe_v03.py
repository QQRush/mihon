#!/usr/bin/env python3
"""Apply v0.3 visible-viewport separator diagnostics after v0.2."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
old="debugOverlay.update(first, offset, recycler.computeVerticalScrollOffset(), scrollDistance)"
new="debugOverlay.update(first, offset, recycler.computeVerticalScrollOffset(), scrollDistance, recycler)"
if new not in s:
    if s.count(old)!=1: raise SystemExit("v0.2 debug call not found")
    p.write_text(s.replace(old,new))
print("v0.3 diagnostic hook applied")
