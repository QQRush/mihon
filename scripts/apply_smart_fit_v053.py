#!/usr/bin/env python3
"""v0.53 Smart Fit: scan composed viewport plus tolerance for a real separator.
Diagnostic only. Preserve v0.51 navigation, no scaling, no scroll changes."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader")
p=base/"viewer/webtoon/SmartScrollDebugOverlay.kt"
s=p.read_text()
start=s.index("    // Diagnostic only. A RecyclerView item is not necessarily one panel.")
end=s.index("\n    fun extendedNotRun(",start)
s=s[:start]+'''    // Only inspect the current visible content plus user-defined lookahead.
    // This is not a JPG-height test; sample the composed RecyclerView strip.
    fun probeSmartFit(recycler: androidx.recyclerview.widget.RecyclerView, tolerance: Int) {
        val h = recycler.height
        val w = recycler.width
        smartFitMarkerY = -1
        smartFitMarkerText = ""
        if (h < 100 || w < 20) {
            smartFitDebug = "FIT: NO_VIEW"
            invalidate()
            return
        }
        val percent = tolerance.coerceIn(1, 30)
        val extra = h * percent / 100
        val end = h + extra
        val children = (0 until recycler.childCount).map { recycler.getChildAt(it) }
            .filter { it.width > 1 && it.height > 1 && it.bottom > 0 && it.top < end }
            .sortedBy { it.top }
        // Do not start a fit scan when the currently visible image already ends.
        val current = children.firstOrNull { it.top <= 0 && it.bottom > 0 }
        if (current == null || current.bottom <= h) {
            smartFitDebug = "FIT: CURRENT_IMAGE_ENDS_IN_VIEW"
            invalidate()
            return
        }
        var covered = 0
        for (child in children) {
            if (child.top > covered + 2) break
            if (child.bottom > covered) covered = child.bottom
        }
        if (covered < end) {
            smartFitDebug = "FIT: LOOKAHEAD_UNAVAILABLE " + covered + "/" + end
            invalidate()
            return
        }
        val sw = 96
        val sh = (end / 3).coerceIn(150, 750)
        val bmp = Bitmap.createBitmap(sw, sh, Bitmap.Config.ARGB_8888)
        try {
            val c = Canvas(bmp)
            c.drawColor(Color.WHITE)
            c.scale(sw.toFloat() / w, sh.toFloat() / end)
            for (child in children) {
                if (child.top >= end) continue
                c.save()
                c.translate(child.left.toFloat(), child.top.toFloat())
                child.draw(c)
                c.restore()
            }
            val pixels = IntArray(sw * sh)
            bmp.getPixels(pixels, 0, sw, 0, 0, sw, sh)
            val blank = BooleanArray(sh)
            for (y in 0 until sh) {
                var white = 0
                var black = 0
                for (x in 5 until 91) {
                    val color = pixels[y * sw + x]
                    if (Color.red(color) >= 245 && Color.green(color) >= 245 &&
                        Color.blue(color) >= 245) white++
                    if (Color.red(color) <= 18 && Color.green(color) <= 18 &&
                        Color.blue(color) <= 18) black++
                }
                blank[y] = white >= 85 || black >= 85
            }
            // The start of the current block is only known if we can see it.
            // A viewport beginning inside a panel is not safe for fit sizing.
            var firstInk = 0
            while (firstInk < sh && blank[firstInk]) firstInk++
            val startPx = firstInk * end / sh
            if (firstInk == 0 || firstInk >= sh || startPx > h / 3) {
                smartFitDebug = "FIT: START_BOUNDARY_UNKNOWN"
                invalidate()
                return
            }
            val minGap = ((35L * sh + end - 1) / end).toInt().coerceAtLeast(2)
            var y = firstInk
            var found = -1
            while (y < sh) {
                if (!blank[y]) { y++; continue }
                val gapStart = y
                while (y < sh && blank[y]) y++
                val gapEnd = y
                val finish = gapStart * end / sh
                if (gapEnd - gapStart < minGap || finish <= h ||
                    finish > end || gapEnd >= sh - 2) continue
                if (!(gapEnd until minOf(sh, gapEnd + 6)).any { !blank[it] }) continue
                found = finish
                break
            }
            if (found < 0) {
                smartFitDebug = "FIT: SEPARATOR_NOT_FOUND within +" + extra + "px"
            } else {
                val block = found - startPx
                val over = (block.toLong() * 100 / h - 100).toInt()
                val scale = (h.toLong() * 100 / block).toInt()
                smartFitMarkerEligible = block > h && block <= end
                // The detected end lies BELOW the viewport. Put an explicit
                // projected marker at the bottom; never fake its true position.
                smartFitMarkerY = h - 5
                smartFitMarkerText = "FIT FOUND +" + (found - h) +
                    "px BELOW | BLOCK " + block + "px | SCALE " + scale + "%"
                smartFitDebug = "FIT: FOUND start=" + startPx + " end=" + found +
                    " block=" + block + " over=" + over + "% scale=" + scale + "%"
            }
        } finally {
            bmp.recycle()
        }
        invalidate()
    }
''' +s[end:]
a='''        // Actual item boundary, not a guessed panel boundary.'''
assert s.count(a)==1
s=s.replace(a,'''        // Projected viewport-edge marker for a separator detected below screen.
        // Label states the real distance; no fake on-screen panel boundary.''',1)
a='''            fitPaint.color = if (smartFitMarkerEligible) Color.CYAN else Color.YELLOW'''
assert s.count(a)==1
s=s.replace(a,'''            fitPaint.color = Color.CYAN''',1)
s=s.replace('"SCROLL DEBUG v0.52 | fit diagnostic only"','"SCROLL DEBUG v0.53 | separator fit probe"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 90")==1
p.write_text(s.replace("versionCode = 90","versionCode = 91",1))
print("v0.53 separator fit diagnostic installed")
