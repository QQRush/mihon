#!/usr/bin/env python3
"""v0.35: constant 3px gutter landing margin; no additional sampling."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"WebtoonViewer.kt"
s=p.read_text()
old="val distance = gutter ?: extended ?: recycler.height.coerceAtLeast(1)"
assert s.count(old)==1
s=s.replace(old,"val distance = gutter?.plus(3) ?: extended ?: recycler.height.coerceAtLeast(1)",1)
p.write_text(s)
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
assert s.count('"SCROLL DEBUG v0.34 | ceil landing"')==1
s=s.replace('"SCROLL DEBUG v0.34 | ceil landing"','"SCROLL DEBUG v0.35 | gutter +3px"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 72")==1
p.write_text(s.replace("versionCode = 72","versionCode = 73",1))
print("v0.35: gutter +3px, no refine or extra bitmap work")
