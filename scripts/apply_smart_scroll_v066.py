#!/usr/bin/env python3
"""v0.66: reuse Smart Fit's proven visible-gap row coordinates for NORMAL
navigation. Only accept a gap whose end and following ink were sampled.
Leave PASSED/PRESERVED and fit behavior unchanged."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='''    private var navigationTrace = "NAV: WAIT"'''
assert s.count(a)==1
s=s.replace(a,'''    private var visibleFitGapLanding = -1
    fun fitVisibleGapLanding(): Int? =
        visibleFitGapLanding.takeIf { it > 0 }
    private var navigationTrace = "NAV: WAIT"''',1)
a='''        smartFitMarkerY = -1'''
# Probe resets state at start, not in other paths.
start=s.index('    fun probeSmartFit(')
end=s.index('    fun extendedNotRun(',start)
part=s[start:end]
assert part.count(a)>=1
part=part.replace(a,'''        visibleFitGapLanding = -1
'''+a,1)
a='''                    smartFitDebug = "FIT: STANDBY_CURRENT_GAP @" + gapStartPx'''
assert part.count(a)==1
part=part.replace(a,'''                    // Only navigate to a measured END, never to the gap
                    // start or beyond the sampled image. Require real ink
                    // following it, not a single border/noise row.
                    if (gapEndRow < sh - 10) {
                        var inkRows = 0
                        for (cy in gapEndRow until gapEndRow + 10) {
                            if (!blank[cy]) inkRows++
                        }
                        if (inkRows >= 5) {
                            visibleFitGapLanding =
                                (gapEndRow * end / sh - 8).coerceAtLeast(1)
                        }
                    }
                    smartFitDebug = "FIT: STANDBY_CURRENT_GAP @" + gapStartPx''',1)
s=s[:start]+part+s[end:]
a='"SCROLL DEBUG v0.65 | gap-end landing"'
assert s.count(a)==1
s=s.replace(a,'"SCROLL DEBUG v0.66 | shared fit gap"',1)
p.write_text(s)
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
a='''            val gapEnd = if (gutter == null && extended == null && !afterIsolated) {
                debugOverlay.nextContentAfterVisibleGap(recycler)
            } else null'''
assert s.count(a)==1
s=s.replace(a,'''            // Fit already sampled the composed strip and found a visible
            // full-width gutter. Prefer its measured first-content row.
            val sharedGapEnd = if (gutter == null && extended == null && !afterIsolated) {
                debugOverlay.fitVisibleGapLanding()
            } else null
            val gapEnd = if (sharedGapEnd == null && gutter == null &&
                extended == null && !afterIsolated) {
                debugOverlay.nextContentAfterVisibleGap(recycler)
            } else sharedGapEnd''',1)
a='''else if (gapEnd != null) "GAP_END@" + gapEnd'''
assert s.count(a)==1
s=s.replace(a,'''else if (gapEnd != null) (if (sharedGapEnd != null) "FIT_SHARED_GAP@" else "GAP_END@") + gapEnd''',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 103")==1
p.write_text(s.replace("versionCode = 103","versionCode = 104",1))
print("v0.66 shared measured Smart Fit visible gutter landing")
