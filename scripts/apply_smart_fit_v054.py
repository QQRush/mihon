#!/usr/bin/env python3
"""v0.54: current viewport starts at zero; find only the first valid separator
just beyond its bottom, within 1..30% tolerance. Diagnostic only."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
start=s.index("    fun probeSmartFit(recycler:")
end=s.index("\n    fun extendedNotRun(",start)
part=s[start:end]
a='''        // Do not start a fit scan when the currently visible image already ends.
        val current = children.firstOrNull { it.top <= 0 && it.bottom > 0 }
        if (current == null || current.bottom <= h) {
            smartFitDebug = "FIT: CURRENT_IMAGE_ENDS_IN_VIEW"
            invalidate()
            return
        }
'''
assert part.count(a)==1
part=part.replace(a,'''        // A JPG boundary is not a vignette boundary. The viewport starts at 0.
        // Continue only if there is rendered content beyond the screen edge.
        if (children.none { it.bottom > h }) {
            smartFitDebug = "FIT: NO_CONTENT_BEYOND_VIEW"
            invalidate()
            return
        }
''',1)
a='''            // The start of the current block is only known if we can see it.
            // A viewport beginning inside a panel is not safe for fit sizing.
            var firstInk = 0
            while (firstInk < sh && blank[firstInk]) firstInk++
            val startPx = firstInk * end / sh
            if (firstInk == 0 || firstInk >= sh || startPx > h / 3) {
                smartFitDebug = "FIT: START_BOUNDARY_UNKNOWN"
                invalidate()
                return
            }
'''
assert part.count(a)==1
part=part.replace(a,'''            // The top of the CURRENT viewport is always our fit start.
            val startPx = 0
''',1)
a='''            var y = firstInk'''
assert part.count(a)==1
part=part.replace(a,'''            var y = ((h - 10).coerceAtLeast(0).toLong() * sh / end).toInt()''',1)
a='''                if (gapEnd - gapStart < minGap || finish <= h ||
                    finish > end || gapEnd >= sh - 2) continue'''
assert part.count(a)==1
part=part.replace(a,'''                // Separator can start just before the bottom, but its end
                // must be within the user-defined lookahead.
                val gapFinish = gapEnd * end / sh
                if (gapEnd - gapStart < minGap || finish < h - 10 ||
                    gapFinish <= h || gapFinish > end || gapEnd >= sh - 2) continue''',1)
a='''                found = finish'''
assert part.count(a)==1
part=part.replace(a,'''                found = gapFinish''',1)
a='''                val scale = (h.toLong() * 100 / block).toInt()'''
assert part.count(a)==1
part=part.replace(a,'''                val scale = (h.toLong() * 1000 / block).toDouble() / 10.0''',1)
a='''                smartFitMarkerEligible = block > h && block <= end'''
assert part.count(a)==1
part=part.replace(a,'''                smartFitMarkerEligible = block > h && block <= end''',1)
s=s[:start]+part+s[end:]
assert s.count('"SCROLL DEBUG v0.53 | separator fit probe"')==1
s=s.replace('"SCROLL DEBUG v0.53 | separator fit probe"','"SCROLL DEBUG v0.54 | viewport-zero fit probe"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 91")==1
p.write_text(s.replace("versionCode = 91","versionCode = 92",1))
print("v0.54 viewport-zero Smart Fit diagnostic applied")
