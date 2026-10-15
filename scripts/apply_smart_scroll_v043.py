#!/usr/bin/env python3
"""v0.43: mechanical context around thin line; keep v0.42 top preservation."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='    private var lineMarkerY = -1'
assert s.count(a)==1
s=s.replace(a,a+'\n    private var passedLineMarkerY = -1',1)
a='        lineMarkerY = -1'
assert s.count(a)==1
s=s.replace(a,a+'\n        passedLineMarkerY = -1',1)
a='''                    isolatedCount++
                    val preservedY = ((end.toLong() * content.height + sh - 1) / sh).toInt()
                    isolatedLineDebug = "LINE: PRESERVED@" + preservedY +
                        " (THIN AFTER GAP)"
                    lineMarkerY = preservedY
                    result = (preservedY - 3).coerceAtLeast(1)
                    contentDecision = "CONTENT: LINE"
                    break'''
assert s.count(a)==1
b='''                    isolatedCount++
                    val lineY = ((end.toLong() * content.height + sh - 1) / sh).toInt()
                    // A closing stroke has nearby content ABOVE it. An
                    // opening stroke follows a long clean area. Only count
                    // meaningful nonblank rows; use the existing bitmap.
                    val contextRows = ((110L * sh + content.height - 1) / content.height)
                        .toInt().coerceAtLeast(1)
                    val contextStart = (end - contextRows).coerceAtLeast(0)
                    var nearbyInkRows = 0
                    for (cy in contextStart until end) {
                        var inkCount = 0
                        for (cx in 5 until 91) {
                            val c = pixels[cy * sw + cx]
                            if (Color.red(c) < 170 && Color.green(c) < 170 && Color.blue(c) < 170) inkCount++
                        }
                        if (inkCount >= 5) nearbyInkRows++
                    }
                    val closingLine = nearbyInkRows >= 7
                    if (closingLine) {
                        passedLineMarkerY = lineY
                        isolatedLineDebug = "LINE: PASSED@" + lineY +
                            " (INK_ABOVE=" + nearbyInkRows + ")"
                        isolatedCandidateRejected = true
                        isolatedResumeY = ((inkEnd.toLong() * content.height + sh - 1) / sh).toInt()
                        continue
                    }
                    isolatedLineDebug = "LINE: PRESERVED@" + lineY +
                        " (CLEAR_ABOVE=" + nearbyInkRows + ")"
                    lineMarkerY = lineY
                    result = (lineY - 3).coerceAtLeast(1)
                    contentDecision = "CONTENT: LINE"
                    break'''
s=s.replace(a,b,1)
a='''        paint.color = Color.MAGENTA
        if (lineMarkerY in 0 until height) {'''
assert s.count(a)==1
s=s.replace(a,'''        paint.color = Color.CYAN
        if (passedLineMarkerY in 0 until height) {
            val y = passedLineMarkerY.toFloat()
            canvas.drawLine(0f, y, w, y, paint)
            canvas.drawText("PASSED LINE", 8f, y - 7f, paint)
        }
        paint.color = Color.MAGENTA
        if (lineMarkerY in 0 until height) {''',1)
s=s.replace('"SCROLL DEBUG v0.42 | mechanical line preserve"','"SCROLL DEBUG v0.43 | line context"')
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 80")==1
p.write_text(s.replace("versionCode = 80","versionCode = 81",1))
print("v0.43 context classification and cyan PASSED LINE diagnostic")
