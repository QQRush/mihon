#!/usr/bin/env python3
"""v0.15 simple bottom-35% viewport gutter, no overlap or source scanning."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
a=s.index("    fun nextContentAlignedDistance(content: View, target: Int): Int? {")
b=s.index("    // Top Trim is independent",a)
replacement="""    // Simple bottom 35% probe. Land exactly on the first content row after
    // a clear horizontal gap. If no next content is visible, return null.
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
                var black = 0
                for (x in 5 until 91) {
                    val c = pixels[row * sw + x]
                    if (Color.red(c) >= 245 && Color.green(c) >= 245 && Color.blue(c) >= 245) white++
                    if (Color.red(c) <= 18 && Color.green(c) <= 18 && Color.blue(c) <= 18) black++
                }
                blank[row] = white >= 85 || black >= 85
            }
            val firstRow = sh * 65 / 100
            var row = firstRow
            var result: Int? = null
            while (row < sh) {
                if (!blank[row]) {
                    row++
                    continue
                }
                val start = row
                while (row < sh && blank[row]) row++
                val end = row
                // Require an obvious gap, preceded and followed by real content.
                if (start <= firstRow || end >= sh - 3 || (end - start) * content.height / sh < 50) continue
                if (!(start - 4 until start).any { it >= 0 && !blank[it] }) continue
                if (!(end until (end + 4).coerceAtMost(sh)).any { !blank[it] }) continue
                // Beginning of next panel goes flush to the top, no white margin.
                val landing = end * content.height / sh
                if (landing > 0 && (result == null || landing > result)) result = landing
            }
            if (result != null) {
                chosenGutterY = result
                chosenLandingY = result
            }
            return result
        } finally {
            bitmap.recycle()
        }
    }

"""
s=s[:a]+replacement+s[b:]
s=s.replace("SCROLL DEBUG v0.14 | source gutters","SCROLL DEBUG v0.15 | bottom 35%")
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
s=s.replace('val fallback = (recycler.height * 0.60f).toInt().coerceAtLeast(1)','val fallback = recycler.height.coerceAtLeast(1)')
s=s.replace('val gutter = sourceGutterDistance(fallback)','val gutter = debugOverlay.nextContentAlignedDistance(recycler, fallback)')
s=s.replace('gutter != null -> "SOURCE_GUTTER"','gutter != null -> "GUTTER"')
p.write_text(s)
# Disable source-image analysis during page loading (keep prior helper unused).
p=base/"WebtoonPageHolder.kt"
s=p.read_text()
a=s.index("            // Analyze the source before the image view consumes the stream.")
b=s.index("            withContext(Dispatchers.Main) {",a)
s=s[:a]+s[b:]
s=s.replace("                page?.let { viewer.cacheSmartPageGutters(it, gutters) }\n","")
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 47")!=1:raise SystemExit("Unexpected versionCode")
p.write_text(s.replace("versionCode = 47","versionCode = 48",1))
print("v0.15 simple navigation installed")
