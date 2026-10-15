#!/usr/bin/env python3
"""v0.39: explicit rectangle-top recognition/debug; keep v0.38 end handling."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
anchor='    private var firstContentDebug = "FIRST_CONTENT: NONE"'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n    private var rectangleDebug = "RECT: NOT FOUND"',1)
anchor='        firstContentDebug = "FIRST_CONTENT: NONE"'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n        rectangleDebug = "RECT: NOT FOUND"',1)
start=s.index('                var connected = false')
end=s.index('                if (!connected && inkEnd > end',start)
old=s[start:end]
new='''                // A rectangle top is a horizontal stroke with two vertical
                // sides that persist below it. Test geometry, not the text.
                var connected = false
                if (inkEnd > end && inkEnd < sh && inkEnd - end <= lookahead) {
                    val inkThreshold = 180
                    fun darkAt(x: Int, y: Int): Boolean {
                        val c = pixels[y * sw + x]
                        return Color.red(c) < inkThreshold ||
                            Color.green(c) < inkThreshold ||
                            Color.blue(c) < inkThreshold
                    }
                    val topY = end
                    val sideDepth = ((22L * sh + content.height - 1) / content.height)
                        .toInt().coerceAtLeast(5)
                    val bottom = minOf(sh, topY + sideDepth + 1)
                    if (bottom - topY >= 5) {
                        // Horizontal upper border: sufficient width of dark pixels.
                        val topInk = (5 until 91).count { darkAt(it, topY) }
                        val sides = mutableListOf<Int>()
                        for (x in 5 until 91) {
                            var hits = 0
                            for (y in topY + 1 until bottom) {
                                if (darkAt(x, y)) hits++
                            }
                            if (hits >= (bottom - topY - 1) * 3 / 4) sides.add(x)
                        }
                        // Both sides must be well separated. Do not classify
                        // a single curved line or a text stroke as a box.
                        val left = sides.firstOrNull()
                        val right = sides.lastOrNull()
                        connected = topInk >= 25 && left != null && right != null &&
                            right - left >= 25
                        rectangleDebug = when {
                            connected -> "RECT: TOP FOUND@" +
                                ((topY.toLong() * content.height + sh - 1) / sh)
                            topInk >= 25 -> "RECT: UNCERTAIN"
                            else -> "RECT: NOT FOUND"
                        }
                    }
                }
'''
s=s[:start]+new+s[end:]
# Only update rectangle debug when a potential isolated border is evaluated;
# don't replace the proven first-content/end logic.
anchor='            firstContentDebug,'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n            rectangleDebug,',1)
anchor='"SCROLL DEBUG v0.38 | first content after skip"'
assert s.count(anchor)==1
s=s.replace(anchor,'"SCROLL DEBUG v0.39 | rectangle top debug"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 76")==1
p.write_text(s.replace("versionCode = 76","versionCode = 77",1))
print("v0.39: rectangle top detection + debug; end-of-rectangle unchanged")
