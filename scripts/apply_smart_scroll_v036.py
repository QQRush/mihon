#!/usr/bin/env python3
"""v0.36: reject isolated thin ink followed by a new blank run; no extra bitmap."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor='    private var contentDecision = "CONTENT: WAIT"'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n    private var isolatedLineDebug = "ISOLATED: 0"')
start=s.index("    fun nextContentAlignedDistance(content:")
end=s.index("    fun extendedLanding(recycler:",start)
part=s[start:end]
anchor='        chosenLandingY = -1'
assert part.count(anchor)==1
part=part.replace(anchor,anchor+'\n        isolatedLineDebug = "ISOLATED: 0"')
anchor='            var result: Int? = null'
assert part.count(anchor)==1
part=part.replace(anchor,anchor+'\n            var isolatedCount = 0')
anchor='                // Beginning of next panel'
assert part.count(anchor)==1
part=part.replace(anchor,'''                // A thin ink border followed by a genuinely blank row is
                // not the beginning of the next panel. Reuse sampled rows.
                // Never reject a continuous curve just for having little ink.
                val lookahead = ((10L * sh + content.height - 1) / content.height).toInt().coerceAtLeast(1)
                var inkEnd = end
                while (inkEnd < sh && !blank[inkEnd] && inkEnd - end < lookahead) inkEnd++
                if (inkEnd > end && inkEnd - end < lookahead && inkEnd < sh && blank[inkEnd]) {
                    isolatedCount++
                    isolatedLineDebug = "ISOLATED: " + isolatedCount + " SKIP@" + ((end.toLong() * content.height + sh - 1) / sh)
                    continue
                }
                // Beginning of next panel''')
s=s[:start]+part+s[end:]
anchor='            contentDecision,'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n            isolatedLineDebug,')
assert s.count('"SCROLL DEBUG v0.35 | gutter +3px"')==1
s=s.replace('"SCROLL DEBUG v0.35 | gutter +3px"','"SCROLL DEBUG v0.36 | isolated line check"')
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
old="val distance = gutter?.plus(3) ?: extended ?: recycler.height.coerceAtLeast(1)"
assert s.count(old)==1
p.write_text(s.replace(old,"val distance = gutter ?: extended ?: recycler.height.coerceAtLeast(1)",1))
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 73")==1
p.write_text(s.replace("versionCode = 73","versionCode = 74",1))
print("v0.36: reject thin isolated border followed by blank; debug ISOLATED")
