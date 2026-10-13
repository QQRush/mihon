#!/usr/bin/env python3
"""v0.13: safe text continuity, exact gutter landing, no blind top trimming."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
start=s.index("    // Only choose separators that are actually visible")
end=s.index("    // Top Trim is independent", start)
replacement="""    // A visible gap is safe only if its entire preceding content is visible
    // and the next content is verifiably visible below it.
    fun nextContentAlignedDistance(content: View, target: Int): Int? {
        chosenGutterY = -1
        chosenLandingY = -1
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
                    val pixel = pixels[row * sw + x]
                    if (Color.red(pixel) >= 245 && Color.green(pixel) >= 245 && Color.blue(pixel) >= 245) white++
                }
                blank[row] = white >= 85
            }
            val minRow = sh * 55 / 100
            val maxRow = sh * 92 / 100
            var bestDistance: Int? = null
            var bestEnd = -1
            var row = minRow
            while (row < maxRow) {
                if (!blank[row] || blank[row - 1]) {
                    row++
                    continue
                }
                val start = row
                while (row < sh && blank[row]) row++
                val end = row
                if (end >= maxRow || (end - start) * content.height / sh < 55) continue
                val before = (start - 6 until start).any { it >= 0 && !blank[it] }
                val after = (end until (end + 6).coerceAtMost(sh)).any { !blank[it] }
                if (!before || !after) continue
                // Avoid using an isolated white patch inside a larger picture:
                // it must span most of the sampled width and have a real run.
                val distance = end * content.height / sh - 24
                if (distance <= 0 || distance > content.height * 90 / 100) continue
                // Do not prefer a distant separator over a nearby safe one.
                if (bestDistance == null || kotlin.math.abs(distance - target) < kotlin.math.abs(bestDistance - target)) {
                    bestDistance = distance
                    bestEnd = end
                }
            }
            if (bestDistance != null) {
                chosenGutterY = bestEnd * content.height / sh
                chosenLandingY = bestDistance
            }
            return bestDistance
        } finally {
            bitmap.recycle()
        }
    }

"""
s=s[:start]+replacement+s[end:]
s=s.replace("SCROLL DEBUG v0.12 | precision","SCROLL DEBUG v0.13 | continuity")
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
old="""            val fallback = (recycler.height * 0.72f).toInt().coerceAtLeast(1)
            // Gutter search is always part of Smart Scroll; Top Trim is optional.
            val gutter = debugOverlay.nextContentAlignedDistance(recycler, fallback)
            val trim = if (readerPreferences.smartScrollTopTrim.get() && gutter == null) {
                debugOverlay.safeTopTrimDistance(recycler, fallback)
            } else {
                null
            }
            val distance = gutter ?: trim ?: fallback
"""
new="""            // Conservative overlap prevents the top of an unfinished speech
            // bubble from being pushed outside the next viewport.
            val fallback = (recycler.height * 0.60f).toInt().coerceAtLeast(1)
            val gutter = debugOverlay.nextContentAlignedDistance(recycler, fallback)
            // Top Trim must not override a continuity-preserving fallback:
            // without seeing the future viewport we cannot prove it is blank.
            val trim: Int? = null
            val distance = gutter ?: fallback
"""
if s.count(old)!=1: raise SystemExit("v0.12 scroll anchor mismatch")
s=s.replace(old,new)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 45")!=1: raise SystemExit("Unexpected versionCode")
p.write_text(s.replace("versionCode = 45","versionCode = 46",1))
print("v0.13 continuity patch applied")
