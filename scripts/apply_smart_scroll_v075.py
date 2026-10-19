#!/usr/bin/env python3
"""v0.75: navigation checkpoints with cumulative 100px manual-drift tolerance.
No changes to Smart Scroll detectors, FIT_NEXT or its 0px landing margin."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
anchor='''    private fun scrollUp() {'''
assert s.count(anchor)==1
s=s.replace(anchor,'''    private data class SmartScrollCheckpoint(
        val item: Int,
        val top: Int,
        val scrollY: Int,
        val hadFit: Boolean,
    )
    private val smartScrollBackStack = ArrayDeque<SmartScrollCheckpoint>()
    private var smartScrollExpectedY: Int? = null
    private val smartScrollManualTolerance = 100

    private fun smartScrollManualDrifted(): Boolean {
        val expected = smartScrollExpectedY ?: return false
        return kotlin.math.abs(recycler.computeVerticalScrollOffset() - expected) > smartScrollManualTolerance
    }

    private fun smartScrollCheckpoint(): SmartScrollCheckpoint? {
        val item = layoutManager.findFirstVisibleItemPosition()
        if (item < 0) return null
        val top = layoutManager.findViewByPosition(item)?.top ?: return null
        return SmartScrollCheckpoint(item, top, recycler.computeVerticalScrollOffset(), fitEnd > 0)
    }

    private fun scrollUp() {
        if (!readerPreferences.smartScrollEnabled.get()) {
            smartScrollBackStack.clear()
            smartScrollExpectedY = null
            scrollUpOriginal()
            return
        }
        if (smartScrollManualDrifted()) {
            smartScrollBackStack.clear()
            smartScrollExpectedY = null
            scrollUpOriginal()
            return
        }
        val checkpoint = if (smartScrollBackStack.isEmpty()) null else smartScrollBackStack.removeLast()
        if (checkpoint == null) {
            scrollUpOriginal()
            return
        }
        // Restore the RecyclerView item geometry, not a potentially stale
        // absolute scrollY. Smart Fit is a snapshot of this original geometry.
        clearFit()
        layoutManager.scrollToPositionWithOffset(checkpoint.item, checkpoint.top)
        recycler.post {
            updateSmartScrollDebug()
            applyFitIfEligible()
            smartScrollExpectedY = recycler.computeVerticalScrollOffset()
        }
        smartScrollExpectedY = checkpoint.scrollY
    }

    private fun scrollUpOriginal() {''',1)
anchor='''    private fun scrollDown() {'''
assert s.count(anchor)==1
s=s.replace(anchor,'''    private fun scrollDown() {
        if (!readerPreferences.smartScrollEnabled.get()) {
            smartScrollBackStack.clear()
            smartScrollExpectedY = null
            scrollDownOriginal()
            return
        }
        if (smartScrollManualDrifted()) smartScrollBackStack.clear()
        val checkpoint = smartScrollCheckpoint()
        scrollDownOriginal()
        val after = recycler.computeVerticalScrollOffset()
        if (checkpoint != null && after > checkpoint.scrollY) {
            smartScrollBackStack.addLast(checkpoint)
            while (smartScrollBackStack.size > 80) smartScrollBackStack.removeFirst()
        }
        smartScrollExpectedY = after
    }

    private fun scrollDownOriginal() {''',1)
p.write_text(s)
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='"SCROLL DEBUG v0.74 | first ink no padding"'
assert s.count(a)==1
p.write_text(s.replace(a,'"SCROLL DEBUG v0.75 | backward checkpoints"',1))
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 112")==1
p.write_text(s.replace("versionCode = 112","versionCode = 113",1))
print("v0.75 back checkpoints and 100px cumulative manual drift")
