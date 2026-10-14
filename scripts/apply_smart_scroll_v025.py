#!/usr/bin/env python3
"""v0.25: diagnose last extended scan; 100% instant fallback. Detector unchanged."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor="    // Search the last 35% of this screen and at most 35% beyond its edge."
assert s.count(anchor)==1
s=s.replace(anchor,"""    private var extendedDebug = "EXT: WAIT"
    fun extendedNotRun(reason: String) {
        extendedDebug = "EXT: " + reason
        invalidate()
    }

"""+anchor)
start=s.index("    fun extendedLanding(recycler:")
end=s.index("    override fun onDraw(canvas: Canvas)",start)
part=s[start:end]
part=part.replace("""        if (h < 100 || w < 2) return null""","""        if (h < 100 || w < 2) {
            extendedNotRun("INVALID_VIEW")
            return null
        }""")
part=part.replace("""        if (covered <= h + 60) return null
        val end = minOf(limit, covered)""","""        val available = (covered - h).coerceAtLeast(0)
        val maximum = limit - h
        if (covered <= h + 60) {
            extendedNotRun("available=" + available + "/" + maximum + " NO_LOOKAHEAD")
            return null
        }
        val end = minOf(limit, covered)
        extendedNotRun("available=" + (end - h) + "/" + maximum + " SCANNING")""")
part=part.replace("""            var y = 0
            while (y < sh) {""","""            var reason = "NO_GAP"
            var y = 0
            while (y < sh) {""")
part=part.replace("""                if (start >= edge || stop <= edge || stop >= sh - 3) continue
                if ((stop - start) * span / sh < 50) continue
                if (!(maxOf(0, start - 4) until start).any { !blank[it] }) continue
                if (!(stop until minOf(sh, stop + 4)).any { !blank[it] }) continue
                return from + stop * span / sh
            }
            return null""","""                if (start >= edge || stop <= edge) {
                    reason = "NOT_CROSSING"
                    continue
                }
                if (stop >= sh - 3) {
                    reason = "NO_CONTENT_AFTER"
                    continue
                }
                if ((stop - start) * span / sh < 50) {
                    reason = "GAP_TOO_SHORT"
                    continue
                }
                if (!(maxOf(0, start - 4) until start).any { !blank[it] }) {
                    reason = "NO_CONTENT_BEFORE"
                    continue
                }
                if (!(stop until minOf(sh, stop + 4)).any { !blank[it] }) {
                    reason = "NO_CONTENT_AFTER"
                    continue
                }
                val landing = from + stop * span / sh
                extendedNotRun("available=" + (end - h) + "/" + maximum + " FOUND@" + landing)
                return landing
            }
            extendedNotRun("available=" + (end - h) + "/" + maximum + " " + reason)
            return null""")
assert 'extendedNotRun("available=" + (end - h) + "/" + maximum + " " + reason)' in part
s=s[:start]+part+s[end:]
anchor='            "SCROLL DEBUG v0.24 | extended scan",'
assert s.count(anchor)==1
s=s.replace(anchor,'            "SCROLL DEBUG v0.25 | extended diagnostics",\n            extendedDebug,')
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
a="""            val extended = if (gutter == null && readerPreferences.smartScrollTopTrim.get()) {
                debugOverlay.extendedLanding(recycler)
            } else null"""
b="""            val extended = if (gutter == null && readerPreferences.smartScrollTopTrim.get()) {
                debugOverlay.extendedLanding(recycler)
            } else {
                debugOverlay.extendedNotRun(if (gutter != null) "CURRENT_GUTTER" else "DISABLED")
                null
            }"""
assert s.count(a)==1
s=s.replace(a,b)
a="val distance = gutter ?: extended ?: scrollDistance"
assert s.count(a)==1
s=s.replace(a,"val distance = gutter ?: extended ?: recycler.height.coerceAtLeast(1)")
p.write_text(s)
p=Path("app/build.gradle.kts");s=p.read_text();assert s.count("versionCode = 62")==1;p.write_text(s.replace("versionCode = 62","versionCode = 63",1))
print("v0.25 diagnostics + instant full-viewport fallback")
