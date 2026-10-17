#!/usr/bin/env python3
"""v0.61 deep diagnostics only: snapshot fit decision and both scroll phases."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
a='    private var navigationTrace = "NAV: WAIT"'
assert s.count(a)==1
s=s.replace(a,a+'''
    private var fitDecisionTrace = "FITSCAN: WAIT"
    private var movementTrace = "MOVE: WAIT"
    fun recordFitDecision(trace: String) {
        fitDecisionTrace = "FITSCAN: " + trace
        invalidate()
    }
    fun recordMovement(trace: String) {
        movementTrace = "MOVE: " + trace
        invalidate()
    }
''',1)
a='            navigationTrace,'
assert s.count(a)==1
s=s.replace(a,a+'\n            movementTrace,\n            fitDecisionTrace,',1)
# Probe currently starts at bottom minus 10px; record whether a long
# blank run already crosses the bottom and thus its start is missed.
a='''            var y = ((h - 10).coerceAtLeast(0).toLong() * sh / end).toInt()
            var found = -1'''
assert s.count(a)==1
s=s.replace(a,'''            val boundaryRow = (h.toLong() * sh / end).toInt().coerceIn(0, sh - 1)
            var boundaryBlankStart = boundaryRow
            while (boundaryBlankStart > 0 && blank[boundaryBlankStart - 1]) boundaryBlankStart--
            var boundaryBlankEnd = boundaryRow
            while (boundaryBlankEnd < sh && blank[boundaryBlankEnd]) boundaryBlankEnd++
            val crossing = blank[boundaryRow]
            fitDecisionTrace = "FITSCAN: h=" + h + " probe=" + end +
                " bottomBlank=" + crossing +
                " runStart=" + (if (crossing) boundaryBlankStart * end / sh else -1) +
                " runEnd=" + (if (crossing) boundaryBlankEnd * end / sh else -1) +
                " (diagnostic)"
            var y = ((h - 10).coerceAtLeast(0).toLong() * sh / end).toInt()
            var found = -1''',1)
assert s.count('"SCROLL DEBUG v0.60 | navigation trace"')==1
s=s.replace('"SCROLL DEBUG v0.60 | navigation trace"','"SCROLL DEBUG v0.61 | deep movement trace"',1)
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
# Preserve actual coordinates for each phase, and the known fit art boundary.
a='''    private var fitEnd = -1
    private var fitting = false'''
assert s.count(a)==1
s=s.replace(a,'''    private var fitEnd = -1
    private var fitArtBoundary = -1
    private var fitting = false''',1)
a='''        fitEnd = -1
        fitImage.visibility = View.GONE'''
assert s.count(a)==1
s=s.replace(a,'''        fitEnd = -1
        fitArtBoundary = -1
        fitImage.visibility = View.GONE''',1)
a='''        fitEnd = target
        fitImage.setBackgroundColor'''
assert s.count(a)==1
s=s.replace(a,'''        fitEnd = target
        fitArtBoundary = artEnd
        fitImage.setBackgroundColor''',1)
a='''            val distance = fitEnd
            clearFit()
            fitting = true
            try {
                recycler.scrollBy(0, distance)
                // The fitted artwork ends at the START of a blank gutter.'''
assert s.count(a)==1
s=s.replace(a,'''            val distance = fitEnd
            val fittedArt = fitArtBoundary
            val beforeFitJump = recycler.computeVerticalScrollOffset()
            val beforeFitItem = layoutManager.findFirstVisibleItemPosition()
            clearFit()
            fitting = true
            try {
                recycler.scrollBy(0, distance)
                val afterFitJump = recycler.computeVerticalScrollOffset()
                // The fitted artwork ends at the START of a blank gutter.''',1)
a='''                if (nextContent > 0) recycler.scrollBy(0, nextContent)
                debugOverlay.recordNavigationTrace('''
assert s.count(a)==1
s=s.replace(a,'''                if (nextContent > 0) recycler.scrollBy(0, nextContent)
                val afterAlign = recycler.computeVerticalScrollOffset()
                debugOverlay.recordMovement(
                    "FIT art=" + fittedArt + " end=" + distance +
                        " stage1=" + (afterFitJump - beforeFitJump) +
                        " stage2=" + (afterAlign - afterFitJump) +
                        " fromItem=" + beforeFitItem +
                        " toItem=" + layoutManager.findFirstVisibleItemPosition() +
                        " total=" + (afterAlign - beforeFitJump)
                )
                debugOverlay.recordNavigationTrace(''',1)
a='''            debugOverlay.recordNavigationTrace(
                "NORMAL chosen="'''
assert s.count(a)==1
s=s.replace(a,'''            debugOverlay.recordMovement(
                "NORMAL first=" + beforeItem + " to=" + afterItem +
                    " requested=" + distance +
                    " moved=" + (afterOffset - beforeOffset) +
                    " current=" + (gutter ?: -1) +
                    " extended=" + (extended ?: -1)
            )
            debugOverlay.recordNavigationTrace(
                "NORMAL chosen="''',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 98")==1
p.write_text(s.replace("versionCode = 98","versionCode = 99",1))
print("v0.61 deep movement diagnostics applied")
