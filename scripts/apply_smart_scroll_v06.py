#!/usr/bin/env python3
"""v0.6 experimental top trim after instant smart-scroll taps."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor="    override fun onDraw(canvas: Canvas) {"
method="""    // Detect only a contiguous white band at the top of the newly visible viewport.
    // Returns zero if uncertain, to avoid skipping dialogue or artwork.
    fun topWhitespaceToTrim(content: View): Int {
        if (content.width < 2 || content.height < 2) return 0
        val sw = 64
        val sh = (content.height / 3).coerceIn(80, 480)
        val bmp = Bitmap.createBitmap(sw, sh, Bitmap.Config.ARGB_8888)
        try {
            val c = Canvas(bmp)
            c.drawColor(Color.WHITE)
            c.scale(sw.toFloat() / content.width, sh.toFloat() / content.height)
            content.draw(c)
            val pixels = IntArray(sw * sh)
            bmp.getPixels(pixels, 0, sw, 0, 0, sw, sh)
            var blankRows = 0
            val maxRows = (sh * 0.42f).toInt()
            for (row in 0 until maxRows) {
                var white = 0
                for (x in 5 until 59) {
                    val pixel = pixels[row * sw + x]
                    if (Color.red(pixel) >= 245 && Color.green(pixel) >= 245 && Color.blue(pixel) >= 245) white++
                }
                if (white < 53) break
                blankRows++
            }
            val pixelsHigh = blankRows * content.height / sh
            val safety = 28
            return if (pixelsHigh >= 85) (pixelsHigh - safety).coerceAtMost(content.height / 3) else 0
        } finally {
            bmp.recycle()
        }
    }

"""
if s.count(anchor)!=1: raise SystemExit("overlay insertion anchor missing")
s=s.replace(anchor,method+anchor)
s=s.replace('SCROLL DEBUG v0.4 | min gutter 60px','SCROLL DEBUG v0.6 | top trim test')
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
old="""            recycler.scrollBy(0, distance)
            updateSmartScrollDebug()"""
new="""            recycler.scrollBy(0, distance)
            // Perform the trim synchronously to avoid a second animated scroll.
            if (readerPreferences.smartScrollTopTrim.get()) {
                val trim = debugOverlay.topWhitespaceToTrim(recycler)
                if (trim > 0) recycler.scrollBy(0, trim)
            }
            updateSmartScrollDebug()"""
if s.count(old)!=1: raise SystemExit("scroll anchor missing")
p.write_text(s.replace(old,new))
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/setting/ReaderPreferences.kt")
s=p.read_text()
old='    val smartScrollVisualDebug: Preference<Boolean> = preferenceStore.getBoolean("smart_scroll_visual_debug", false)'
if s.count(old)!=1: raise SystemExit("preference anchor missing")
p.write_text(s.replace(old,old+'\n\n    val smartScrollTopTrim: Preference<Boolean> = preferenceStore.getBoolean("smart_scroll_top_trim", true)'))
p=Path("app/src/main/java/eu/kanade/presentation/more/settings/screen/SettingsReaderScreen.kt")
s=p.read_text()
old='                    title = "Smart Scroll: visual debug",\n                ),'
if s.count(old)!=1: raise SystemExit("settings anchor missing")
p.write_text(s.replace(old,old+'\n                Preference.PreferenceItem.SwitchPreference(\n                    preference = readerPreferences.smartScrollTopTrim,\n                    title = "Smart Scroll: Top Trim (experimental)",\n                ),'))
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 38")!=1: raise SystemExit("versionCode anchor missing")
p.write_text(s.replace("versionCode = 38","versionCode = 39",1))
print("Smart Scroll v0.6 top trim applied")
