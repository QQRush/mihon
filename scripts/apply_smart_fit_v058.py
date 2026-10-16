#!/usr/bin/env python3
"""v0.58: Fit by the START of a confirmed blank separator, even when
the blank region continues beyond lookahead. Keep original scrolling logic."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='''                if (gapEnd - gapStart < minGap || finish < h - 10 ||
                    gapFinish <= h || gapFinish > end || gapEnd >= sh - 2) continue
                if (!(gapEnd until minOf(sh, gapEnd + 6)).any { !blank[it] }) continue
                found = gapFinish
                artEnd = finish'''
b='''                // Fit only cares where the drawing ENDS, not where the
                // blank gutter ends. Require a confirmed 35px blank run.
                if (gapEnd - gapStart < minGap || finish <= h ||
                    finish > end) continue
                // If the gap runs past the probe edge, resume at the last
                // confirmed blank pixel, never at unknown future content.
                found = gapFinish.coerceAtMost(end)
                artEnd = finish'''
assert s.count(a)==1, "separator anchor changed"
s=s.replace(a,b,1)
a='''                smartFitMarkerEligible = block > h && block <= end
                if (smartFitMarkerEligible && artEnd > h) {'''
b='''                smartFitMarkerEligible = artEnd > h && artEnd <= end
                if (smartFitMarkerEligible) {'''
assert s.count(a)==1
s=s.replace(a,b,1)
a='''                smartFitDebug = "FIT: FOUND start=" + startPx + " end=" + found +
                    " block=" + block + " over=" + over + "% scale=" + scale + "%"'''
b='''                smartFitDebug = "FIT: FOUND artEnd=" + artEnd + " gapProbeEnd=" + found +
                    " extra=" + (artEnd - h) + "px scale=" +
                    (h.toLong() * 1000 / (artEnd + 3)).toDouble() / 10.0 + "%"'''
assert s.count(a)==1
s=s.replace(a,b,1)
a='''                smartFitMarkerText = "FIT FOUND +" + (found - h) +
                    "px BELOW | BLOCK " + block + "px | SCALE " + scale + "%"'''
b='''                smartFitMarkerText = "FIT ART +" + (artEnd - h) +
                    "px | SCALE " + (h.toLong() * 1000 / (artEnd + 3)).toDouble() / 10.0 + "%"'''
assert s.count(a)==1
s=s.replace(a,b,1)
assert s.count('"SCROLL DEBUG v0.56 | proportional art fit"')==1
s=s.replace('"SCROLL DEBUG v0.56 | proportional art fit"','"SCROLL DEBUG v0.58 | gap-start fit"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 95")==1
p.write_text(s.replace("versionCode = 95","versionCode = 96",1))
print("v0.58: fit based on separator start, including long white gutters")
