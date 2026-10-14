#!/usr/bin/env python3
"""v0.32: refine visible gutter landing using full-height-resolution rows."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor="    override fun onDraw(canvas: Canvas) {"
assert s.count(anchor)==1
method="""    // Sample only seven real-height pixels around the chosen landing.
    // Unlike the coarse detector, Y is NOT downscaled. Only correct a thin,
    // full-width dark seam followed by a clean white row.
    fun refineGutterLanding(recycler: androidx.recyclerview.widget.RecyclerView, landing: Int): Int {
        if (landing < 4 || landing + 4 >= recycler.height || recycler.width < 2) return landing
        val sw = 96
        val rows = 9
        val bmp = Bitmap.createBitmap(sw, rows, Bitmap.Config.ARGB_8888)
        try {
            val canvas = Canvas(bmp)
            canvas.drawColor(Color.WHITE)
            canvas.scale(sw.toFloat() / recycler.width, 1f)
            canvas.translate(0f, -(landing - 4).toFloat())
            for (i in 0 until recycler.childCount) {
                val child = recycler.getChildAt(i)
                if (child.width < 2 || child.height < 1 ||
                    child.bottom <= landing - 4 || child.top >= landing + 5) continue
                canvas.save()
                canvas.translate(child.left.toFloat(), child.top.toFloat())
                child.draw(canvas)
                canvas.restore()
            }
            val pixels = IntArray(sw * rows)
            bmp.getPixels(pixels, 0, sw, 0, 0, sw, rows)
            fun whiteRow(y: Int): Boolean {
                var white = 0
                for (x in 5 until 91) {
                    val c = pixels[y * sw + x]
                    if (Color.red(c) >= 245 && Color.green(c) >= 245 && Color.blue(c) >= 245) white++
                }
                return white >= 85
            }
            fun darkRow(y: Int): Boolean {
                var dark = 0
                for (x in 5 until 91) {
                    val c = pixels[y * sw + x]
                    if (Color.red(c) <= 35 && Color.green(c) <= 35 && Color.blue(c) <= 35) dark++
                }
                return dark >= 85
            }
            // A real border is at most 3 pixels high; avoid trimming art.
            // Correct only forward, so we never reveal a previous panel edge.
            for (offset in 0..3) {
                val y = 4 + offset
                if (whiteRow(y)) return landing + offset
                if (!darkRow(y)) break
            }
            return landing
        } finally {
            bmp.recycle()
        }
    }

"""
s=s.replace(anchor,method+anchor,1)
s=s.replace('"SCROLL DEBUG v0.29 | visible gutters"','"SCROLL DEBUG v0.32 | precise landing"')
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
a="""val distance = if (gutter != null && gutter >= recycler.height * 99 / 100 &&
                gutter <= recycler.height) {
                gutter + 1
            } else {
                gutter ?: extended ?: recycler.height.coerceAtLeast(1)
            }"""
assert s.count(a)==1
b="""val distance = if (gutter != null) {
                debugOverlay.refineGutterLanding(recycler, gutter)
            } else {
                extended ?: recycler.height.coerceAtLeast(1)
            }"""
s=s.replace(a,b,1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 69")==1
p.write_text(s.replace("versionCode = 69","versionCode = 70",1))
print("v0.32: full-resolution local gutter refinement, no fixed +1")
