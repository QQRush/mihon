package eu.kanade.tachiyomi.ui.reader.viewer.webtoon

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.view.View

/**
 * Diagnostic overlay: reports viewport geometry and fixed-scroll target.
 * IMPORTANT: this version does NOT detect image separators.
 */
class SmartScrollDebugOverlay(context: Context) : View(context) {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private var firstItem = 0
    private var firstTop = 0
    private var scrollY = 0
    private var step = 0

    init {
        setWillNotDraw(false)
        visibility = GONE
    }

    fun update(item: Int, top: Int, y: Int, distance: Int) {
        firstItem = item
        firstTop = top
        scrollY = y
        step = distance
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val w = width.toFloat()
        val h = height.toFloat()
        if (w <= 0f || h <= 0f) return
        val baseline = (step.toFloat() / h).coerceIn(0f, 1f) * h
        val lineY = baseline.coerceAtMost(h - 4f)
        paint.strokeWidth = 3f * resources.displayMetrics.density
        paint.color = Color.RED
        canvas.drawLine(0f, lineY, w, lineY, paint)
        paint.color = Color.BLUE
        canvas.drawLine(0f, (h - lineY).coerceAtLeast(0f), w, (h - lineY).coerceAtLeast(0f), paint)
        val density = resources.displayMetrics.density
        val font = 12f * density
        paint.textSize = font
        val lines = listOf(
            "SCROLL DEBUG | no separator detection",
            "item=$firstItem top=$firstTop scrollY=$scrollY",
            "step=$step px | red=target blue=overlap",
        )
        paint.color = Color.BLACK
        canvas.drawRect(0f, 0f, w, (lines.size * 18f + 8f) * density, paint)
        paint.color = Color.WHITE
        lines.forEachIndexed { index, text ->
            canvas.drawText(text, 6f * density, (18f + index * 18f) * density, paint)
        }
    }
}
