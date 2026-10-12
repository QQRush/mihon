#!/usr/bin/env python3
"""v0.5: use validated visible-viewport gutters for tap scrolling."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor="    override fun onDraw(canvas: Canvas) {"
addition="""    // Candidates are in visible recycler coordinates; never scan off-screen.
    fun nearestSafeGutter(target: Int, viewportHeight: Int): Int? {
        val tolerance = (viewportHeight * 0.22f).toInt()
        return candidates.filter { it > viewportHeight / 2 && kotlin.math.abs(it - target) <= tolerance }
            .minByOrNull { kotlin.math.abs(it - target) }
    }

"""
if s.count(anchor)!=1: raise SystemExit("overlay anchor mismatch")
s=s.replace(anchor,addition+anchor)
s=s.replace('"SCROLL DEBUG v0.3 | visible viewport only"','"SCROLL DEBUG v0.5 | gutter navigation"')
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
old="""        if (config.usePageTransitions) {
            recycler.smoothScrollBy(0, scrollDistance)
        } else {
            recycler.scrollBy(0, scrollDistance)
        }"""
new="""        if (readerPreferences.smartScrollEnabled.get()) {
            // Probe before moving. If there is no safe gutter, keep a small overlap.
            val target = (recycler.height * 0.88f).toInt().coerceAtLeast(1)
            debugOverlay.update(
                layoutManager.findFirstVisibleItemPosition(),
                layoutManager.findViewByPosition(layoutManager.findFirstVisibleItemPosition())?.top ?: 0,
                recycler.computeVerticalScrollOffset(),
                target,
                recycler,
            )
            val distance = debugOverlay.nearestSafeGutter(target, recycler.height)
                ?: target
            recycler.scrollBy(0, distance)
            updateSmartScrollDebug()
        } else if (config.usePageTransitions) {
            recycler.smoothScrollBy(0, scrollDistance)
        } else {
            recycler.scrollBy(0, scrollDistance)
        }"""
if s.count(old)!=1: raise SystemExit(f"viewer anchor mismatch: expected 1, got {s.count(old)}")
p.write_text(s.replace(old,new))
print("v0.5 gutter navigation applied")

# Keep package identity unchanged; Android requires a strictly higher versionCode.
gradle=Path("app/build.gradle.kts")
g=gradle.read_text()
if g.count("versionCode = 37")!=1: raise SystemExit("Unexpected versionCode")
gradle.write_text(g.replace("versionCode = 37","versionCode = 38",1))
