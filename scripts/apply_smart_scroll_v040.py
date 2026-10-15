#!/usr/bin/env python3
"""v0.40 diagnostic only: rectangle candidate state and visual marker.
Navigation and v0.38 rectangle-end behavior remain unchanged."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='    private var rectangleDebug = "RECT: NOT FOUND"'
assert s.count(a)==1
s=s.replace(a,a+'\n    private var rectangleMarkerY = -1',1)
a='        rectangleDebug = "RECT: NOT FOUND"'
assert s.count(a)==1
s=s.replace(a,'        rectangleDebug = "RECT: NOT SCANNED"\n        rectangleMarkerY = -1',1)
a='''                // A rectangle top is a horizontal stroke with two vertical'''
assert s.count(a)==1
s=s.replace(a,'''                rectangleDebug = "RECT: REJECTED (NO_GEOMETRY)"
                // A rectangle top is a horizontal stroke with two vertical''',1)
a='''                        rectangleDebug = when {
                            connected -> "RECT: TOP FOUND@" +
                                ((topY.toLong() * content.height + sh - 1) / sh)
                            topInk >= 25 -> "RECT: UNCERTAIN"
                            else -> "RECT: NOT FOUND"
                        }'''
assert s.count(a)==1
s=s.replace(a,'''                        rectangleMarkerY = ((topY.toLong() * content.height + sh - 1) / sh).toInt()
                        rectangleDebug = when {
                            connected -> "RECT: CONFIRMED@" + rectangleMarkerY
                            topInk >= 25 -> "RECT: CANDIDATE@" + rectangleMarkerY +
                                " REJECTED(SIDES)"
                            else -> "RECT: REJECTED(TOP_INK=" + topInk + ")"
                        }''',1)
# Draw magenta line for the actual geometry-tested row.
a='''        paint.color = Color.BLUE
        if (chosenLandingY in 0 until height) {'''
assert s.count(a)==1
s=s.replace(a,'''        paint.color = Color.MAGENTA
        if (rectangleMarkerY in 0 until height) {
            canvas.drawLine(0f, rectangleMarkerY.toFloat(), w, rectangleMarkerY.toFloat(), paint)
        }
        paint.color = Color.BLUE
        if (chosenLandingY in 0 until height) {''',1)
a='"SCROLL DEBUG v0.39 | rectangle top debug"'
assert s.count(a)==1
s=s.replace(a,'"SCROLL DEBUG v0.40 | rectangle diagnostic"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 77")==1
p.write_text(s.replace("versionCode = 77","versionCode = 78",1))
print("v0.40 diagnostic: magenta geometry probe, statuses; navigation unchanged")
