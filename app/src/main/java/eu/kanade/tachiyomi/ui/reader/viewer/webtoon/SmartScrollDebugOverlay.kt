package eu.kanade.tachiyomi.ui.reader.viewer.webtoon

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.view.View

/**
 * Debug-only visible-viewport separator probe.
 * Does not alter navigation or claim to scan off-screen pixels.
 */
class SmartScrollDebugOverlay(context: Context) : View(context) {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var firstItem = 0
    private var firstTop = 0
    private var scrollY = 0
    private var step = 0
    private var candidates: List<Int> = emptyList()

    init {
        setWillNotDraw(false)
        visibility = GONE
        isClickable = false
        isFocusable = false
    }

    fun update(item: Int, top: Int, y: Int, distance: Int, content: View) {
        firstItem = item
        firstTop = top
        scrollY = y
        step = distance
        candidates = probe(content)
        invalidate()
    }

    private fun probe(content: View): List<Int> {
        if (content.width < 2 || content.height < 2) return emptyList()
        // Downsample to reduce work; only runs when Visual Debug is enabled.
        val sampleWidth = 64
        val sampleHeight = (content.height / 8).coerceIn(32, 240)
        val bitmap = Bitmap.createBitmap(sampleWidth, sampleHeight, Bitmap.Config.ARGB_8888)
        try {
            val canvas = Canvas(bitmap)
            canvas.scale(sampleWidth.toFloat() / content.width, sampleHeight.toFloat() / content.height)
            content.draw(canvas)
            val pixels = IntArray(sampleWidth * sampleHeight)
            bitmap.getPixels(pixels, 0, sampleWidth, 0, 0, sampleWidth, sampleHeight)
            val blank = BooleanArray(sampleHeight)
            for (row in 0 until sampleHeight) {
                var light = 0
                var dark = 0
                // Ignore the left and right 10% (often UI padding).
                for (x in 7 until 57) {
                    val pixel = pixels[row * sampleWidth + x]
                    val r = Color.red(pixel)
                    val g = Color.green(pixel)
                    val b = Color.blue(pixel)
                    if (r > 238 && g > 238 && b > 238) light++
                    if (r < 20 && g < 20 && b < 20) dark++
                }
                blank[row] = light >= 49 || dark >= 49
            }
            val found = mutableListOf<Int>()
            var start = -1
            for (row in 0..sampleHeight) {
                val isBlank = row < sampleHeight && blank[row]
                if (isBlank && start < 0) start = row
                if (!isBlank && start >= 0) {
                    val end = row
                    if (end - start >= 3 && start > 8 && end < sampleHeight - 4) {
                        val center = (start + end) / 2
                        found.add(center * content.height / sampleHeight)
                    }
                    start = -1
                }
            }
            return found.take(12)
        } finally {
            bitmap.recycle()
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val w = width.toFloat()
        val h = height.toFloat()
        if (w <= 0f || h <= 0f) return
        val lineY = step.toFloat().coerceIn(0f, h - 4f)
        paint.strokeWidth = 2f * resources.displayMetrics.density
        paint.color = Color.RED
        canvas.drawLine(0f, lineY, w, lineY, paint)
        paint.color = Color.BLUE
        canvas.drawLine(0f, (h - lineY).coerceAtLeast(0f), w, (h - lineY).coerceAtLeast(0f), paint)
        paint.color = Color.GREEN
        for (candidate in candidates) {
            val cy = candidate.toFloat()
            if (cy in 0f..h) canvas.drawLine(0f, cy, w, cy, paint)
        }
        val density = resources.displayMetrics.density
        paint.textSize = 12f * density
        val lines = listOf(
            "SCROLL DEBUG v0.3 | visible viewport only",
            "item=$firstItem top=$firstTop scrollY=$scrollY",
            "step=$step | candidate gutters=${candidates.size}",
        )
        paint.color = Color.BLACK
        canvas.drawRect(0f, 0f, w, (lines.size * 18f + 8f) * density, paint)
        paint.color = Color.WHITE
        lines.forEachIndexed { index, text ->
            canvas.drawText(text, 6f * density, (18f + index * 18f) * density, paint)
        }
    }
}
