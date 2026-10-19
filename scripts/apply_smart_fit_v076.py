#!/usr/bin/env python3
"""v0.76: FIT_NEXT-only guard for a tiny remnant of prior art above a long blank gutter.
Never skip a first-content tip: require a thin remnant AND a substantial blank run."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
a='''    fun firstInkAfterFit(recycler: androidx.recyclerview.widget.RecyclerView): Int {'''
assert s.count(a)==1
s=s.replace(a,'''    var lastFitInkTrace = "boundary=NA searchStart=NA firstInk=NA"
        private set

    fun firstInkAfterFit(recycler: androidx.recyclerview.widget.RecyclerView): Int {''',1)
a='''            var firstInk = -1
            for (y in 0 until sh) {
                var ink = false
                for (x in 3 until sw - 3) {
                    if (isInk(pixels[y * sw + x])) { ink = true; break }
                }
                if (ink) { firstInk = y; break }
            }
            if (firstInk <= 4) return 0
            // Land exactly on the first detected ink; no intentional top padding.
            return (firstInk.toLong() * h / sh).toInt().coerceAtLeast(0)'''
b='''            val inkRows = BooleanArray(sh)
            for (y in 0 until sh) {
                for (x in 3 until sw - 3) {
                    if (isInk(pixels[y * sw + x])) {
                        inkRows[y] = true
                        break
                    }
                }
            }
            val firstInk = inkRows.indexOfFirst { it }
            if (firstInk < 0) {
                lastFitInkTrace = "boundary=NA searchStart=0 firstInk=NONE"
                return 0
            }
            // After FIT_NEXT, a 1-30px sliver of the ALREADY FITTED
            // artwork can remain at screen top. Only skip it if a long,
            // uninterrupted empty band separates it from the next content.
            // Do not treat an isolated speech-balloon tip as disposable.
            val remnantLimit = ((32L * sh + h - 1) / h).toInt().coerceAtLeast(1)
            val minBlank = ((64L * sh + h - 1) / h).toInt().coerceAtLeast(2)
            var remnantEnd = firstInk
            while (remnantEnd < sh && inkRows[remnantEnd]) remnantEnd++
            var blankEnd = remnantEnd
            while (blankEnd < sh && !inkRows[blankEnd]) blankEnd++
            val hasThinRemnant = firstInk <= 4 && remnantEnd <= remnantLimit
            val hasLongGap = blankEnd - remnantEnd >= minBlank
            val nextInk = if (blankEnd < sh) blankEnd else -1
            if (hasThinRemnant && hasLongGap && nextInk >= 0) {
                val boundaryPx = (remnantEnd.toLong() * h / sh).toInt()
                val startPx = (blankEnd.toLong() * h / sh).toInt()
                lastFitInkTrace = "boundary=" + boundaryPx +
                    " searchStart=" + boundaryPx + " firstInk=" + startPx + " REMNANT"
                return startPx
            }
            val firstPx = (firstInk.toLong() * h / sh).toInt()
            lastFitInkTrace = "boundary=NA searchStart=0 firstInk=" + firstPx +
                " KEEP_TOP remnant=" + remnantEnd + " gap=" + (blankEnd - remnantEnd)
            if (firstInk <= 4) return 0
            return firstPx.coerceAtLeast(0)'''
assert s.count(a)==1
s=s.replace(a,b,1)
a='"SCROLL DEBUG v0.75 | backward checkpoints"'
assert s.count(a)==1
s=s.replace(a,'"SCROLL DEBUG v0.76 | fit remnant guard"',1)
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
a='''"FIT_NEXT probeEnd=" + distance + " align=" + nextContent +'''
assert s.count(a)==1
s=s.replace(a,'''"FIT_NEXT probeEnd=" + distance + " align=" + nextContent +
                        " " + debugOverlay.lastFitInkTrace +''',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 113")==1
p.write_text(s.replace("versionCode = 113","versionCode = 114",1))
print("v0.76: FIT_NEXT-only guarded remnant skip with boundary/searchStart/firstInk diagnostics")
