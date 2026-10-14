#!/usr/bin/env python3
"""v0.26: current scan 45%, unchanged 35% lookahead, conservative first-gap landing."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
# The on-screen detector starts at 55% instead of 65%.
a="val firstRow = sh * 65 / 100"
assert s.count(a)==1
s=s.replace(a,"val firstRow = sh * 55 / 100")
# Keep the first safe gap rather than the last: a later gap can occur inside
# the next speech balloon, resulting in skipping its first lines.
a="if (landing > 0 && (result == null || landing > result)) result = landing"
assert s.count(a)==1
s=s.replace(a,"if (landing > 0 && result == null) result = landing")
# Extend the existing lookahead sampling backward to the same 55% boundary.
# The 35% AFTER the screen is intentionally unchanged.
a="val from = h * 65 / 100"
assert s.count(a)==1
s=s.replace(a,"val from = h * 55 / 100")
s=s.replace("    // Search the last 35% of this screen and at most 35% beyond its edge.",
            "    // Search the last 45% of this screen and at most 35% beyond its edge.")
a='"SCROLL DEBUG v0.25 | extended diagnostics"'
assert s.count(a)==1
s=s.replace(a,'"SCROLL DEBUG v0.26 | first safe gutter"')
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text();assert s.count("versionCode = 63")==1
p.write_text(s.replace("versionCode = 63","versionCode = 64",1))
print("v0.26: current 45%, lookahead 35%, prefer first safe separator")
