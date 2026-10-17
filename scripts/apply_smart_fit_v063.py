#!/usr/bin/env python3
"""v0.63: Smart Fit standby when a valid full-width gutter starts on screen.
Use the existing 96-column white/black blank-row classification, no new
image detector. Leave Smart Scroll navigation and coordinate recheck alone."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
anchor='''            val boundaryRow = (h.toLong() * sh / end).toInt().coerceIn(0, sh - 1)'''
assert s.count(anchor)==1
guard='''            // An existing visible interruption wins over lookahead Smart Fit.
            // Reuse the exact blank[] rows already used by the fit detector.
            // Ignore a header gutter in the first quarter of the viewport.
            val minVisibleGap = ((35L * sh + end - 1) / end).toInt().coerceAtLeast(2)
            val screenEndRow = (h.toLong() * sh / end).toInt().coerceIn(0, sh - 1)
            var currentRow = (h.toLong() * sh / (4L * end)).toInt()
            while (currentRow < screenEndRow) {
                if (!blank[currentRow]) { currentRow++; continue }
                val gapStartRow = currentRow
                while (currentRow < sh && blank[currentRow]) currentRow++
                val gapEndRow = currentRow
                if (gapEndRow - gapStartRow >= minVisibleGap) {
                    val gapStartPx = gapStartRow * end / sh
                    smartFitTarget = -1
                    smartFitArtEnd = -1
                    smartFitMarkerEligible = false
                    smartFitDebug = "FIT: STANDBY_CURRENT_GAP @" + gapStartPx
                    fitDecisionTrace = "FITSCAN: CURRENT_GAP @" + gapStartPx +
                        " end=" + (gapEndRow * end / sh) + " h=" + h
                    invalidate()
                    return
                }
            }
'''
s=s.replace(anchor,guard+anchor,1)
assert s.count('"SCROLL DEBUG v0.62 | coordinate recheck"')==1
s=s.replace('"SCROLL DEBUG v0.62 | coordinate recheck"','"SCROLL DEBUG v0.63 | visible gap standby"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 100")==1
p.write_text(s.replace("versionCode = 100","versionCode = 101",1))
print("v0.63 Smart Fit standby on visible full-width gap")
