#!/usr/bin/env python3
"""v0.52 SUPER ALPHA: non-invasive Smart Fit diagnostic only.
Measures attached image-items, NOT inferred panels. Does not resize or scroll."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader")
p=base/"viewer/webtoon/SmartScrollDebugOverlay.kt"
s=p.read_text()
a='    private var extendedDebug = "EXT: WAIT"'
assert s.count(a)==1
s=s.replace(a,a+'''
    private var smartFitDebug = "SMART FIT: WAIT"
    private var smartFitMarkerY = -1
    private var smartFitMarkerText = ""
    private var smartFitMarkerEligible = false
    // Diagnostic only. A RecyclerView item is not necessarily one panel.
    fun probeSmartFit(recycler: androidx.recyclerview.widget.RecyclerView, tolerance: Int) {
        val h = recycler.height
        smartFitMarkerY = -1
        smartFitMarkerText = ""
        if (h <= 0) { smartFitDebug = "SMART FIT: NO_VIEW"; invalidate(); return }
        val maxPercent = tolerance.coerceIn(1, 30)
        val items = (0 until recycler.childCount).map { recycler.getChildAt(it) }
            .filter { it.height > 0 && it.bottom > 0 && it.top < h }
        val candidate = items.firstOrNull { it.height > h }
        if (candidate == null) {
            smartFitDebug = "SMART FIT: NO_OVERSIZE_ITEM (limit=" + maxPercent + "%)"
        } else {
            val extra = ((candidate.height.toLong() - h) * 100L / h).toInt()
            val scale = (h.toLong() * 100L / candidate.height).toInt()
            smartFitMarkerEligible = extra <= maxPercent
            smartFitMarkerY = candidate.bottom
            smartFitMarkerText = if (smartFitMarkerEligible) {
                "FIT CANDIDATE " + extra + "% -> " + scale + "% (NOT APPLIED)"
            } else {
                "FIT TOO LONG " + extra + "% (LIMIT " + maxPercent + "%)"
            }
            smartFitDebug = "SMART FIT ITEM: " + candidate.height + "/" + h +
                " OVER=" + extra + "% SCALE=" + scale + "% " +
                (if (extra <= maxPercent) "CANDIDATE (UNVERIFIED)" else "TOO_LONG") +
                " LIMIT=" + maxPercent + "%"
        }
        invalidate()
    }
''',1)
a='            extendedDebug,'
assert s.count(a)==1
s=s.replace(a,a+'\n            smartFitDebug,',1)
assert s.count('"SCROLL DEBUG v0.51 | post-pass preserved top"')==1
s=s.replace('"SCROLL DEBUG v0.51 | post-pass preserved top"','"SCROLL DEBUG v0.52 | fit diagnostic only"',1)
a='    override fun onDraw(canvas: Canvas) {'
assert s.count(a)==1
s=s.replace(a,a+'''
        // Actual item boundary, not a guessed panel boundary.
        if (smartFitMarkerY in 24 until height - 3) {
            val fitPaint = Paint(Paint.ANTI_ALIAS_FLAG)
            fitPaint.color = if (smartFitMarkerEligible) Color.CYAN else Color.YELLOW
            fitPaint.strokeWidth = 3f
            canvas.drawLine(0f, smartFitMarkerY.toFloat(), width.toFloat(),
                smartFitMarkerY.toFloat(), fitPaint)
            fitPaint.textSize = 21f
            val labelY = (smartFitMarkerY - 7).toFloat()
            val labelWidth = fitPaint.measureText(smartFitMarkerText)
            val bgPaint = Paint()
            bgPaint.color = 0xBB000000.toInt()
            canvas.drawRect(0f, labelY - 23f, labelWidth + 12f, labelY + 4f, bgPaint)
            canvas.drawText(smartFitMarkerText, 6f, labelY, fitPaint)
        }
''',1)
p.write_text(s)
p=base/"viewer/webtoon/WebtoonViewer.kt"
s=p.read_text()
# Hook into scroll debug method without relying on its historical update signature.
a='    private fun updateSmartScrollDebug() {'
assert s.count(a)==1
s=s.replace(a,a+'''
        if (readerPreferences.smartScrollEnabled.get() &&
            readerPreferences.smartScrollVisualDebug.get() &&
            readerPreferences.smartFitEnabled.get()) {
            debugOverlay.probeSmartFit(recycler, readerPreferences.smartFitMaxReduction.get())
        }
''',1)
p.write_text(s)
p=base/"setting/ReaderPreferences.kt"
s=p.read_text()
a='preferenceStore.getInt("smart_fit_max_reduction", 20)'
assert s.count(a)==1
s=s.replace(a,'preferenceStore.getInt("smart_fit_max_reduction", 15)',1)
p.write_text(s)
p=Path("app/src/main/java/eu/kanade/presentation/more/settings/screen/SettingsReaderScreen.kt")
s=p.read_text()
a='title = "Smart Fit (preparazione: non ancora attivo)"'
assert s.count(a)==1
s=s.replace(a,'title = "Smart Fit: diagnostica SUPER ALPHA (nessuno zoom)"',1)
a='valueRange = 5..33,'
assert s.count(a)==1
s=s.replace(a,'valueRange = 1..30,',1)
a='title = "Smart Fit: riduzione massima",'
assert s.count(a)==1
s=s.replace(a,'title = "Smart Fit: tolleranza eccedenza",',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 89")==1
p.write_text(s.replace("versionCode = 89","versionCode = 90",1))
print("v0.52 diagnostic: no layout changes, no zoom, no navigation changes")
