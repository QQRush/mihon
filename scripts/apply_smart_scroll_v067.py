#!/usr/bin/env python3
"""v0.67: preserve thin opening stroke beyond viewport using Smart Fit's
composed-strip rows. No additional bitmap and no modification to v0.51."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='''                    if (gapEndRow < sh - 10) {
                        var inkRows = 0
                        for (cy in gapEndRow until gapEndRow + 10) {
                            if (!blank[cy]) inkRows++
                        }
                        if (inkRows >= 5) {
                            visibleFitGapLanding =
                                (gapEndRow * end / sh - 8).coerceAtLeast(1)
                        }
                    }'''
b='''                    if (gapEndRow < sh - 3) {
                        // A thin PRESERVED opening line can be only 1-2 rows,
                        // followed by a white balloon interior. The v0.66
                        // five-ink-rows rule incorrectly discarded it.
                        val strokeRows = ((12L * sh + end - 1) / end).toInt().coerceAtLeast(1)
                        var strokeEnd = gapEndRow
                        while (strokeEnd < sh && !blank[strokeEnd] &&
                            strokeEnd - gapEndRow <= strokeRows) strokeEnd++
                        val thinPreserved = strokeEnd > gapEndRow &&
                            strokeEnd - gapEndRow <= strokeRows &&
                            strokeEnd < sh && blank[strokeEnd]
                        var inkRows = 0
                        for (cy in gapEndRow until minOf(sh, gapEndRow + 10)) {
                            if (!blank[cy]) inkRows++
                        }
                        if (thinPreserved || inkRows >= 5) {
                            visibleFitGapLanding =
                                (gapEndRow * end / sh - 8).coerceAtLeast(1)
                        }
                    }'''
assert s.count(a)==1
s=s.replace(a,b,1)
a='"SCROLL DEBUG v0.66 | shared fit gap"'
assert s.count(a)==1
s=s.replace(a,'"SCROLL DEBUG v0.67 | preserved lookahead"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 104")==1
p.write_text(s.replace("versionCode = 104","versionCode = 105",1))
print("v0.67 preserved thin opening stroke in composed lookahead")
