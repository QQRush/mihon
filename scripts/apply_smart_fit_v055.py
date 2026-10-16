#!/usr/bin/env python3
"""v0.55 experimental Smart Fit via temporary rendered viewport snapshot.
No RecyclerView geometry mutation. Fit OFF => original v0.51 navigation."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
a='    private var smartFitMarkerEligible = false'
assert s.count(a)==1
s=s.replace(a,a+'''
    private var smartFitTarget = -1
    fun fitTarget(): Int = smartFitTarget
''',1)
a='''        smartFitMarkerY = -1
        smartFitMarkerText = ""
        if (h < 100'''
assert s.count(a)==1
s=s.replace(a,'''        smartFitMarkerY = -1
        smartFitMarkerText = ""
        smartFitTarget = -1
        if (h < 100''',1)
a='''                smartFitMarkerEligible = block > h && block <= end'''
assert s.count(a)==1
s=s.replace(a,a+'''
                if (smartFitMarkerEligible) smartFitTarget = found''',1)
assert s.count('"SCROLL DEBUG v0.54 | viewport-zero fit probe"')==1
s=s.replace('"SCROLL DEBUG v0.54 | viewport-zero fit probe"','"SCROLL DEBUG v0.55 | live fit snapshot"',1)
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
a='import android.graphics.PointF'
assert s.count(a)==1
s=s.replace(a,a+'''
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.widget.ImageView''',1)
a='    private val debugOverlay = SmartScrollDebugOverlay(activity)'
assert s.count(a)==1
s=s.replace(a,a+'''
    private val fitImage = ImageView(activity)
    private var fitBitmap: Bitmap? = null
    private var fitEnd = -1
    private var fitting = false
    private fun clearFit() {
        fitEnd = -1
        fitImage.visibility = View.GONE
        fitImage.setImageDrawable(null)
        fitBitmap?.recycle()
        fitBitmap = null
    }
    private fun applyFitIfEligible() {
        if (fitting || !readerPreferences.smartScrollEnabled.get() ||
            !readerPreferences.smartFitEnabled.get()) {
            clearFit()
            return
        }
        // Probe regardless of visual-debug preference.
        debugOverlay.probeSmartFit(recycler, readerPreferences.smartFitMaxReduction.get())
        val target = debugOverlay.fitTarget()
        if (target <= recycler.height || target > recycler.height * 13 / 10 ||
            recycler.width < 20) {
            clearFit()
            return
        }
        // All content needed must already be attached. Do not fake missing pixels.
        val children = (0 until recycler.childCount).map { recycler.getChildAt(it) }
            .filter { it.bottom > 0 && it.top < target }.sortedBy { it.top }
        var covered = 0
        for (child in children) {
            if (child.top > covered + 2) break
            covered = maxOf(covered, child.bottom)
        }
        if (covered < target) { clearFit(); return }
        val bmp = try {
            Bitmap.createBitmap(recycler.width, target, Bitmap.Config.ARGB_8888)
        } catch (_: OutOfMemoryError) {
            clearFit()
            return
        }
        try {
            val canvas = Canvas(bmp)
            canvas.drawColor(Color.WHITE)
            for (child in children) {
                canvas.save()
                canvas.translate(child.left.toFloat(), child.top.toFloat())
                child.draw(canvas)
                canvas.restore()
            }
        } catch (_: Exception) {
            bmp.recycle()
            clearFit()
            return
        }
        clearFit()
        fitBitmap = bmp
        fitEnd = target
        fitImage.setImageBitmap(bmp)
        fitImage.visibility = View.VISIBLE
    }
''',1)
a='''        frame.addView(debugOverlay, FrameLayout.LayoutParams(MATCH_PARENT, MATCH_PARENT))'''
assert s.count(a)==1
s=s.replace(a,'''        fitImage.scaleType = ImageView.ScaleType.FIT_XY
        fitImage.isClickable = false
        fitImage.isFocusable = false
        fitImage.visibility = View.GONE
        frame.addView(fitImage, FrameLayout.LayoutParams(MATCH_PARENT, MATCH_PARENT))
'''+a,1)
# After scroll listener update, refresh snapshot only if it was not a fit jump.
a='''                    updateSmartScrollDebug()'''
assert s.count(a)==1
s=s.replace(a,a+'''
                    if (!fitting) applyFitIfEligible()''',1)
# When the reader is first displayed, evaluate initial viewport.
a='''        frame.post { updateSmartScrollDebug() }'''
assert s.count(a)==1
s=s.replace(a,'''        frame.post {
            updateSmartScrollDebug()
            applyFitIfEligible()
        }''',1)
# Next page from fit snapshot goes to separator in ORIGINAL coordinates.
# Clear the overlay first, then let existing scan run from the new position.
a='''    private fun scrollDown() {'''
assert s.count(a)==1
s=s.replace(a,a+'''
        if (fitEnd > recycler.height && readerPreferences.smartFitEnabled.get() &&
            readerPreferences.smartScrollEnabled.get()) {
            val distance = fitEnd
            clearFit()
            fitting = true
            try { recycler.scrollBy(0, distance) } finally { fitting = false }
            updateSmartScrollDebug()
            applyFitIfEligible()
            return
        }
''',1)
# Discard snapshot when going backward and keep original back navigation.
a='''    private fun scrollUp() {'''
assert s.count(a)==1
s=s.replace(a,a+'''
        if (fitEnd > 0) clearFit()
''',1)
# Handle manual movement: no frozen old snapshot on a changed scroll.
a='''    override fun destroy() {'''
assert s.count(a)==1
s=s.replace(a,a+'''
        clearFit()
''',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 92")==1
p.write_text(s.replace("versionCode = 92","versionCode = 93",1))
print("v0.55 snapshot fit with original-coordinate next jump")
