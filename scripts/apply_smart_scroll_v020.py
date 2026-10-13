#!/usr/bin/env python3
"""v0.20: search forward from computed offset, never from item start."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
start=s.index("    // Read only the visible beginning of the NEXT attached item.")
end=s.index("    override fun onDraw(canvas: Canvas) {",start)
method="""    // Only search for the first content AFTER a blank gutter at the
    // calculated landing offset. Never rewind to the beginning of an item.
    // If landing is inside content or detection is ambiguous, do not adjust.
    fun contentAfterOffset(item: View, offset: Int, scanLength: Int): Int? {
        if (item.width < 2 || item.height < 2 || offset < 0 || offset >= item.height) return null
        val length = minOf(scanLength, item.height - offset)
        if (length < 60) return null
        val sw = 96
        val sh = (length / 3).coerceIn(48, 480)
        val bitmap = Bitmap.createBitmap(sw, sh, Bitmap.Config.ARGB_8888)
        try {
            val canvas = Canvas(bitmap)
            canvas.drawColor(Color.WHITE)
            canvas.scale(sw.toFloat() / item.width, sh.toFloat() / length)
            canvas.translate(0f, -offset.toFloat())
            item.draw(canvas)
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
            // The computed position must already be in blank space;
            // otherwise the rest of a speech bubble might still be unread.
            if (!blank(0) || !blank(1)) return null
            var y = 0
            while (y < sh && blank(y)) y++
            if (y >= sh || y < 3) return null
            if (y + 2 >= sh || blank(y + 1) || blank(y + 2)) return null
            return offset + (y.toLong() * length / sh).toInt()
        } finally { bitmap.recycle() }
    }

"""
s=s[:start]+method+s[end:]
s=s.replace("SCROLL DEBUG v0.19 | boundary target","SCROLL DEBUG v0.20 | offset scan")
# v0.19 script never actually replaced label, so replace existing v0.17r too
s=s.replace("SCROLL DEBUG v0.17r | v0.16 navigation","SCROLL DEBUG v0.20 | offset scan")
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
old="""            val boundaryTarget = if (nextView != null && nextTop != null &&
                nextTop > 0 && nextTop < proposed && nextTop < recycler.height
            ) {
                val visible = recycler.height - nextTop
                val offset = debugOverlay.nextItemContentOffset(nextView, visible)
                nextTop + offset
            } else {
                null
            }
"""
new="""            val boundaryTarget = if (nextView != null && nextTop != null &&
                nextTop > 0 && nextTop < proposed && nextTop < recycler.height
            ) {
                // Proposed is in RecyclerView viewport coordinates.
                // Convert to item-local coordinates BEFORE scanning.
                val offset = proposed - nextTop
                val nextContent = debugOverlay.contentAfterOffset(nextView, offset, recycler.height)
                nextContent?.let { nextTop + it }
            } else {
                null
            }
"""
if s.count(old)!=1:raise SystemExit("v0.19 boundary anchor changed")
s=s.replace(old,new)
s=s.replace('if (boundaryTarget != null) "BOUNDARY"','if (boundaryTarget != null) "OFFSET_GAP"')
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 55")!=1:raise SystemExit("versionCode mismatch")
p.write_text(s.replace("versionCode = 55","versionCode = 56",1))
print("v0.20 offset-based boundary scan applied")
