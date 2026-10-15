#!/usr/bin/env python3
"""v0.45: v0.43 classification, then skip entire closing stroke and seek next gutter.
No rectangle recognition. Keep preserved top behavior unchanged."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='    private var passedLineMarkerY = -1'
assert s.count(a)==1
s=s.replace(a,a+'\n    private var passedLineEndY = -1',1)
a='        passedLineMarkerY = -1'
assert s.count(a)==1
s=s.replace(a,a+'\n        passedLineEndY = -1',1)
# The current scan already knows inkEnd: the first blank row after the
# closing stroke. Record that as the resume boundary, not the first ink.
a='''                        isolatedResumeY = ((inkEnd.toLong() * content.height + sh - 1) / sh).toInt()
                        continue'''
assert s.count(a)==1
s=s.replace(a,'''                        isolatedResumeY = ((inkEnd.toLong() * content.height + sh - 1) / sh).toInt()
                        passedLineEndY = isolatedResumeY
                        continue''',1)
# v0.38's FIRST_CONTENT shortcut is unsafe after PASSED: remove and
# instead resume the existing extended gutter loop beyond the whole band.
start=s.index('            if (afterIsolated) {\n                val resume = ')
end=s.index('            val edge = (h - from) * sh / span',start)
s=s[:start]+'''            val resumeRow = if (afterIsolated) {
                ((isolatedResumeY - from).toLong() * sh / span)
                    .toInt().coerceIn(0, sh)
            } else 0
'''+s[end:]
# Don't revisit the same gap that contains the discarded line; a valid
# next gutter must START strictly after the blank run following the line.
a='''                if ((!afterIsolated && start >= edge) || stop <= edge) {'''
assert s.count(a)==1
s=s.replace(a,'''                if ((afterIsolated && start <= resumeRow) ||
                    (!afterIsolated && (start >= edge || stop <= edge))) {''',1)
a='''                val landing = from + stop * span / sh'''
assert s.count(a)==1
s=s.replace(a,'''                val landing = from + stop * span / sh
                if (afterIsolated && landing <= isolatedResumeY) continue''',1)
a='''                extendedNotRun("available=" + (end - h) + "/" + maximum + " FOUND@" + landing)'''
assert s.count(a)==1
s=s.replace(a,'''                extendedNotRun("available=" + (end - h) + "/" + maximum +
                    (if (afterIsolated) " NEXT_GAP@" else " FOUND@") + landing)''',1)
# On no next gutter, use a conservative fallback: never allow a full-screen
# jump to cross unknown content after a passed closing stroke.
# This is applied in WebtoonViewer where the fallback is selected.
p.write_text(s.replace('"SCROLL DEBUG v0.43 | line context"','"SCROLL DEBUG v0.45 | after pass next gap"'))
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
a='''val distance = gutter ?: extended ?: recycler.height.coerceAtLeast(1)'''
assert s.count(a)==1
s=s.replace(a,'''val distance = gutter ?: extended ?: if (afterIsolated) {
                // No reliable next separator: don't skip unseen content.
                (recycler.height / 2).coerceAtLeast(1)
            } else recycler.height.coerceAtLeast(1)''',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 81")==1
p.write_text(s.replace("versionCode = 81","versionCode = 83",1))
print("v0.45 applied on v0.43: skip full band, next gap, conservative fallback")
