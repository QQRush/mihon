#!/usr/bin/env python3
"""v0.65: find the first next-content row after a full-width gutter.
Use existing white/black row classification and v0.64 fallback if uncertain."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
anchor='    override fun onDraw(canvas: Canvas) {'
assert s.count(anchor)==1
method='''    // Normal navigation only. The current visible gutter can finish just
    // beyond the screen, where the old crossing-only scan rejects it.
    fun nextContentAfterVisibleGap(recycler: androidx.recyclerview.widget.RecyclerView): Int? {
        val h = recycler.height
        val w = recycler.width
        if (h < 100 || w < 20) return null
        val end = h + h * 35 / 100
        val children = (0 until recycler.childCount).map { recycler.getChildAt(it) }
            .filter { it.width > 1 && it.height > 1 && it.bottom > 0 && it.top < end }
            .sortedBy { it.top }
        var covered = 0
        for (child in children) {
            if (child.top > covered + 2) break
            if (child.bottom > covered) covered = child.bottom
        }
        if (covered < end) return null
        val sw = 96
        val sh = (end / 3).coerceIn(150, 750)
        val bmp = Bitmap.createBitmap(sw, sh, Bitmap.Config.ARGB_8888)
        try {
            val c = Canvas(bmp)
            c.drawColor(Color.WHITE)
            c.scale(sw.toFloat() / w, sh.toFloat() / end)
            for (child in children) {
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
            val minGap = ((35L * sh + end - 1) / end).toInt().coerceAtLeast(2)
            var y = (h.toLong() * sh / (2L * end)).toInt()
            val latestStart = (h.toLong() * sh / end).toInt()
            while (y < latestStart) {
                if (!blank[y]) { y++; continue }
                val start = y
                while (y < sh && blank[y]) y++
                if (y - start < minGap || y >= sh - 3) continue
                // The first row after the gap must be real full-width content,
                // not a single noise row or an isolated horizontal stroke.
                var inkRows = 0
                for (cy in y until minOf(sh, y + 10)) {
                    if (!blank[cy]) inkRows++
                }
                if (inkRows < 5) continue
                val landing = (y * end / sh - 8).coerceAtLeast(1)
                if (landing > h / 2 && landing < end - 8) return landing
            }
            return null
        } finally {
            bmp.recycle()
        }
    }

'''
s=s.replace(anchor,method+anchor,1)
a='"SCROLL DEBUG v0.64 | safe fallback overlap"'
assert s.count(a)==1
s=s.replace(a,'"SCROLL DEBUG v0.65 | gap-end landing"',1)
p.write_text(s)
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
a='''            val distance = gutter ?: extended ?: if (afterIsolated) {'''
assert s.count(a)==1
s=s.replace(a,'''            val gapEnd = if (gutter == null && extended == null && !afterIsolated) {
                debugOverlay.nextContentAfterVisibleGap(recycler)
            } else null
            val distance = gutter ?: extended ?: gapEnd ?: if (afterIsolated) {''',1)
a='''else if (extended != null) "EXTENDED@" + extended
                    else if (afterIsolated) "FALLBACK_POST_PASS_50%"'''
assert s.count(a)==1
s=s.replace(a,'''else if (extended != null) "EXTENDED@" + extended
                    else if (gapEnd != null) "GAP_END@" + gapEnd
                    else if (afterIsolated) "FALLBACK_POST_PASS_50%"''',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 102")==1
p.write_text(s.replace("versionCode = 102","versionCode = 103",1))
print("v0.65 full-width visible gutter end landing")
