#!/usr/bin/env python3
"""v0.62: anchor Smart Fit to RecyclerView item geometry and recheck before Next.
Keep the established 'first content after fit' logic intact."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
a='''    private var fitArtBoundary = -1
    private var fitting = false'''
b='''    private var fitArtBoundary = -1
    private var fitAnchorItem = -1
    private var fitAnchorTop = 0
    private var fitting = false'''
assert s.count(a)==1
s=s.replace(a,b,1)
a='''        fitArtBoundary = -1
        fitImage.visibility = View.GONE'''
b='''        fitArtBoundary = -1
        fitAnchorItem = -1
        fitImage.visibility = View.GONE'''
assert s.count(a)==1
s=s.replace(a,b,1)
a='''        fitEnd = target
        fitArtBoundary = artEnd
        fitImage.setBackgroundColor'''
b='''        fitEnd = target
        fitArtBoundary = artEnd
        fitAnchorItem = layoutManager.findFirstVisibleItemPosition()
        fitAnchorTop = layoutManager.findViewByPosition(fitAnchorItem)?.top ?: 0
        fitImage.setBackgroundColor'''
assert s.count(a)==1
s=s.replace(a,b,1)
a='''            val distance = fitEnd
            val fittedArt = fitArtBoundary
            val beforeFitJump = recycler.computeVerticalScrollOffset()
            val beforeFitItem = layoutManager.findFirstVisibleItemPosition()
            clearFit()
            fitting = true'''
b='''            val originalTarget = fitEnd
            val fittedArt = fitArtBoundary
            val beforeFitJump = recycler.computeVerticalScrollOffset()
            val beforeFitItem = layoutManager.findFirstVisibleItemPosition()
            val savedAnchor = fitAnchorItem
            val savedTop = fitAnchorTop
            val currentTop = layoutManager.findViewByPosition(savedAnchor)?.top
            // A layout reflow changes the source item's screen top. Translate
            // the original-coordinate target by that delta, not by fit scale.
            val anchorDelta = if (currentTop != null) currentTop - savedTop else 0
            val distance = (originalTarget + anchorDelta).coerceAtLeast(1)
            clearFit()
            fitting = true'''
assert s.count(a)==1
s=s.replace(a,b,1)
a='''                debugOverlay.recordMovement(
                    "FIT art=" + fittedArt + " end=" + distance +'''
b='''                debugOverlay.recordMovement(
                    "FIT art=" + fittedArt + " end=" + distance +
                        " anchor=" + savedAnchor + " top=" + savedTop +
                        " now=" + (currentTop ?: -9999) + " delta=" + anchorDelta +'''
assert s.count(a)==1
s=s.replace(a,b,1)
# Make the diagnostic distinguish the original fit target from the adjusted jump.
a='''                    "FIT_NEXT probeEnd=" + distance + " align=" + nextContent +'''
b='''                    "FIT_NEXT original=" + originalTarget +
                        " corrected=" + distance + " align=" + nextContent +'''
assert s.count(a)==1
s=s.replace(a,b,1)
p.write_text(s)
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
assert s.count('"SCROLL DEBUG v0.61 | deep movement trace"')==1
s=s.replace('"SCROLL DEBUG v0.61 | deep movement trace"','"SCROLL DEBUG v0.62 | coordinate recheck"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 99")==1
p.write_text(s.replace("versionCode = 99","versionCode = 100",1))
print("v0.62 anchored coordinate recheck applied")
