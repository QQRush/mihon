#!/usr/bin/env python3
"""v0.49: post-PASSED scan starts at rejected stroke; keep existing debug."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
anchor=s.index("fun extendedLanding(")
start=s.index("        val from = ",anchor)
finish=s.index("\n",start)
s=s[:start]+"""        // Begin at the rejected stroke rather than an arbitrary screen fraction.
        val from = if (afterIsolated) (isolatedResumeY - 8).coerceIn(0, h * 65 / 100)
            else h * 65 / 100"""+s[finish:]
a="        val limit = h + h * (if (afterIsolated) 50 else 35) / 100"
assert s.count(a)==1
s=s.replace(a,"        val limit = h + h * (if (afterIsolated) 100 else 35) / 100",1)
a='''                extendedNotRun("available=" + (end - h) + "/" + maximum +
                    (if (afterIsolated) " NEXT_GAP@" else " FOUND@") + landing)'''
assert s.count(a)==1
s=s.replace(a,'''                extendedNotRun("available=" + (end - h) + "/" + maximum +
                    (if (afterIsolated) " PASS_END@" + isolatedResumeY +
                        " GAP_START@" + (from + start * span / sh) +
                        " GAP_END@" else " FOUND@") + landing)''',1)
assert s.count('"SCROLL DEBUG v0.48 | earliest post-pass gap"')==1
s=s.replace('"SCROLL DEBUG v0.48 | earliest post-pass gap"','"SCROLL DEBUG v0.49 | pass gap landing"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 86")==1
p.write_text(s.replace("versionCode = 86","versionCode = 87",1))
print("v0.49 post-pass scan and debug applied")
