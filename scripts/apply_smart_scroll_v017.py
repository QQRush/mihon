#!/usr/bin/env python3
"""v0.17: never overshoot a visible image boundary on a Smart Next tap."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"WebtoonViewer.kt"
s=p.read_text()
old="""            val distance = gutter ?: fallback
            val origin = currentSmartPosition()
"""
new="""            val proposedDistance = gutter ?: fallback
            // A source gutter can fall beyond the end of the current image.
            // If the next image begins within this jump, stop at its exact top
            // instead of entering partway through its first panel or speech bubble.
            val firstVisible = layoutManager.findFirstVisibleItemPosition()
            val nextItemTop = layoutManager.findViewByPosition(firstVisible + 1)?.top
            val distance = if (nextItemTop != null && nextItemTop > 0 && nextItemTop < proposedDistance) {
                nextItemTop
            } else {
                proposedDistance
            }
            val origin = currentSmartPosition()
"""
if s.count(old)!=1:raise SystemExit("v0.16 jump anchor mismatch")
s=s.replace(old,new)
p.write_text(s)
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
if s.count("SCROLL DEBUG v0.16 | gap landing")!=1:raise SystemExit("debug label mismatch")
p.write_text(s.replace("SCROLL DEBUG v0.16 | gap landing","SCROLL DEBUG v0.17 | boundary guard"))
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 49")!=1:raise SystemExit("version mismatch")
p.write_text(s.replace("versionCode = 49","versionCode = 50",1))
print("v0.17 image-boundary guard installed")
