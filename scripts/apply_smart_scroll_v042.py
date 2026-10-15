#!/usr/bin/env python3
"""v0.42: mechanical thin-line preservation, expanded on-image debug.
Remove rectangle classifiers/guard; reuse existing sampled bitmap."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
start=s.index('                // A rectangle top is a horizontal stroke')
end=s.index('                if (!connected && inkEnd > end',start)
s=s[:start]+s[end:]
s=s.replace('if (!connected && inkEnd > end && inkEnd - end < lookahead && inkEnd < sh && blank[inkEnd]) {',
            'if (inkEnd > end && inkEnd - end < lookahead && inkEnd < sh && blank[inkEnd]) {',1)
# A thin line after a substantial gutter is a safe boundary, not an object to discard.
a='''                    isolatedCount++
                    isolatedCandidateRejected = true
                    isolatedResumeY = ((inkEnd.toLong() * content.height + sh - 1) / sh).toInt()
                    isolatedLineDebug = "ISOLATED: " + isolatedCount + " SKIP@" + ((end.toLong() * content.height + sh - 1) / sh)
                    continue'''
assert s.count(a)==1
s=s.replace(a,'''                    isolatedCount++
                    val preservedY = ((end.toLong() * content.height + sh - 1) / sh).toInt()
                    isolatedLineDebug = "LINE: PRESERVED@" + preservedY +
                        " (THIN AFTER GAP)"
                    lineMarkerY = preservedY
                    result = (preservedY - 3).coerceAtLeast(1)
                    contentDecision = "CONTENT: LINE"
                    break''',1)
# Remove the rectangle-guard correction block; restore v0.38 landing.
start=s.index('            if (result != null) {\n                // The existing gutter algorithm')
end=s.index('            return result',start)
s=s[:start]+'''            if (result != null) {
                chosenGutterY = result
                chosenLandingY = result
            }
'''+s[end:]
# Remove old rectangle diagnostics/marker, and replace with line marker.
s=s.replace('    private var rectangleDebug = "RECT: NOT FOUND"\n','')
s=s.replace('    private var rectangleMarkerY = -1\n','')
s=s.replace('    private var rectangleGuardDebug = "RECT_GUARD: NONE"\n','')
s=s.replace('        rectangleDebug = "RECT: NOT SCANNED"\n','')
s=s.replace('        rectangleMarkerY = -1\n','')
s=s.replace('        rectangleGuardDebug = "RECT_GUARD: NONE"\n','')
s=s.replace('                rectangleDebug = "RECT: REJECTED (NO_GEOMETRY)"\n','')
s=s.replace('            rectangleDebug,\n','')
s=s.replace('            rectangleGuardDebug,\n','')
a='''        paint.color = Color.MAGENTA
        if (rectangleMarkerY in 0 until height) {
            canvas.drawLine(0f, rectangleMarkerY.toFloat(), w, rectangleMarkerY.toFloat(), paint)
        }'''
assert s.count(a)==1
s=s.replace(a,'''        paint.color = Color.MAGENTA
        if (lineMarkerY in 0 until height) {
            val y = lineMarkerY.toFloat()
            canvas.drawLine(0f, y, w, y, paint)
            canvas.drawText("PRESERVED LINE", 8f, y - 7f, paint)
        }''',1)
# State reset only once per detection, alongside existing isolated state.
a='    private var isolatedLineDebug = "ISOLATED: 0"'
assert s.count(a)==1
s=s.replace(a,a+'\n    private var lineMarkerY = -1',1)
a='        isolatedLineDebug = "ISOLATED: 0"'
assert s.count(a)==1
s=s.replace(a,a+'\n        lineMarkerY = -1',1)
# Display the scanned gutter and the rejected/accepted boundary directly.
a='''        paint.color = Color.GREEN
        for (candidate in candidates) {'''
assert s.count(a)==1
s=s.replace(a,'''        paint.color = Color.GREEN
        for (candidate in candidates) {''',1)
s=s.replace('"SCROLL DEBUG v0.41 | rectangle guard 350px"','"SCROLL DEBUG v0.42 | mechanical line preserve"')
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 79")==1
p.write_text(s.replace("versionCode = 79","versionCode = 80",1))
print("v0.42: isolated stroke after gap preserved, magenta line, rectangle logic removed")
