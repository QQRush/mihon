#!/usr/bin/env python3
"""v0.27: lightweight post-gutter content verification using existing pixels."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
anchor="    // Simple bottom 35% probe."
assert s.count(anchor)==1
s=s.replace(anchor,"""    private var contentDecision = "CONTENT: WAIT"

    // Reject isolated borders and tiny marks after a gap.
    // Use the bitmap already sampled by each detector, without a second draw.
    private fun hasMeaningfulContent(pixels: IntArray, width: Int, height: Int, after: Int): Boolean {
        val end = minOf(height, after + 16)
        if (end - after < 8) return false
        var strongRows = 0
        for (y in after until end) {
            var ink = 0
            for (x in 5 until 91) {
                val c = pixels[y * width + x]
                if (!(Color.red(c) >= 245 && Color.green(c) >= 245 && Color.blue(c) >= 245)) ink++
            }
            if (ink >= 12) strongRows++
        }
        return strongRows >= 3
    }

"""+anchor)
start=s.index("    fun nextContentAlignedDistance(content:")
end=s.index("    fun extendedLanding(recycler:",start)
part=s[start:end]
a="""        chosenLandingY = -1
        if (content.width < 2"""
assert part.count(a)==1
part=part.replace(a,"""        chosenLandingY = -1
        contentDecision = "CONTENT: NO_GAP"
        if (content.width < 2""")
a="""                if (!(end until (end + 4).coerceAtMost(sh)).any { !blank[it] }) continue
                // Beginning of next panel"""
assert part.count(a)==1
part=part.replace(a,"""                if (!(end until (end + 4).coerceAtMost(sh)).any { !blank[it] }) continue
                if (!hasMeaningfulContent(pixels, sw, sh, end)) {
                    contentDecision = "CONTENT: WEAK"
                    continue
                }
                contentDecision = "CONTENT: OK"
                // Beginning of next panel""")
s=s[:start]+part+s[end:]
# Same lightweight content check for the extended scan, so weak current candidates
# cannot simply pass through the alternate path.
start=s.index("    fun extendedLanding(recycler:")
end=s.index("    override fun onDraw(canvas: Canvas)",start)
part=s[start:end]
a="""                val landing = from + stop * span / sh
                extendedNotRun("""
assert part.count(a)==1
part=part.replace(a,"""                if (!hasMeaningfulContent(pixels, sw, sh, stop)) {
                    reason = "CONTENT_WEAK"
                    continue
                }
                val landing = from + stop * span / sh
                extendedNotRun(""")
s=s[:start]+part+s[end:]
a='            "SCROLL DEBUG v0.26 | first safe gutter",'
assert s.count(a)==1
s=s.replace(a,'            "SCROLL DEBUG v0.27 | content-aware gutter",\n            contentDecision,')
p.write_text(s)
p=Path("app/build.gradle.kts");s=p.read_text();assert s.count("versionCode = 64")==1
p.write_text(s.replace("versionCode = 64","versionCode = 65",1))
print("v0.27 content-aware separator filter")
