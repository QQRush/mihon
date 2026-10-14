#!/usr/bin/env python3
"""v0.29: prefer visible real gutters; remove unused v0.28 repeat heuristic."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
a='    private var repeatFromY: Int? = null\n    private var repeatDecision = "REPEAT: NONE"\n    fun repeatFromPartial(): Int? = repeatFromY\n\n'
assert s.count(a)==1
s=s.replace(a,"")
start=s.index("    fun nextContentAlignedDistance(content:")
end=s.index("    fun extendedLanding(recycler:",start)
part=s[start:end]
a='        repeatFromY = null\n        repeatDecision = "REPEAT: NONE"\n'
assert part.count(a)==1
part=part.replace(a,"")
a='            // A partial balloon at the bottom should reappear from its beginning.'
b='            val firstRow = sh * 55 / 100'
assert part.count(a)==1 and part.count(b)==1
part=part[:part.index(a)]+part[part.index(b):]
a='''                if (!hasMeaningfulContent(pixels, sw, sh, end)) {
                    contentDecision = "CONTENT: WEAK"
                    continue
                }
                contentDecision = "CONTENT: OK"
'''
assert part.count(a)==1
part=part.replace(a,'''                // A complete horizontal gap already separates the content.
                // Do not reject it merely because the following balloon has
                // little visible content before the bottom of the screen.
                contentDecision = "CONTENT: GAP"
''')
# A clear full-width separator, not merely the white interior of a speech balloon.
a='''                blank[row] = white >= 85 || black >= 85'''
assert part.count(a)==1
part=part.replace(a,'''                blank[row] = white >= 85 || black >= 85''')
s=s[:start]+part+s[end:]
a='            repeatDecision,\n'
assert s.count(a)==1
s=s.replace(a,"")
a='"SCROLL DEBUG v0.28 | repeat partial"'
assert s.count(a)==1
s=s.replace(a,'"SCROLL DEBUG v0.29 | visible gutters"')
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
a='''            // Reuse the existing viewport scan: no extra bitmap or second scroll.
            // A partial element at the bottom is repeated from its start.
            val repeat = if (gutter == null) debugOverlay.repeatFromPartial() else null
            val distance = gutter ?: repeat ?: extended ?: recycler.height.coerceAtLeast(1)'''
assert s.count(a)==1
s=s.replace(a,'''            // A visible separator may be above the bottom: repeat the
            // partial next element instead of blindly advancing 100%.
            val distance = gutter ?: extended ?: recycler.height.coerceAtLeast(1)''')
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text();assert s.count("versionCode = 66")==1
p.write_text(s.replace("versionCode = 66","versionCode = 67",1))
print("v0.29: visible gutters, no REPEAT")
