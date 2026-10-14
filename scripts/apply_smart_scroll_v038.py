#!/usr/bin/env python3
"""v0.38: after isolated line, land on first ink (not another gutter);
preserve connected rectangular borders, reuse existing bitmap samples."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
a='    private var isolatedCandidateRejected = false'
assert s.count(a)==1
s=s.replace(a,a+'''
    private var isolatedResumeY = -1
    private var firstContentDebug = "FIRST_CONTENT: NONE"''')
a='        isolatedCandidateRejected = false'
assert s.count(a)==1
s=s.replace(a,a+'''
        isolatedResumeY = -1
        firstContentDebug = "FIRST_CONTENT: NONE"''')
# Thin horizontal lines may be the top of a rectangular balloon. If ink at
# the same two horizontal positions persists below, retain the top border.
a='''                if (inkEnd > end && inkEnd - end < lookahead && inkEnd < sh && blank[inkEnd]) {'''
assert s.count(a)==1
b='''                var connected = false
                if (inkEnd > end && inkEnd < sh) {
                    val edgeRows = (inkEnd + 1 until minOf(sh, inkEnd + lookahead + 2))
                    var persistentColumns = 0
                    for (x in 5 until 91) {
                        val top = pixels[end * sw + x]
                        val topInk = Color.red(top) < 180 || Color.green(top) < 180 || Color.blue(top) < 180
                        if (!topInk) continue
                        if (edgeRows.any { y ->
                                val c = pixels[y * sw + x]
                                Color.red(c) < 180 || Color.green(c) < 180 || Color.blue(c) < 180
                            }) persistentColumns++
                        if (persistentColumns >= 2) { connected = true; break }
                    }
                }
                if (!connected && inkEnd > end && inkEnd - end < lookahead && inkEnd < sh && blank[inkEnd]) {'''
s=s.replace(a,b,1)
a='                    isolatedCandidateRejected = true'
assert s.count(a)==1
s=s.replace(a,a+'''
                    isolatedResumeY = ((inkEnd.toLong() * content.height + sh - 1) / sh).toInt()''')
# In extended bitmap, do not search another gap: find first nonblank
# AFTER the discarded border and its following blank run.
a='''            val edge = (h - from) * sh / span'''
assert s.count(a)==1
s=s.replace(a,'''            if (afterIsolated) {
                val resume = ((isolatedResumeY - from).toLong() * sh / span).toInt().coerceIn(0, sh)
                var y = resume
                // Resume only after the rejected stroke, never at its start.
                while (y < sh && blank[y]) y++
                if (y < sh) {
                    val landing = from + ((y.toLong() * span + sh - 1) / sh).toInt()
                    firstContentDebug = "FIRST_CONTENT@" + landing
                    extendedNotRun("FIRST_CONTENT@" + landing)
                    return landing
                }
                firstContentDebug = "FIRST_CONTENT: NONE"
                extendedNotRun("FIRST_CONTENT_NOT_FOUND")
                return null
            }
            val edge = (h - from) * sh / span''',1)
a='            isolatedLineDebug,'
assert s.count(a)==1
s=s.replace(a,a+'\n            firstContentDebug,')
assert s.count('"SCROLL DEBUG v0.37 | isolated + 50% search"')==1
s=s.replace('"SCROLL DEBUG v0.37 | isolated + 50% search"','"SCROLL DEBUG v0.38 | first content after skip"')
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 75")==1
p.write_text(s.replace("versionCode = 75","versionCode = 76",1))
print("v0.38: first ink after skip; protect connected rectangle outlines")
