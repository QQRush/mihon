#!/usr/bin/env python3
"""Smart Scroll v0.11: manual scroll reset, reversible navigation, pre-jump top trim."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor="    override fun onDraw(canvas: Canvas) {"
method="""    // Top Trim is independent of gutter navigation. Only visible white pixels
    // after the safe overlap target may be skipped; never scan unseen pages.
    fun safeTopTrimDistance(content: View, target: Int): Int? {
        if (content.width < 2 || content.height < 2) return null
        val sw = 96
        val sh = (content.height / 2).coerceIn(120, 640)
        val bitmap = Bitmap.createBitmap(sw, sh, Bitmap.Config.ARGB_8888)
        try {
            val canvas = Canvas(bitmap)
            canvas.drawColor(Color.WHITE)
            canvas.scale(sw.toFloat() / content.width, sh.toFloat() / content.height)
            content.draw(canvas)
            val pixels = IntArray(sw * sh)
            bitmap.getPixels(pixels, 0, sw, 0, 0, sw, sh)
            val targetRow = (target.toLong() * sh / content.height).toInt().coerceIn(1, sh - 2)
            fun isBlank(row: Int): Boolean {
                var white = 0
                for (x in 5 until 91) {
                    val pixel = pixels[row * sw + x]
                    if (Color.red(pixel) >= 245 && Color.green(pixel) >= 245 && Color.blue(pixel) >= 245) white++
                }
                return white >= 85
            }
            // We can only trim when the normal destination lies in a verified
            // white run and the next content is already visible on screen.
            if (!isBlank(targetRow)) return null
            var start = targetRow
            while (start > 0 && isBlank(start - 1)) start--
            var end = targetRow
            while (end < sh && isBlank(end)) end++
            if (end >= sh || (end - start) * content.height / sh < 65) return null
            if (end >= sh - 3 || (end until end + 3).all { isBlank(it) }) return null
            val aligned = end * content.height / sh - 30
            return aligned.takeIf { it >= target && it <= content.height - 30 }
        } finally {
            bitmap.recycle()
        }
    }

"""
if s.count(anchor)!=1: raise SystemExit("Overlay anchor mismatch")
s=s.replace(anchor,method+anchor)
s=s.replace("SCROLL DEBUG v0.10 | safe page turn","SCROLL DEBUG v0.11 | smart back + trim")
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
anchor="    private val debugOverlay = SmartScrollDebugOverlay(activity)"
if s.count(anchor)!=1: raise SystemExit("Viewer overlay anchor mismatch")
s=s.replace(anchor,anchor+"""
    private data class SmartPosition(val item: Int, val top: Int)
    private val smartBackHistory = ArrayDeque<SmartPosition>()
    private var manualScrollInProgress = false

    private fun currentSmartPosition(): SmartPosition? {
        val item = layoutManager.findFirstVisibleItemPosition()
        if (item == RecyclerView.NO_POSITION) return null
        return SmartPosition(item, layoutManager.findViewByPosition(item)?.top ?: 0)
    }
""")
anchor="                override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {"
if s.count(anchor)!=1: raise SystemExit("Scroll listener anchor mismatch")
s=s.replace(anchor,"""                override fun onScrollStateChanged(recyclerView: RecyclerView, newState: Int) {
                    if (newState == RecyclerView.SCROLL_STATE_DRAGGING) {
                        manualScrollInProgress = true
                    } else if (newState == RecyclerView.SCROLL_STATE_IDLE && manualScrollInProgress) {
                        manualScrollInProgress = false
                        smartBackHistory.clear()
                        // No bitmap work here: recalculate lazily on the next tap.
                        updateSmartScrollDebug()
                    }
                }

"""+anchor)
anchor="""    private fun scrollUp() {
        updateSmartScrollDebug()
"""
if s.count(anchor)!=1: raise SystemExit("scrollUp anchor mismatch")
s=s.replace(anchor,anchor+"""        if (readerPreferences.smartScrollEnabled.get() && smartBackHistory.isNotEmpty()) {
            val position = smartBackHistory.removeLast()
            layoutManager.scrollToPositionWithOffset(position.item, position.top)
            recycler.post { updateSmartScrollDebug() }
            return
        }
""")
start=s.index("            val fallback = (recycler.height * 0.78f)")
end=s.index("            updateSmartScrollDebug()",start)
replacement="""            val fallback = (recycler.height * 0.78f).toInt().coerceAtLeast(1)
            // Gutter search is always part of Smart Scroll; Top Trim is optional.
            val gutter = debugOverlay.nextContentAlignedDistance(recycler, fallback)
            val trim = if (readerPreferences.smartScrollTopTrim.get() && gutter == null) {
                debugOverlay.safeTopTrimDistance(recycler, fallback)
            } else {
                null
            }
            val distance = gutter ?: trim ?: fallback
            val origin = currentSmartPosition()
            val beforeItem = layoutManager.findFirstVisibleItemPosition()
            val beforeTop = layoutManager.findViewByPosition(beforeItem)?.top ?: 0
            recycler.scrollBy(0, distance)
            val afterItem = layoutManager.findFirstVisibleItemPosition()
            val afterTop = layoutManager.findViewByPosition(afterItem)?.top ?: 0
            if (origin != null && (beforeItem != afterItem || beforeTop != afterTop)) {
                smartBackHistory.addLast(origin)
                if (smartBackHistory.size > 20) smartBackHistory.removeFirst()
            }
            // Pixel delta is meaningful only while the same item is visible.
            val measured = if (beforeItem == afterItem) beforeTop - afterTop else 0
            debugOverlay.recordJump(
                when {
                    gutter != null -> "GUTTER"
                    trim != null -> "TOP_TRIM"
                    else -> "OVERLAP"
                },
                distance,
                measured,
            )
"""
s=s[:start]+replacement+s[end:]
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 43")!=1: raise SystemExit("versionCode mismatch")
p.write_text(s.replace("versionCode = 43","versionCode = 44",1))
print("v0.11 installed")
