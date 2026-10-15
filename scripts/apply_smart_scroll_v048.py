#!/usr/bin/env python3
"""v0.48: after PASSED prefer the first visible valid gutter over a later extended gap.
Retain all v0.47 visual debug and existing classification."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
a='''val distance = gutter ?: extended ?: if (afterIsolated) {'''
assert s.count(a)==1
# A current-viewport valid gutter wins; extended is a fallback only.
# The existing expression already does this, so preserve it.
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
# The post-PASSED scan must not require a gutter to straddle the viewport edge.
# Keep the first candidate after resume; do not filter out a gutter just
# because it begins before resume, provided its end is beyond the passed band.
a='''                if (afterIsolated && landing <= isolatedResumeY) continue'''
assert s.count(a)==1
s=s.replace(a,'''                if (afterIsolated && landing <= isolatedResumeY) continue''',1)
# Remove the minimum-width filter for post-PASSED candidates: the next
# separator can be narrow, while ordinary scanning keeps its original limit.
a='''                if ((stop - start) * span / sh < 50) {'''
assert s.count(a)==1
s=s.replace(a,'''                if (!afterIsolated && (stop - start) * span / sh < 50) {''',1)
assert s.count('"SCROLL DEBUG v0.47 | first gap after pass"')==1
s=s.replace('"SCROLL DEBUG v0.47 | first gap after pass"','"SCROLL DEBUG v0.48 | earliest post-pass gap"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 85")==1
p.write_text(s.replace("versionCode = 85","versionCode = 86",1))
print("v0.48: accept earliest narrow post-PASSED gap, preserve visual debug")
