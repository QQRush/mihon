#!/usr/bin/env python3
"""v0.73: after FIT ART, stop at the art boundary and find the FIRST ink.
Only the one-shot Fit Next path changes; never filter out a thin balloon tip."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor="    override fun onDraw(canvas: Canvas) {"
assert s.count(anchor)==1
helper='''    // One-shot after FIT ART only. A 2px-high sample and ANY foreground
    // pixel preserve the first stroke, including the tip of a speech balloon.
    // Never search for another gap or jump over the first nonblank row.
    fun firstInkAfterFit(recycler: androidx.recyclerview.widget.RecyclerView): Int {
        val w = recycler.width
        val h = recycler.height
        if (w < 4 || h < 80) return 0
        val sw = 160
        val sh = (h / 2).coerceAtLeast(40)
        val bitmap = Bitmap.createBitmap(sw, sh, Bitmap.Config.ARGB_8888)
        try {
            val canvas = Canvas(bitmap)
            canvas.drawColor(Color.WHITE)
            canvas.scale(sw.toFloat() / w, sh.toFloat() / h)
            for (i in 0 until recycler.childCount) {
                val child = recycler.getChildAt(i)
                if (child.width < 2 || child.height < 2 || child.bottom <= 0 || child.top >= h) continue
                canvas.save()
                canvas.translate(child.left.toFloat(), child.top.toFloat())
                child.draw(canvas)
                canvas.restore()
            }
            val pixels = IntArray(sw * sh)
            bitmap.getPixels(pixels, 0, sw, 0, 0, sw, sh)
            // Identify the background from the topmost row. A nonblank top
            // means we are already on content: never trim anything.
            val first = pixels[sw / 2]
            val darkBackground = Color.red(first) < 35 && Color.green(first) < 35 && Color.blue(first) < 35
            val whiteBackground = Color.red(first) > 235 && Color.green(first) > 235 && Color.blue(first) > 235
            if (!darkBackground && !whiteBackground) return 0
            fun isInk(c: Int): Boolean = if (darkBackground) {
                Color.red(c) > 45 || Color.green(c) > 45 || Color.blue(c) > 45
            } else {
                Color.red(c) < 220 || Color.green(c) < 220 || Color.blue(c) < 220
            }
            var firstInk = -1
            for (y in 0 until sh) {
                var ink = false
                for (x in 3 until sw - 3) {
                    if (isInk(pixels[y * sw + x])) { ink = true; break }
                }
                if (ink) { firstInk = y; break }
            }
            if (firstInk <= 4) return 0
            // 8px breathing room ABOVE the first stroke; never below it.
            return ((firstInk.toLong() * h / sh).toInt() - 8).coerceAtLeast(0)
        } finally {
            bitmap.recycle()
        }
    }

'''
s=s.replace(anchor,helper+anchor,1)
a='"SCROLL DEBUG v0.72 | full viewport fallback"'
assert s.count(a)==1
p.write_text(s.replace(a,'"SCROLL DEBUG v0.73 | first ink after fit"',1))
p=base/"WebtoonViewer.kt"
s=p.read_text()
a='''            val distance = (originalTarget + anchorDelta).coerceAtLeast(1)'''
b='''            // Stop at the START of the fitted art's trailing gutter.
            // Advancing to probeEnd could pass a tiny next-content tip.
            val distance = (fittedArt + anchorDelta).coerceAtLeast(1)'''
assert s.count(a)==1
s=s.replace(a,b,1)
a='''                val nextContent = debugOverlay.firstContentAfterBoundary(recycler, 0)'''
b='''                val nextContent = debugOverlay.firstInkAfterFit(recycler)'''
assert s.count(a)==1
s=s.replace(a,b,1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 110")==1
p.write_text(s.replace("versionCode = 110","versionCode = 111",1))
print("v0.73: fit boundary first, one-shot first ink, no minimum shape or gap skipping")
