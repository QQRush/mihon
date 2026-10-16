#!/usr/bin/env python3
"""v0.57: port Smart Webtoon Scroll viewportBackgroundColor edge luminance
sampling to Mihon's proportional Smart Fit margins. No scroll changes."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
anchor='''    private fun applyFitIfEligible() {'''
assert s.count(anchor)==1
s=s.replace(anchor,'''    // Ported from QQRush/smart-webtoon-scroll.koplugin main.lua:
    // viewportBackgroundColor()/fitSideColor(). Sample both rendered edges
    // at about 24 vertical positions; choose one background for the viewport.
    private fun fitSideBackground(bitmap: Bitmap): Int {
        if (bitmap.width < 2 || bitmap.height < 1) return Color.WHITE
        val inset = minOf(2, maxOf(0, bitmap.width / 100))
        val right = (bitmap.width - 1 - inset).coerceAtLeast(0)
        val step = maxOf(1, bitmap.height / 24)
        var sum = 0L
        var count = 0
        for (y in 0 until bitmap.height step step) {
            for (x in intArrayOf(inset, right)) {
                val pixel = bitmap.getPixel(x, y)
                // Equivalent 8-bit grayscale to the KOReader sample:
                // weighted luminance of RGB rather than one channel.
                val lum = (299 * Color.red(pixel) +
                    587 * Color.green(pixel) + 114 * Color.blue(pixel)) / 1000
                sum += lum
                count++
            }
        }
        return if (count > 0 && sum < 128L * count) Color.BLACK else Color.WHITE
    }

'''+anchor,1)
anchor='''        fitImage.setImageBitmap(bmp)
        // Same factor on both axes: preserve aspect ratio.'''
assert s.count(anchor)==1
s=s.replace(anchor,'''        fitImage.setBackgroundColor(fitSideBackground(bmp))
        fitImage.setImageBitmap(bmp)
        // Same factor on both axes: preserve aspect ratio.''',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 94")==1
p.write_text(s.replace("versionCode = 94","versionCode = 95",1))
print("v0.57 adaptive white/black fit margins")
