#!/usr/bin/env python3
"""v0.10: safe page boundaries instead of forcing panel alignment."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
start=s.index("    fun nextContentAlignedDistance(content: View, target: Int): Int? {")
end=s.index("    override fun onDraw(canvas: Canvas) {",start)
replacement="""    private var jumpMode = "WAIT"
    private var requestedJump = 0
    private var measuredJump = 0

    fun recordJump(mode: String, requested: Int, measured: Int) {
        jumpMode = mode
        requestedJump = requested
        measuredJump = measured
        invalidate()
    }

    // Scan the rendered viewport, never unrendered content.
    // Only a sufficiently wide white gap near the page end may be skipped.
    fun nextContentAlignedDistance(content: View, target: Int): Int? {
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
            val blank = BooleanArray(sh)
            for (row in 0 until sh) {
                var white = 0
                for (x in 5 until 91) {
                    val color = pixels[row * sw + x]
                    if (Color.red(color) >= 245 && Color.green(color) >= 245 && Color.blue(color) >= 245) white++
                }
                blank[row] = white >= 85
            }
            // Start looking at 65%: the previous content must be mostly seen.
            val minRow = sh * 65 / 100
            val maxRow = sh * 94 / 100
            var best: Int? = null
            var row = minRow
            while (row < maxRow) {
                if (!blank[row] || blank[row - 1]) {
                    row++
                    continue
                }
                val start = row
                while (row < sh && blank[row]) row++
                val end = row
                if (end >= sh || end > maxRow) continue
                if ((end - start) * content.height / sh < 65) continue
                // Require actual content on both sides of the separator.
                val before = (start - 4 until start).any { it >= 0 && !blank[it] }
                val after = (end until (end + 4).coerceAtMost(sh)).any { !blank[it] }
                if (!before || !after) continue
                val distance = end * content.height / sh - 30
                if (distance > 0 && distance <= content.height * 94 / 100) {
                    if (best == null || kotlin.math.abs(distance - target) < kotlin.math.abs(best - target)) {
                        best = distance
                    }
                }
            }
            return best
        } finally {
            bitmap.recycle()
        }
    }

"""
s=s[:start]+replacement+s[end:]
s=s.replace("SCROLL DEBUG v0.8 | single jump","SCROLL DEBUG v0.10 | safe page turn")
s=s.replace('"step=$step | candidate gutters=', '"step=$step req=$requestedJump actual=$measuredJump $jumpMode | gutters=')
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
start=s.index("            val distance = if (readerPreferences.smartScrollTopTrim.get()) {")
end=s.index("            updateSmartScrollDebug()",start)
s=s[:start]+"""            val fallback = (recycler.height * 0.78f).toInt().coerceAtLeast(1)
            val safeBoundary = if (readerPreferences.smartScrollTopTrim.get()) {
                debugOverlay.nextContentAlignedDistance(recycler, fallback)
            } else {
                null
            }
            val distance = safeBoundary ?: fallback
            val before = recycler.computeVerticalScrollOffset()
            recycler.scrollBy(0, distance)
            val measured = recycler.computeVerticalScrollOffset() - before
            debugOverlay.recordJump(if (safeBoundary != null) "GUTTER" else "OVERLAP", distance, measured)
"""+s[end:]
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 42")!=1: raise SystemExit("Unexpected versionCode")
p.write_text(s.replace("versionCode = 42","versionCode = 43",1))
print("v0.10 safe page turn applied")
