#!/usr/bin/env python3
"""v0.46: avoid accepting weak-content closing strokes as gutters.
Retains all v0.45 visual markers and diagnostics."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='''                    val closingLine = nearbyInkRows >= 7'''
assert s.count(a)==1
s=s.replace(a,'''                    // A box bottom can have only a few sampled ink rows
                    // above its horizontal stroke. Treat those as a closing
                    // border too; zero nearby ink remains a possible opening.
                    val closingLine = nearbyInkRows >= 2''',1)
assert s.count('"SCROLL DEBUG v0.45 | after pass next gap"')==1
s=s.replace('"SCROLL DEBUG v0.45 | after pass next gap"','"SCROLL DEBUG v0.46 | border-band recovery"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 83")==1
p.write_text(s.replace("versionCode = 83","versionCode = 84",1))
print("v0.46 closing-border guard; v0.45 debug retained")
