#!/usr/bin/env python3
"""v0.17 revised: restore v0.16 movement and keep Top Trim removed.
No speculative next-item clipping, no boundary image sampling.
"""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"WebtoonViewer.kt"
s=p.read_text()
start=s.index("            val proposedDistance = gutter ?: fallback")
end=s.index("            val origin = currentSmartPosition()",start)
s=s[:start]+"""            // v0.16: one coordinate system, one target, one forward jump.
            // Do not reinterpret gutters using RecyclerView item boundaries.
            val distance = gutter ?: fallback
"""+s[end:]
p.write_text(s)
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
start=s.index("    // Only inspect visible pixels below the next image boundary.")
end=s.index("    override fun onDraw(canvas: Canvas) {",start)
s=s[:start]+s[end:]
s=s.replace("SCROLL DEBUG v0.18 | clean boundary","SCROLL DEBUG v0.17r | v0.16 navigation")
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 51")!=1:raise SystemExit("versionCode mismatch")
p.write_text(s.replace("versionCode = 51","versionCode = 52",1))
print("Revised v0.17: v0.16 navigation restored, Top Trim remains removed")
