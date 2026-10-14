#!/usr/bin/env python3
"""v0.24: bounded lookahead, only attached image views, instant original fallback."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor="    override fun onDraw(canvas: Canvas) {"
assert s.count(anchor)==1
method="""    // Search the last 35% of this screen and at most 35% beyond its edge.
    // Only already attached RecyclerView children are sampled.
    fun extendedLanding(recycler: androidx.recyclerview.widget.RecyclerView): Int? {
        val h = recycler.height
        val w = recycler.width
        if (h < 100 || w < 2) return null
        val from = h * 65 / 100
        val limit = h + h * 35 / 100
        val children = (0 until recycler.childCount).map { recycler.getChildAt(it) }
            .filter { it.width > 1 && it.height > 1 && it.bottom > from && it.top < limit }
            .sortedBy { it.top }
        var covered = from
        for (child in children) {
            if (child.top > covered + 2) break
            if (child.bottom > covered) covered = child.bottom
        }
        if (covered <= h + 60) return null
        val end = minOf(limit, covered)
        val span = end - from
        val sw = 96
        val sh = (span / 3).coerceIn(120, 640)
        val bmp = Bitmap.createBitmap(sw, sh, Bitmap.Config.ARGB_8888)
        try {
            val canvas = Canvas(bmp)
            canvas.drawColor(Color.WHITE)
            canvas.scale(sw.toFloat() / w, sh.toFloat() / span)
            canvas.translate(0f, -from.toFloat())
            for (child in children) {
                if (child.top >= end || child.bottom <= from) continue
                canvas.save()
                canvas.translate(child.left.toFloat(), child.top.toFloat())
                child.draw(canvas)
                canvas.restore()
            }
            val pixels = IntArray(sw * sh)
            bmp.getPixels(pixels, 0, sw, 0, 0, sw, sh)
            val blank = BooleanArray(sh)
            for (y in 0 until sh) {
                var white = 0
                var black = 0
                for (x in 5 until 91) {
                    val c = pixels[y * sw + x]
                    if (Color.red(c) >= 245 && Color.green(c) >= 245 && Color.blue(c) >= 245) white++
                    if (Color.red(c) <= 18 && Color.green(c) <= 18 && Color.blue(c) <= 18) black++
                }
                blank[y] = white >= 85 || black >= 85
            }
            val edge = (h - from) * sh / span
            var y = 0
            while (y < sh) {
                if (!blank[y]) { y++; continue }
                val start = y
                while (y < sh && blank[y]) y++
                val stop = y
                if (start >= edge || stop <= edge || stop >= sh - 3) continue
                if ((stop - start) * span / sh < 50) continue
                if (!(maxOf(0, start - 4) until start).any { !blank[it] }) continue
                if (!(stop until minOf(sh, stop + 4)).any { !blank[it] }) continue
                return from + stop * span / sh
            }
            return null
        } finally {
            bmp.recycle()
        }
    }

"""
s=s.replace(anchor,method+anchor)
s=s.replace("SCROLL DEBUG v0.23 | red=scan blue=landing","SCROLL DEBUG v0.24 | extended scan")
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
a="            val distance = gutter ?: fallback\n"
assert s.count(a)==1
s=s.replace(a,"""            val extended = if (gutter == null && readerPreferences.smartScrollTopTrim.get()) {
                debugOverlay.extendedLanding(recycler)
            } else null
            // Original Mihon distance, but always instant for Smart Scroll.
            val distance = gutter ?: extended ?: scrollDistance
""")
a="""            if (readerPreferences.smartScrollTopTrim.get()) {
                val trim = debugOverlay.topWhitespaceToTrim(recycler)
                if (trim > 0) recycler.scrollBy(0, trim)
            }
"""
assert s.count(a)==1
s=s.replace(a,"")
s=s.replace('if (gutter != null) "GUTTER" else "FULL"','if (gutter != null) "CURRENT" else if (extended != null) "EXTENDED" else "ORIGINAL"')
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 61")==1
p.write_text(s.replace("versionCode = 61","versionCode = 62",1))
print("v0.24 patch applied")
