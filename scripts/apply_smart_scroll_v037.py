#!/usr/bin/env python3
"""v0.37: extend search to 150% only after isolated candidate; correct red scan marker."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor='    private var isolatedLineDebug = "ISOLATED: 0"'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n    private var isolatedCandidateRejected = false\n    fun hadIsolatedCandidate(): Boolean = isolatedCandidateRejected')
start=s.index("    fun nextContentAlignedDistance(content:")
end=s.index("    fun extendedLanding(recycler:",start)
part=s[start:end]
assert part.count('        isolatedLineDebug = "ISOLATED: 0"')==1
part=part.replace('        isolatedLineDebug = "ISOLATED: 0"','        isolatedLineDebug = "ISOLATED: 0"\n        isolatedCandidateRejected = false',1)
anchor='                    isolatedCount++'
assert part.count(anchor)==1
part=part.replace(anchor,anchor+'\n                    isolatedCandidateRejected = true')
s=s[:start]+part+s[end:]
start=s.index("    fun extendedLanding(recycler:")
end=s.index("    override fun onDraw(canvas: Canvas)",start)
part=s[start:end]
assert part.count('fun extendedLanding(recycler: androidx.recyclerview.widget.RecyclerView): Int?')==1
part=part.replace('fun extendedLanding(recycler: androidx.recyclerview.widget.RecyclerView): Int?','fun extendedLanding(recycler: androidx.recyclerview.widget.RecyclerView, afterIsolated: Boolean = false): Int?')
assert part.count('val limit = h + h * 35 / 100')==1
part=part.replace('val limit = h + h * 35 / 100','val limit = h + h * (if (afterIsolated) 50 else 35) / 100')
# The original extended scan only permits gutters straddling the viewport edge.
# After rejecting an isolated line, allow gutters starting anywhere after the scan start.
anchor='if (start >= edge || stop <= edge) {'
assert part.count(anchor)==1
part=part.replace(anchor,'if ((!afterIsolated && start >= edge) || stop <= edge) {')
anchor='                val landing = from + stop * span / sh'
assert part.count(anchor)==1
part=part.replace(anchor,'''                if (afterIsolated) {
                    val lookahead = ((10L * sh + span - 1) / span).toInt().coerceAtLeast(1)
                    var inkEnd = stop
                    while (inkEnd < sh && !blank[inkEnd] && inkEnd - stop < lookahead) inkEnd++
                    if (inkEnd > stop && inkEnd - stop < lookahead && inkEnd < sh && blank[inkEnd]) {
                        isolatedLineDebug = "ISOLATED: EXT SKIP@" + (from + stop * span / sh)
                        reason = "ISOLATED_LINE"
                        continue
                    }
                }
                val landing = from + stop * span / sh''')
s=s[:start]+part+s[end:]
assert s.count('canvas.drawLine(0f, h * 0.65f, w, h * 0.65f, paint)')==1
s=s.replace('canvas.drawLine(0f, h * 0.65f, w, h * 0.65f, paint)','canvas.drawLine(0f, h * 0.55f, w, h * 0.55f, paint)')
assert s.count('"SCROLL DEBUG v0.36 | isolated line check"')==1
s=s.replace('"SCROLL DEBUG v0.36 | isolated line check"','"SCROLL DEBUG v0.37 | isolated + 50% search"')
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
old='''            val extended = if (gutter == null && readerPreferences.smartScrollTopTrim.get()) {
                debugOverlay.extendedLanding(recycler)
            } else {'''
new='''            val afterIsolated = gutter == null && debugOverlay.hadIsolatedCandidate()
            val extended = if (gutter == null && (afterIsolated || readerPreferences.smartScrollTopTrim.get())) {
                debugOverlay.extendedLanding(recycler, afterIsolated)
            } else {'''
assert s.count(old)==1
s=s.replace(old,new)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 74")==1
p.write_text(s.replace("versionCode = 74","versionCode = 75",1))
print("v0.37: isolated candidate triggers 50% extended search, red marker at 55%")
