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
    // Diagnostic only. A RecyclerView item is not necessarily one panel.
    fun probeSmartFit(recycler: androidx.recyclerview.widget.RecyclerView, tolerance: Int) {
        val h = recycler.height
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
p.write_text(s)
p=base/"viewer/webtoon/WebtoonViewer.kt"
s=p.read_text()
a='''            debugOverlay.update(first, offset, recycler.computeVerticalScrollOffset(), scrollDistance)'''
assert s.count(a)==1
s=s.replace(a,a+'''
            // Diagnostic only: never touches scroll positions or image scale.
            if (readerPreferences.smartFitEnabled.get()) {
                debugOverlay.probeSmartFit(recycler, readerPreferences.smartFitMaxReduction.get())
            }''',1)
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
