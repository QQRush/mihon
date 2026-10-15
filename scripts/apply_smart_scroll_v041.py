#!/usr/bin/env python3
"""v0.41: bounded 350-screen-pixel rectangle-top guard, using existing bitmap."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
anchor='    private var rectangleMarkerY = -1'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n    private var rectangleGuardDebug = "RECT_GUARD: NONE"',1)
anchor='        rectangleMarkerY = -1'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n        rectangleGuardDebug = "RECT_GUARD: NONE"',1)
start=s.index('    fun nextContentAlignedDistance(content:')
end=s.index('    fun extendedLanding(recycler:',start)
part=s[start:end]
anchor='''            if (result != null) {
                chosenGutterY = result
                chosenLandingY = result
            }
            return result'''
assert part.count(anchor)==1
replacement='''            if (result != null) {
                // The existing gutter algorithm remains authoritative unless
                // we positively identify a rectangle enclosing its landing.
                val original = result
                val landingRow = ((original.toLong() * sh) / content.height)
                    .toInt().coerceIn(0, sh - 1)
                val maxRise = ((350L * sh + content.height - 1) / content.height)
                    .toInt().coerceAtLeast(1)
                fun ink(x: Int, y: Int): Boolean {
                    val c = pixels[y * sw + x]
                    return Color.red(c) < 110 && Color.green(c) < 110 && Color.blue(c) < 110
                }
                // First find two persistent vertical strokes around the
                // landing. Allow tiny gaps from sampling and antialiasing.
                val depth = ((35L * sh + content.height - 1) / content.height)
                    .toInt().coerceAtLeast(5)
                val y0 = (landingRow - depth / 2).coerceAtLeast(0)
                val y1 = (landingRow + depth / 2).coerceAtMost(sh - 1)
                val verticals = mutableListOf<Int>()
                if (y1 - y0 >= 4) {
                    for (x in 3 until sw - 3) {
                        var hits = 0
                        for (y in y0..y1) {
                            if ((x - 1..x + 1).any { ink(it, y) }) hits++
                        }
                        if (hits * 4 >= (y1 - y0 + 1) * 3) verticals.add(x)
                    }
                }
                var corrected: Int? = null
                // The sides must be separated by a meaningful box width.
                val left = verticals.firstOrNull()
                val right = verticals.lastOrNull()
                if (left != null && right != null && right - left >= 22) {
                    val minRow = (landingRow - maxRise).coerceAtLeast(0)
                    // Follow both sides upward and look for the joining top.
                    for (y in landingRow - 1 downTo minRow) {
                        if (y < 0) break
                        val l = (left - 2..left + 2).any { x -> x in 0 until sw && ink(x, y) }
                        val r = (right - 2..right + 2).any { x -> x in 0 until sw && ink(x, y) }
                        if (!l || !r) break
                        var across = 0
                        for (x in left..right) if (ink(x, y)) across++
                        if (across * 100 >= (right - left + 1) * 75) {
                            val top = ((y.toLong() * content.height) / sh).toInt()
                            // Do not move backward by more than 350 px.
                            if (original - top in 1..350) {
                                corrected = (top - 4).coerceAtLeast(1)
                                rectangleMarkerY = top
                            }
                            break
                        }
                    }
                }
                if (corrected != null) {
                    rectangleGuardDebug = "RECT_GUARD: TOP@" + rectangleMarkerY +
                        " FROM@" + original
                    result = corrected
                } else {
                    rectangleGuardDebug = "RECT_GUARD: NO_MATCH"
                }
                chosenGutterY = original
                chosenLandingY = result
            }
            return result'''
part=part.replace(anchor,replacement,1)
s=s[:start]+part+s[end:]
anchor='            rectangleDebug,'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n            rectangleGuardDebug,',1)
anchor='"SCROLL DEBUG v0.40 | rectangle diagnostic"'
assert s.count(anchor)==1
s=s.replace(anchor,'"SCROLL DEBUG v0.41 | rectangle guard 350px"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 78")==1
p.write_text(s.replace("versionCode = 78","versionCode = 79",1))
print("v0.41 rectangle top guard (350px max), existing gutter/end preserved")
