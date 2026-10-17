#!/usr/bin/env python3
"""v0.68: explicit isolated routing baseline: Smart Fit standby v0.63,
normal Smart Scroll v0.51. No experimental fallback/gap sharing patches."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='"SCROLL DEBUG v0.63 | visible gap standby"'
assert s.count(a)==1
p.write_text(s.replace(a,'"SCROLL DEBUG v0.68 | fit standby / super safe scroll"',1))
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 101")==1
p.write_text(s.replace("versionCode = 101","versionCode = 106",1))
print("v0.68: v0.51 normal navigation + v0.63 fit standby, no shared scanner")
