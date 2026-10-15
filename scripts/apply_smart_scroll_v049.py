#!/usr/bin/env python3
"""v0.49: search directly after PASSED across attached content; keep visual debug."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='''        val from = h * 65 / 100'''
if s.count(a) != 1:
    # Earlier revisions may have adjusted the scan origin.
    import re
    m = re.search(r'^        val from = .*, start immediately after the rejected border, not
        // at the arbitrary last 35% of the viewport.
        val from = if (afterIsolated) (isolatedResumeY - 8).coerceIn(0, h * 65 / 100)
            else h * 65 / 100''',1)
a='''        val limit = h + h * (if (afterIsolated) 50 else 35) / 100'''
assert s.count(a)==1
s=s.replace(a,'''        // A wide white interval may end far beyond the screen edge.
        val limit = h + h * (if (afterIsolated) 100 else 35) / 100''',1)
a='''                if ((afterIsolated && stop <= resumeRow) ||
                    (!afterIsolated && (start >= edge || stop <= edge))) {'''
assert s.count(a)==1
s=s.replace(a,'''                if ((afterIsolated && stop <= resumeRow) ||
                    (!afterIsolated && (start >= edge || stop <= edge))) {''',1)
a='''                extendedNotRun("available=" + (end - h) + "/" + maximum +
                    (if (afterIsolated) " NEXT_GAP@" else " FOUND@") + landing)'''
assert s.count(a)==1
s=s.replace(a,'''                extendedNotRun("available=" + (end - h) + "/" + maximum +
                    (if (afterIsolated) " PASS_END@" + isolatedResumeY +
                        " GAP_START@" + (from + start * span / sh) +
                        " GAP_END@" + landing else " FOUND@") + landing)''',1)
assert s.count('"SCROLL DEBUG v0.48 | earliest post-pass gap"')==1
s=s.replace('"SCROLL DEBUG v0.48 | earliest post-pass gap"','"SCROLL DEBUG v0.49 | pass gap landing"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 86")==1
p.write_text(s.replace("versionCode = 86","versionCode = 87",1))
print("v0.49 post-pass scan origin and range, first gap diagnostics")
, s, re.MULTILINE)
    assert m, "Missing scan origin"
    a = m.group(0)
s=s.replace(a,'''        // After PASSED, start immediately after the rejected border, not
        // at the arbitrary last 35% of the viewport.
        val from = if (afterIsolated) (isolatedResumeY - 8).coerceIn(0, h * 65 / 100)
            else h * 65 / 100''',1)
a='''        val limit = h + h * (if (afterIsolated) 50 else 35) / 100'''
assert s.count(a)==1
s=s.replace(a,'''        // A wide white interval may end far beyond the screen edge.
        val limit = h + h * (if (afterIsolated) 100 else 35) / 100''',1)
a='''                if ((afterIsolated && stop <= resumeRow) ||
                    (!afterIsolated && (start >= edge || stop <= edge))) {'''
assert s.count(a)==1
s=s.replace(a,'''                if ((afterIsolated && stop <= resumeRow) ||
                    (!afterIsolated && (start >= edge || stop <= edge))) {''',1)
a='''                extendedNotRun("available=" + (end - h) + "/" + maximum +
                    (if (afterIsolated) " NEXT_GAP@" else " FOUND@") + landing)'''
assert s.count(a)==1
s=s.replace(a,'''                extendedNotRun("available=" + (end - h) + "/" + maximum +
                    (if (afterIsolated) " PASS_END@" + isolatedResumeY +
                        " GAP_START@" + (from + start * span / sh) +
                        " GAP_END@" + landing else " FOUND@") + landing)''',1)
assert s.count('"SCROLL DEBUG v0.48 | earliest post-pass gap"')==1
s=s.replace('"SCROLL DEBUG v0.48 | earliest post-pass gap"','"SCROLL DEBUG v0.49 | pass gap landing"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 86")==1
p.write_text(s.replace("versionCode = 86","versionCode = 87",1))
print("v0.49 post-pass scan origin and range, first gap diagnostics")
