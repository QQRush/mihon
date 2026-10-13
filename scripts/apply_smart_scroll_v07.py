#!/usr/bin/env python3
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a=s.index("    fun topWhitespaceToTrim(content: View): Int {")
b=s.index("    override fun onDraw(canvas: Canvas) {",a)
method="""    fun topWhitespaceToTrim(content: View): Int {
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
            var firstContent = -1
            for (row in 0 until (sh * 0.78f).toInt()) {
                var ink = 0
                for (x in 5 until 91) {
                    val pixel = pixels[row * sw + x]
                    if (Color.red(pixel) < 240 || Color.green(pixel) < 240 || Color.blue(pixel) < 240) ink++
                }
                if (ink >= 3) {
                    firstContent = row
                    break
                }
            }
            if (firstContent < 0) return 0
            val whitespace = firstContent * content.height / sh
            return if (whitespace >= 90) {
                (whitespace - 30).coerceIn(0, content.height * 65 / 100)
            } else 0
        } finally {
            bitmap.recycle()
        }
    }

"""
s=s[:a]+method+s[b:]
s=s.replace("SCROLL DEBUG v0.6 | top trim test","SCROLL DEBUG v0.7 | top trim scan")
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 39")==1
p.write_text(s.replace("versionCode = 39","versionCode = 40",1))
print("v0.7 top trim applied")
