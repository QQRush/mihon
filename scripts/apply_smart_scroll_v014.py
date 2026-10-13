#!/usr/bin/env python3
"""v0.14: sampled source-image gutters, cached per page; no viewport guessing."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
analyzer=r'''package eu.kanade.tachiyomi.ui.reader.viewer.webtoon

import android.graphics.BitmapFactory
import android.graphics.Color
import okio.BufferedSource

/**
 * Optional low-resolution source-image scan, performed off the UI thread.
 * Returns separator positions as fractions of the original page height.
 * No full-resolution bitmap is retained.
 */
internal object SmartPageGutters {
    fun scan(source: BufferedSource): List<Float> {
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        source.peek().inputStream().use { BitmapFactory.decodeStream(it, null, bounds) }
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return emptyList()
        var sample = 1
        while (maxOf(bounds.outWidth, bounds.outHeight) / sample > 2048) sample *= 2
        val options = BitmapFactory.Options().apply {
            inSampleSize = sample
            inPreferredConfig = android.graphics.Bitmap.Config.RGB_565
        }
        val bitmap = source.peek().inputStream().use { BitmapFactory.decodeStream(it, null, options) }
            ?: return emptyList()
        try {
            val width = bitmap.width
            val height = bitmap.height
            if (width < 8 || height < 20) return emptyList()
            val columns = 48
            val xPositions = IntArray(columns) { i -> ((i + 1L) * (width - 1) / (columns + 1)).toInt() }
            val blank = BooleanArray(height)
            for (y in 0 until height) {
                var light = 0
                var dark = 0
                for (x in xPositions) {
                    val c = bitmap.getPixel(x, y)
                    if (Color.red(c) >= 244 && Color.green(c) >= 244 && Color.blue(c) >= 244) light++
                    if (Color.red(c) <= 18 && Color.green(c) <= 18 && Color.blue(c) <= 18) dark++
                }
                blank[y] = light >= 47 || dark >= 47
            }
            val found = mutableListOf<Float>()
            var start = -1
            for (y in 0..height) {
                val empty = y < height && blank[y]
                if (empty && start == -1) start = y
                if (!empty && start != -1) {
                    val length = y - start
                    // Require a visible, full-width gap with content on both sides.
                    if (start > 4 && y < height - 4 && length >= 5 &&
                        (start - 4 until start).any { !blank[it] } &&
                        (y until y + 4).any { !blank[it] }
                    ) {
                        found.add(y.toFloat() / height)
                    }
                    start = -1
                }
            }
            return found
        } finally {
            bitmap.recycle()
        }
    }
}
'''
(base/"SmartPageGutters.kt").write_text(analyzer)
p=base/"WebtoonPageHolder.kt"
s=p.read_text()
anchor='''            withContext(Dispatchers.Main) {
                frame.setImage('''
if s.count(anchor)!=1:raise SystemExit("PageHolder insertion anchor mismatch")
s=s.replace(anchor,'''            // Analyze the source before the image view consumes the stream.
            // On decode errors, simply fall back to conservative navigation.
            val gutters = if (!isAnimated && viewer.readerPreferences.smartScrollEnabled.get()) {
                withContext(Dispatchers.Default) {
                    runCatching { SmartPageGutters.scan(source) }.getOrDefault(emptyList())
                }
            } else {
                emptyList()
            }
            withContext(Dispatchers.Main) {
                page?.let { viewer.cacheSmartPageGutters(it, gutters) }
                frame.setImage(''')
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
anchor="    private val smartBackHistory = ArrayDeque<SmartPosition>()"
if s.count(anchor)!=1:raise SystemExit("Viewer history anchor mismatch")
s=s.replace(anchor,anchor+'''
    private val smartGutters = java.util.WeakHashMap<ReaderPage, List<Float>>()

    fun cacheSmartPageGutters(page: ReaderPage, positions: List<Float>) {
        smartGutters[page] = positions
    }

    private fun sourceGutterDistance(target: Int): Int? {
        val viewport = recycler.height
        var best: Int? = null
        for (i in 0 until recycler.childCount) {
            val child = recycler.getChildAt(i)
            val itemPosition = recycler.getChildAdapterPosition(child)
            val page = adapter.items.getOrNull(itemPosition) as? ReaderPage ?: continue
            val gutters = smartGutters[page] ?: continue
            for (fraction in gutters) {
                val landing = child.top + (fraction * child.height).toInt() - 24
                // The next content must already be rendered within this viewport;
                // otherwise a safe landing cannot be verified.
                if (landing < viewport * 0.45f || landing > viewport * 0.88f) continue
                if (best == null || kotlin.math.abs(landing - target) < kotlin.math.abs(best - target)) {
                    best = landing
                }
            }
        }
        return best
    }
''')
old='''            val gutter = debugOverlay.nextContentAlignedDistance(recycler, fallback)'''
if s.count(old)!=1:raise SystemExit("Viewer gutter anchor mismatch")
s=s.replace(old,'''            val gutter = sourceGutterDistance(fallback)''')
s=s.replace('''                    gutter != null -> "GUTTER"''','''                    gutter != null -> "SOURCE_GUTTER"''')
p.write_text(s)
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text().replace("SCROLL DEBUG v0.13 | continuity","SCROLL DEBUG v0.14 | source gutters")
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 46")!=1:raise SystemExit("Unexpected versionCode")
p.write_text(s.replace("versionCode = 46","versionCode = 47",1))
print("v0.14 source scan installed")
