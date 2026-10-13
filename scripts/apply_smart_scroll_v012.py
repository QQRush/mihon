#!/usr/bin/env python3
"""v0.12: tighten separator landing and report precise chosen boundary."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
a=s.index("    fun nextContentAlignedDistance(content: View, target: Int): Int? {")
b=s.index("    // Top Trim is independent",a)
replacement="""    private var chosenGutterY = -1
    private var chosenLandingY = -1

    // Only choose separators that are actually visible, sufficiently near the
    // bottom, and followed by confirmed non-white content.
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
            // A boundary before 65% risks a short/unnatural page; after 90%
            // there is too little confirmed next content to validate it.
            val minRow = sh * 65 / 100
            val maxRow = sh * 90 / 100
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
                if (end >= maxRow || (end - start) * content.height / sh < 65) continue
                // Reject whitespace with no real content on either side.
                val before = (start - 5 until start).any { it >= 0 && !blank[it] }
                val after = (end until (end + 5).coerceAtMost(sh)).any { !blank[it] }
                if (!before || !after) continue
                val distance = (end * content.height / sh - 24).coerceAtLeast(1)
                // Never jump farther than the currently rendered safe area.
                if (distance > content.height * 90 / 100) continue
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
s=s[:a]+replacement+s[b:]
s=s.replace("SCROLL DEBUG v0.11 | smart back + trim","SCROLL DEBUG v0.12 | precision")
s=s.replace('"step=$step req=$requestedJump actual=$measuredJump $jumpMode | gutters=', '"step=$step req=$requestedJump actual=$measuredJump $jumpMode gutterY=$chosenGutterY landingY=$chosenLandingY | gutters=')
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
s=s.replace('val fallback = (recycler.height * 0.78f).toInt().coerceAtLeast(1)','val fallback = (recycler.height * 0.72f).toInt().coerceAtLeast(1)')
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 44") != 1: raise SystemExit("Unexpected versionCode")
p.write_text(s.replace("versionCode = 44","versionCode = 45",1))
print("v0.12 precision patch applied")
