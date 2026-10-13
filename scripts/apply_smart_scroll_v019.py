#!/usr/bin/env python3
"""v0.19: choose the next image's first visible content before scrolling.
Only change navigation at an image boundary; preserve v0.16 gutter logic.
"""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor="    override fun onDraw(canvas: Canvas) {"
method="""    // Read only the visible beginning of the NEXT attached item.
    // Return an offset into that item, or zero if its content cannot be proven.
    // Crucially, never sample the RecyclerView with previous-item fragments.
    fun nextItemContentOffset(item: View, visiblePixels: Int): Int {
        if (item.width < 2 || visiblePixels < 24) return 0
        val region = minOf(item.height, visiblePixels)
        if (region < 24) return 0
        val sw = 96
        val sh = (region / 3).coerceIn(48, 400)
        val bitmap = Bitmap.createBitmap(sw, sh, Bitmap.Config.ARGB_8888)
        try {
            val canvas = Canvas(bitmap)
            canvas.drawColor(Color.WHITE)
            canvas.scale(sw.toFloat() / item.width, sh.toFloat() / region)
            item.draw(canvas)
            val pixels = IntArray(sw * sh)
            bitmap.getPixels(pixels, 0, sw, 0, 0, sw, sh)
            fun hasContent(y: Int): Boolean {
                var white = 0
                for (x in 5 until 91) {
                    val c = pixels[y * sw + x]
                    if (Color.red(c) >= 245 && Color.green(c) >= 245 && Color.blue(c) >= 245) white++
                }
                return white < 85
            }
            // Require consecutive nonblank rows; if uncertain, preserve
            // the start of the item rather than risk clipping speech bubbles.
            for (y in 0 until sh - 2) {
                if (hasContent(y) && hasContent(y + 1) && hasContent(y + 2)) {
                    return (y.toLong() * region / sh).toInt()
                }
            }
            return 0
        } finally { bitmap.recycle() }
    }

"""
if s.count(anchor)!=1:raise SystemExit("overlay anchor changed")
s=s.replace(anchor,method+anchor)
s=s.replace("SCROLL DEBUG DIAG | v0.17r","SCROLL DEBUG v0.19 | boundary target")
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
old="""            val distance = gutter ?: fallback
            val origin = currentSmartPosition()
"""
new="""            val proposed = gutter ?: fallback
            val firstItem = layoutManager.findFirstVisibleItemPosition()
            val nextView = layoutManager.findViewByPosition(firstItem + 1)
            val nextTop = nextView?.top
            // Only override a proposed jump that would ENTER the next image.
            // Align its first visible content instead of overshooting it.
            val boundaryTarget = if (nextView != null && nextTop != null &&
                nextTop > 0 && nextTop < proposed && nextTop < recycler.height
            ) {
                val visible = recycler.height - nextTop
                val offset = debugOverlay.nextItemContentOffset(nextView, visible)
                nextTop + offset
            } else {
                null
            }
            val distance = boundaryTarget ?: proposed
            val origin = currentSmartPosition()
"""
if s.count(old)!=1:raise SystemExit("navigation anchor mismatch")
s=s.replace(old,new)
s=s.replace('if (gutter != null) "GUTTER" else "FULL"', 'if (boundaryTarget != null) "BOUNDARY" else if (gutter != null) "GUTTER" else "FULL"')
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 52")!=1:raise SystemExit("version mismatch")
p.write_text(s.replace("versionCode = 52","versionCode = 55",1))
print("v0.19 boundary destination correction installed")
