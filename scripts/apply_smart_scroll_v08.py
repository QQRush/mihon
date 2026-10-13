#!/usr/bin/env python3
"""v0.8: single-jump navigation based on safe, visible content boundaries."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor="    override fun onDraw(canvas: Canvas) {"
method="""    // Find the first meaningful content after a white gutter near the target.
    // Never jump past an unverified region or beyond the rendered viewport.
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
            val targetRow = (target * sh / content.height).coerceIn(0, sh - 1)
            val radius = (content.height / 7 * sh / content.height).coerceAtLeast(1)
            val first = (targetRow - radius).coerceAtLeast(1)
            val last = (targetRow + radius).coerceAtMost(sh - 2)
            var best: Int? = null
            for (row in first..last) {
                if (!blank[row] || blank[row - 1]) continue
                var end = row
                while (end < sh && blank[end]) end++
                val gutterPixels = (end - row) * content.height / sh
                if (gutterPixels < 65 || end >= sh) continue
                // Place next content 30px from the top, but only when
                // its start is near the ordinary overlap-safe target.
                val aligned = end * content.height / sh - 30
                if (aligned > 0 && aligned <= content.height - 30 &&
                    kotlin.math.abs(aligned - target) <= content.height / 7) {
                    if (best == null || kotlin.math.abs(aligned - target) < kotlin.math.abs(best - target)) {
                        best = aligned
                    }
                }
            }
            return best
        } finally {
            bitmap.recycle()
        }
    }

"""
if s.count(anchor)!=1: raise SystemExit("Overlay anchor missing")
s=s.replace(anchor,method+anchor)
s=s.replace("SCROLL DEBUG v0.7 | top trim scan","SCROLL DEBUG v0.8 | single jump")
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
old="""            val distance = debugOverlay.nearestSafeGutter(target, recycler.height)
                ?: target
            recycler.scrollBy(0, distance)
            // Perform the trim synchronously to avoid a second animated scroll.
            if (readerPreferences.smartScrollTopTrim.get()) {
                val trim = debugOverlay.topWhitespaceToTrim(recycler)
                if (trim > 0) recycler.scrollBy(0, trim)
            }
            updateSmartScrollDebug()"""
new="""            val distance = if (readerPreferences.smartScrollTopTrim.get()) {
                debugOverlay.nextContentAlignedDistance(recycler, target) ?: target
            } else {
                debugOverlay.nearestSafeGutter(target, recycler.height) ?: target
            }
            // One instant scroll only. Never run a post-scroll trim.
            recycler.scrollBy(0, distance)
            updateSmartScrollDebug()"""
if s.count(old)!=1: raise SystemExit("Viewer anchor mismatch")
p.write_text(s.replace(old,new))
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 40")!=1: raise SystemExit("versionCode mismatch")
p.write_text(s.replace("versionCode = 40","versionCode = 41",1))
print("v0.8 single-jump navigation applied")
