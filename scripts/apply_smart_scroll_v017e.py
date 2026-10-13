#!/usr/bin/env python3
"""v0.17e: conservative end-of-viewport blank-gap experiment."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor="    override fun onDraw(canvas: Canvas) {"
method="""    // A minimal viewport-edge test: after an ordinary full-page turn, trim
    // only a tiny already-read fragment followed by a verified blank gutter.
    // Never jump across a nonblank region longer than 5% of the screen.
    fun edgeGapCleanup(content: View): Int {
        if (content.width < 2 || content.height < 2) return 0
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
            fun blank(y: Int): Boolean {
                var white = 0
                for (x in 5 until 91) {
                    val c = pixels[y * sw + x]
                    if (Color.red(c) >= 245 && Color.green(c) >= 245 && Color.blue(c) >= 245) white++
                }
                return white >= 85
            }
            val maxFragment = sh / 20
            var y = 0
            while (y < maxFragment && !blank(y)) y++
            if (y == 0 || y >= maxFragment) return 0
            val start = y
            while (y < sh / 3 && blank(y)) y++
            if (y == sh / 3 || y - start < sh / 30 || blank(y)) return 0
            return y * content.height / sh
        } finally { bitmap.recycle() }
    }

"""
if s.count(anchor)!=1:raise SystemExit("overlay anchor changed")
s=s.replace(anchor,method+anchor)
s=s.replace("SCROLL DEBUG v0.17r | v0.16 navigation","SCROLL DEBUG v0.17e | edge gap test")
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
old="""            recycler.scrollBy(0, distance)
            val afterOffset = recycler.computeVerticalScrollOffset()
"""
new="""            recycler.scrollBy(0, distance)
            // Only for a plain full-height turn: a tiny leftover strip at the
            // new top may be removed if followed by a real, visible white gap.
            val edgeCleanup = if (gutter == null) debugOverlay.edgeGapCleanup(recycler) else 0
            if (edgeCleanup > 0) recycler.scrollBy(0, edgeCleanup)
            val afterOffset = recycler.computeVerticalScrollOffset()
"""
if s.count(old)!=1:raise SystemExit("scroll anchor changed")
s=s.replace(old,new)
s=s.replace('debugOverlay.recordJump(if (gutter != null) "GUTTER" else "OVERLAP",distance,measured)','debugOverlay.recordJump(if (gutter != null) "GUTTER" else if (edgeCleanup > 0) "EDGE_CLEAN" else "FULL",distance + edgeCleanup,measured)')
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 52")!=1:raise SystemExit("version anchor changed")
p.write_text(s.replace("versionCode = 52","versionCode = 53",1))
print("Edge gap experiment installed")
