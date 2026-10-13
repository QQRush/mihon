#!/usr/bin/env python3
"""v0.18: remove redundant Top Trim, align visible next-image content."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader")
p=base/"setting/ReaderPreferences.kt"
s=p.read_text()
line='    val smartScrollTopTrim: Preference<Boolean> = preferenceStore.getBoolean("smart_scroll_top_trim", true)\n'
if s.count(line)!=1:raise SystemExit("top trim preference anchor mismatch")
p.write_text(s.replace(line,""))
p=Path("app/src/main/java/eu/kanade/presentation/more/settings/screen/SettingsReaderScreen.kt")
s=p.read_text()
block='''                Preference.PreferenceItem.SwitchPreference(
                    preference = readerPreferences.smartScrollTopTrim,
                    title = "Smart Scroll: Top Trim (experimental)",
                ),
'''
if s.count(block)!=1:raise SystemExit("top trim setting anchor mismatch")
p.write_text(s.replace(block,""))
p=base/"viewer/webtoon/SmartScrollDebugOverlay.kt"
s=p.read_text()
a=s.index("    // Top Trim is independent")
b=s.index("    override fun onDraw(canvas: Canvas) {",a)
s=s[:a]+"""    // Only inspect visible pixels below the next image boundary.
    // Never trim a partially visible speech bubble or artwork.
    fun firstContentAfterBoundary(content: View, boundary: Int): Int {
        if (content.width < 2 || content.height < 2 || boundary < 0 || boundary >= content.height) return boundary
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
            val start = (boundary.toLong() * sh / content.height).toInt().coerceIn(0, sh - 1)
            // Restrict trimming to a small, actually visible portion of the next image.
            val limit = (start + sh / 4).coerceAtMost(sh)
            for (y in start until limit) {
                var white = 0
                for (x in 5 until 91) {
                    val c = pixels[y * sw + x]
                    if (Color.red(c) >= 245 && Color.green(c) >= 245 && Color.blue(c) >= 245) white++
                }
                if (white < 85) return y * content.height / sh
            }
            return boundary
        } finally {
            bitmap.recycle()
        }
    }

"""+s[b:]
s=s.replace("SCROLL DEBUG v0.17 | boundary guard","SCROLL DEBUG v0.18 | clean boundary")
p.write_text(s)
p=base/"viewer/webtoon/WebtoonViewer.kt"
s=p.read_text()
old="""            val distance = if (nextItemTop != null && nextItemTop > 0 && nextItemTop < proposedDistance) {
                nextItemTop
            } else {
                proposedDistance
            }
"""
new="""            val distance = if (nextItemTop != null && nextItemTop > 0 && nextItemTop < proposedDistance) {
                debugOverlay.firstContentAfterBoundary(recycler, nextItemTop)
            } else {
                proposedDistance
            }
"""
if s.count(old)!=1:raise SystemExit("boundary anchor mismatch")
p.write_text(s.replace(old,new))
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 50")!=1:raise SystemExit("version mismatch")
p.write_text(s.replace("versionCode = 50","versionCode = 51",1))
print("v0.18: removed Top Trim and aligned visible next-image content")
