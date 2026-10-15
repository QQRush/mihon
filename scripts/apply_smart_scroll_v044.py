#!/usr/bin/env python3
"""v0.44: after PASSED, search next gap instead of first ink."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
start=s.index('            if (afterIsolated) {\n                val resume = ')
end=s.index('            val edge = (h - from) * sh / span',start)
s=s[:start]+'''            // v0.44: do not land at first ink after a passed closing
            // stroke. Resume the normal gap search beyond that stroke.
            val resumeRow = if (afterIsolated) {
                ((isolatedResumeY - from).toLong() * sh / span)
                    .toInt().coerceIn(0, sh)
            } else 0
'''+s[end:]
a='''                if ((!afterIsolated && start >= edge) || stop <= edge) {'''
assert s.count(a)==1
s=s.replace(a,'''                if ((afterIsolated && start < resumeRow) ||
                    (!afterIsolated && (start >= edge || stop <= edge))) {''',1)
# v0.37 has a second thin-stroke skipper in the extended scan;
# retain it, but avoid reselecting a line that was already passed.
a='''                if (afterIsolated) {
                    val lookahead = ((10L * sh + span - 1) / span).toInt().coerceAtLeast(1)'''
assert s.count(a)==1
s=s.replace(a,'''                if (afterIsolated) {
                    val lookahead = ((10L * sh + span - 1) / span).toInt().coerceAtLeast(1)''',1)
a='''                extendedNotRun("available=" + (end - h) + "/" + maximum + " FOUND@" + landing)'''
assert s.count(a)==1
s=s.replace(a,'''                extendedNotRun("available=" + (end - h) + "/" + maximum +
                    (if (afterIsolated) " NEXT_GAP@" else " FOUND@") + landing)''',1)
# Explicitly refuse to return the passed line itself.
a='''                val landing = from + stop * span / sh'''
assert s.count(a)==1
s=s.replace(a,'''                val landing = from + stop * span / sh
                if (afterIsolated && landing <= isolatedResumeY) continue''',1)
s=s.replace('"SCROLL DEBUG v0.43 | line context"','"SCROLL DEBUG v0.44 | next gap after pass"')
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 81")==1
p.write_text(s.replace("versionCode = 81","versionCode = 82",1))
print("v0.44: extended scan resumes after passed line and seeks next gap")
