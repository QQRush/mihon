#!/usr/bin/env python3
"""v0.70 diagnostic-only: report FIRST rejected extended gutter and why.
Do not change scrolling decisions, Fit, or SUPER SAFE detection."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
start=s.index("    fun extendedLanding(recycler:")
end=s.index("    override fun onDraw(canvas: Canvas)",start)
part=s[start:end]
a='''            var reason = "NO_GAP"'''
assert part.count(a)==1
part=part.replace(a,'''            var reason = "NO_GAP"
            var firstRejected = "NONE"
            fun rejectOnce(why: String, start: Int, stop: Int) {
                if (firstRejected == "NONE") {
                    firstRejected = why + "@" + (from + start * span / sh) +
                        "-" + (from + stop * span / sh)
                }
            }''',1)
a='''                    reason = "NOT_CROSSING"'''
assert part.count(a)==1
part=part.replace(a,'''                    reason = "NOT_CROSSING"
                    rejectOnce("NOT_CROSSING", start, stop)''',1)
a='''                    reason = "NO_CONTENT_AFTER"'''
assert part.count(a)>=1
part=part.replace(a,'''                    reason = "NO_CONTENT_AFTER"
                    rejectOnce("NO_CONTENT_AFTER", start, stop)''')
a='''                    reason = "GAP_TOO_SHORT"'''
assert part.count(a)==1
part=part.replace(a,'''                    reason = "GAP_TOO_SHORT"
                    rejectOnce("GAP_TOO_SHORT", start, stop)''',1)
a='''                    reason = "NO_CONTENT_BEFORE"'''
assert part.count(a)==1
part=part.replace(a,'''                    reason = "NO_CONTENT_BEFORE"
                    rejectOnce("NO_CONTENT_BEFORE", start, stop)''',1)
a='''                    reason = "SHORT_GAP"'''
assert part.count(a)==1
part=part.replace(a,'''                    reason = "SHORT_GAP"
                    rejectOnce("SHORT_GAP", start, stop)''',1)
a='''            extendedNotRun("available=" + (end - h) + "/" + maximum + " " +
                reason + (if (afterIsolated) " REJECTED_SHORT=" + postPassRejected else ""))'''
assert part.count(a)==1
part=part.replace(a,'''            extendedNotRun("available=" + (end - h) + "/" + maximum + " " +
                reason + " FIRST=" + firstRejected +
                (if (afterIsolated) " REJECTED_SHORT=" + postPassRejected else ""))''',1)
s=s[:start]+part+s[end:]
a='"SCROLL DEBUG v0.69 | scroll preserved lookahead"'
assert s.count(a)==1
s=s.replace(a,'"SCROLL DEBUG v0.70 | first rejected gap diagnostic"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 107")==1
p.write_text(s.replace("versionCode = 107","versionCode = 108",1))
print("v0.70 diagnostic only: first rejected gap and reason")
