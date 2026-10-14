#!/usr/bin/env python3
"""v0.28 experimental repeat-from: reuse current 96px scan; no second bitmap."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor='    private var contentDecision = "CONTENT: WAIT"'
assert s.count(anchor)==1
s=s.replace(anchor,'''    private var repeatFromY: Int? = null
    private var repeatDecision = "REPEAT: NONE"
    fun repeatFromPartial(): Int? = repeatFromY

'''+anchor)
start=s.index("    fun nextContentAlignedDistance(content:")
end=s.index("    fun extendedLanding(recycler:",start)
part=s[start:end]
a='        contentDecision = "CONTENT: NO_GAP"'
assert part.count(a)==1
part=part.replace(a,'''        contentDecision = "CONTENT: NO_GAP"
        repeatFromY = null
        repeatDecision = "REPEAT: NONE"''')
a='''            val firstRow = sh * 55 / 100'''
assert part.count(a)==1
part=part.replace(a,'''            // A partial balloon at the bottom should reappear from its beginning.
            // Detect the transition from a dense illustration to a predominantly
            // white dialogue region. This uses the bitmap already sampled above.
            // Require real dark content in the bottom 15%, not empty whitespace.
            val bottomStart = sh * 85 / 100
            var bottomInkRows = 0
            for (yy in bottomStart until sh) {
                var ink = 0
                for (xx in 0 until sw) {
                    val c = pixels[yy * sw + xx]
                    if (Color.red(c) < 185 || Color.green(c) < 185 || Color.blue(c) < 185) ink++
                }
                if (ink >= 8) bottomInkRows++
            }
            if (bottomInkRows >= 5) {
                var previousWhite = 0
                var transition: Int? = null
                for (yy in sh * 60 / 100 until sh * 91 / 100) {
                    var white = 0
                    for (xx in 0 until sw) {
                        val c = pixels[yy * sw + xx]
                        if (Color.red(c) >= 240 && Color.green(c) >= 240 && Color.blue(c) >= 240) white++
                    }
                    // A panel-to-dialogue transition, not an arbitrary white row.
                    if (previousWhite <= 22 && white >= 65 && yy >= sh * 65 / 100) {
                        var sustained = 0
                        for (dy in 0 until 8) {
                            if (yy + dy >= sh) break
                            var n = 0
                            for (xx in 0 until sw) {
                                val c = pixels[(yy + dy) * sw + xx]
                                if (Color.red(c) >= 240 && Color.green(c) >= 240 && Color.blue(c) >= 240) n++
                            }
                            if (n >= 55) sustained++
                        }
                        if (sustained >= 6) { transition = yy; break }
                    }
                    previousWhite = white
                }
                if (transition != null) {
                    repeatFromY = (transition * content.height / sh).coerceAtLeast(1)
                    repeatDecision = "REPEAT: FROM=" + repeatFromY
                }
            }
            val firstRow = sh * 55 / 100''')
s=s[:start]+part+s[end:]
a='            contentDecision,'
assert s.count(a)==1
s=s.replace(a,'            contentDecision,\n            repeatDecision,')
a='"SCROLL DEBUG v0.27 | content-aware gutter"'
assert s.count(a)==1
s=s.replace(a,'"SCROLL DEBUG v0.28 | repeat partial"')
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
a='val distance = gutter ?: extended ?: recycler.height.coerceAtLeast(1)'
assert s.count(a)==1
s=s.replace(a,'''// Reuse the existing viewport scan: no extra bitmap or second scroll.
            // A partial element at the bottom is repeated from its start.
            val repeat = if (gutter == null) debugOverlay.repeatFromPartial() else null
            val distance = gutter ?: repeat ?: extended ?: recycler.height.coerceAtLeast(1)''')
p.write_text(s)
p=Path("app/build.gradle.kts");s=p.read_text()
assert s.count("versionCode = 65")==1
p.write_text(s.replace("versionCode = 65","versionCode = 66",1))
print("v0.28 experimental repeat-from installed")
