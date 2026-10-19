#!/usr/bin/env python3
"""v0.77 diagnostic only: FIT_NEXT source boundary and actual landing geometry.
No scrolling or detector behavior changes."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"WebtoonViewer.kt"
s=p.read_text()
a='''" " + debugOverlay.lastFitInkTrace +'''
b='''" " + debugOverlay.lastFitInkTrace +
                        " fitBoundary=" + fittedArt +
                        " sourceAnchor=" + savedAnchor +
                        " anchorDelta=" + anchorDelta +
                        " requested=" + distance +
                        " actualStage1=" + (afterFitJump - beforeFitJump) +
                        " actualStage2=" + (recycler.computeVerticalScrollOffset() - afterFitJump) +
                        " itemAfter=" + layoutManager.findFirstVisibleItemPosition() +
                        " itemTop=" + (layoutManager.findViewByPosition(layoutManager.findFirstVisibleItemPosition())?.top ?: -9999) +'''
assert s.count(a)==1, "v0.76 navigation trace anchor missing"
s=s.replace(a,b,1)
p.write_text(s)
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
a='"SCROLL DEBUG v0.76 | fit remnant guard"'
assert s.count(a)==1
p.write_text(s.replace(a,'"SCROLL DEBUG v0.77 | boundary diagnostics"',1))
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 114")==1
p.write_text(s.replace("versionCode = 114","versionCode = 115",1))
print("v0.77: FIT_NEXT geometry diagnostics only")
