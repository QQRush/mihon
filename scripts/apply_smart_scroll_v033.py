#!/usr/bin/env python3
"""v0.33: recognize narrow horizontal dark seams and report refinement."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
anchor="    // Sample only seven real-height pixels around the chosen landing."
assert s.count(anchor)==1
s=s.replace(anchor,'''    private var refinementDebug = "REFINE: WAIT"

'''+anchor,1)
start=s.index("    fun refineGutterLanding(recycler:")
end=s.index("    override fun onDraw(canvas: Canvas)",start)
part=s[start:end]
part=part.replace('if (landing < 4 || landing + 4 >= recycler.height || recycler.width < 2) return landing','''if (landing < 4 || landing + 4 >= recycler.height || recycler.width < 2) {
            refinementDebug = "REFINE: EDGE"
            return landing
        }''')
a='''            fun darkRow(y: Int): Boolean {
                var dark = 0
                for (x in 5 until 91) {
                    val c = pixels[y * sw + x]
                    if (Color.red(c) <= 35 && Color.green(c) <= 35 && Color.blue(c) <= 35) dark++
                }
                return dark >= 85
            }
            // A real border is at most 3 pixels high; avoid trimming art.
            // Correct only forward, so we never reveal a previous panel edge.
            for (offset in 0..3) {
                val y = 4 + offset
                if (whiteRow(y)) return landing + offset
                if (!darkRow(y)) break
            }
            return landing'''
assert part.count(a)==1
b='''            fun inkRow(y: Int): Int {
                var ink = 0
                for (x in 5 until 91) {
                    val c = pixels[y * sw + x]
                    if (Color.red(c) < 100 && Color.green(c) < 100 && Color.blue(c) < 100) ink++
                }
                return ink
            }
            // Correct only a thin isolated border: dark ink near the landing,
            // followed by clean white. Never skip a sustained drawing.
            val inkBefore = inkRow(3)
            for (offset in 0..3) {
                val y = 4 + offset
                if (!whiteRow(y)) continue
                val preceding = (4 until y).all { inkRow(it) in 3..65 }
                val isolated = inkBefore >= 3 || (4 until y).any { inkRow(it) >= 3 }
                if (preceding && isolated && (y == 4 || (y + 1 < rows && whiteRow(y + 1)))) {
                    refinementDebug = "REFINE: +" + offset + "px"
                    return landing + offset
                }
            }
            refinementDebug = "REFINE: 0px"
            return landing'''
part=part.replace(a,b)
s=s[:start]+part+s[end:]
a='            contentDecision,'
assert s.count(a)==1
s=s.replace(a,'            contentDecision,\n            refinementDebug,',1)
s=s.replace('"SCROLL DEBUG v0.32 | precise landing"','"SCROLL DEBUG v0.33 | seam refinement"')
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 70")==1
p.write_text(s.replace("versionCode = 70","versionCode = 71",1))
print("v0.33: thin seam refinement and debug")
