#!/usr/bin/env python3
"""v0.71: complete a verified current gutter with Smart Scroll's own lookahead.
Keep PASSED/PRESERVED, Fit and fallback unchanged."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
start=s.index("    fun extendedLanding(recycler:")
end=s.index("    override fun onDraw(canvas: Canvas)",start)
part=s[start:end]
a="fun extendedLanding(recycler: androidx.recyclerview.widget.RecyclerView, afterIsolated: Boolean = false): Int?"
assert part.count(a)==1
part=part.replace(a,"fun extendedLanding(recycler: androidx.recyclerview.widget.RecyclerView, afterIsolated: Boolean = false, currentGutter: Int? = null): Int?",1)
a='''                if ((afterIsolated && stop <= resumeRow) ||
                    (!afterIsolated && (start >= edge || stop <= edge))) {'''
assert part.count(a)==1
part=part.replace(a,'''                val gapStartPx = from + start * span / sh
                val gapStopPx = from + stop * span / sh
                val continuesCurrent = currentGutter != null && !afterIsolated &&
                    gapStartPx <= currentGutter && gapStopPx > currentGutter &&
                    gapStartPx < h && gapStopPx > h
                if ((afterIsolated && stop <= resumeRow) ||
                    (!afterIsolated && !continuesCurrent && (start >= edge || stop <= edge))) {''',1)
# In current-gutter mode, only a matching crossing band is allowed to return.
a='''                if (stop >= sh - 3) {'''
assert part.count(a)==1
part=part.replace(a,'''                if (currentGutter != null && !continuesCurrent) {
                    reason = "NOT_CURRENT_GAP"
                    continue
                }
                if (stop >= sh - 3) {''',1)
# Preserve all the existing checks (width, content before/after).
s=s[:start]+part+s[end:]
a='"SCROLL DEBUG v0.70 | first rejected gap diagnostic"'
assert s.count(a)==1
s=s.replace(a,'"SCROLL DEBUG v0.71 | current gap end lookahead"',1)
p.write_text(s)
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
a='''            val extended = if (gutter == null && (afterIsolated || readerPreferences.smartScrollTopTrim.get())) {
                debugOverlay.extendedLanding(recycler, afterIsolated)
            } else {'''
assert s.count(a)==1
b='''            val extended = if ((gutter == null && (afterIsolated || readerPreferences.smartScrollTopTrim.get())) ||
                (gutter != null && !afterIsolated && readerPreferences.smartScrollTopTrim.get())) {
                debugOverlay.extendedLanding(recycler, afterIsolated, if (afterIsolated) null else gutter)
            } else {'''
s=s.replace(a,b,1)
a='''            val distance = gutter ?: extended ?: if (afterIsolated) {'''
assert s.count(a)==1
s=s.replace(a,'''            val distance = if (gutter != null && extended != null && extended > gutter) {
                extended
            } else gutter ?: extended ?: if (afterIsolated) {''',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 108")==1
p.write_text(s.replace("versionCode = 108","versionCode = 109",1))
print("v0.71 current gutter completion with independent Smart Scroll scan")
