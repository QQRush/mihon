#!/usr/bin/env python3
"""v0.72: restore full-screen normal fallback; leave post-PASSED safety intact."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
a='''                // No verified next start: do not blindly cross unseen ink.
                (recycler.height * 3 / 4).coerceAtLeast(1)'''
b='''                // Normal fallback: one full viewport, no artificial 25% overlap.
                recycler.height.coerceAtLeast(1)'''
assert s.count(a)==1, "Expected v0.69 normal 75-percent fallback missing"
p.write_text(s.replace(a,b,1))
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='"SCROLL DEBUG v0.71 | current gap end lookahead"'
assert s.count(a)==1
p.write_text(s.replace(a,'"SCROLL DEBUG v0.72 | full viewport fallback"',1))
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 109")==1
p.write_text(s.replace("versionCode = 109","versionCode = 110",1))
print("v0.72: normal fallback 100%; post-PASSED fallback unchanged")
