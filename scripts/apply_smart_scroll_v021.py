#!/usr/bin/env python3
"""v0.21: one continuous viewport-based webtoon navigation path.

RecyclerView already lays consecutive images into one continuous vertical view.
Sample that composed viewport once; never reinterpret a landing at JPG boundaries.
"""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"WebtoonViewer.kt"
s=p.read_text()
start=s.index("            val proposed = gutter ?: fallback")
end=s.index("            val origin = currentSmartPosition()",start)
s=s[:start]+"""            // Treat all loaded webtoon images as one continuous vertical strip.
            // The viewport detector works on RecyclerView's composed image;
            // image-item boundaries never change the destination.
            val distance = gutter ?: fallback
"""+s[end:]
s=s.replace('if (boundaryTarget != null) "OFFSET_GAP" else if (gutter != null) "GUTTER" else "FULL"', 'if (gutter != null) "GUTTER" else "FULL"')
if "boundaryTarget" in s or "nextContent = debugOverlay.contentAfterOffset" in s:
    raise SystemExit("Residual per-image boundary navigation")
p.write_text(s)
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
start=s.index("    // Only search for the first content AFTER a blank gutter")
end=s.index("    override fun onDraw(canvas: Canvas) {",start)
s=s[:start]+s[end:]
s=s.replace("SCROLL DEBUG v0.20D2 | scan reasons","SCROLL DEBUG v0.21 | continuous strip")
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 58")!=1:raise SystemExit("version mismatch")
p.write_text(s.replace("versionCode = 58","versionCode = 59",1))
print("v0.21: single viewport detector, no JPG boundary correction, no Top Trim")
