#!/usr/bin/env python3
"""v0.50: after PASSED, reject tiny false gutters and preserve next content start.
The normal v0.43 PRESERVED/PASSED classification is untouched."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='    private var passedLineEndY = -1'
assert s.count(a)==1
s=s.replace(a,a+'\n    private var postPassLandingY = -1\n    private var postPassRejected = 0',1)
a='        passedLineEndY = -1'
assert s.count(a)==1
s=s.replace(a,a+'\n        postPassLandingY = -1\n        postPassRejected = 0',1)
# Keep the normal scan untouched. Only change the extended scan following PASSED.
start=s.index('    fun extendedLanding(recycler:')
end=s.index('    override fun onDraw(canvas: Canvas)',start)
part=s[start:end]
a='''                if (!afterIsolated && (stop - start) * span / sh < 50) {'''
assert part.count(a)==1
part=part.replace(a,'''                // A 7px gap inside a drawing is not a safe landing.
                // Require the same meaningful blank band after PASSED.
                if ((stop - start) * span / sh < 50) {
                    if (afterIsolated) {
                        postPassRejected++
                        reason = "SHORT_GAP"
                    }''',1)
a='''                val landing = from + stop * span / sh
                if (afterIsolated && landing <= isolatedResumeY) continue'''
assert part.count(a)==1
part=part.replace(a,'''                val landing = from + stop * span / sh
                if (afterIsolated && landing <= isolatedResumeY) continue
                if (afterIsolated) {
                    // The first nonblank row after a substantial gutter is
                    // the start of new content, including a thin balloon top.
                    // Never land beyond it.
                    postPassLandingY = landing
                    isolatedLineDebug = "LINE: PASSED -> NEXT_START@" + landing +
                        " REJECTED_SHORT=" + postPassRejected
                }''',1)
a='''                        " GAP_END@" else " FOUND@") + landing)'''
assert part.count(a)==1
part=part.replace(a,'''                        " GAP_END@" else " FOUND@") + landing +
                    (if (afterIsolated) " REJECTED_SHORT=" + postPassRejected else ""))''',1)
# Distinguish a failed search, do not imply an unsafe landing.
a='''            extendedNotRun("available=" + (end - h) + "/" + maximum + " " + reason)'''
assert part.count(a)==1
part=part.replace(a,'''            extendedNotRun("available=" + (end - h) + "/" + maximum + " " +
                reason + (if (afterIsolated) " REJECTED_SHORT=" + postPassRejected else ""))''',1)
s=s[:start]+part+s[end:]
# On-image marker for accepted post-pass landing.
a='''        paint.color = Color.MAGENTA
        if (lineMarkerY in 0 until height) {'''
assert s.count(a)==1
s=s.replace(a,'''        paint.color = Color.YELLOW
        if (postPassLandingY in 0 until height) {
            val y = postPassLandingY.toFloat()
            canvas.drawLine(0f, y, w, y, paint)
            canvas.drawText("NEXT CONTENT START", 8f, y - 7f, paint)
        }
        paint.color = Color.MAGENTA
        if (lineMarkerY in 0 until height) {''',1)
assert s.count('"SCROLL DEBUG v0.49 | pass gap landing"')==1
s=s.replace('"SCROLL DEBUG v0.49 | pass gap landing"','"SCROLL DEBUG v0.50 | post-pass content guard"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 87")==1
p.write_text(s.replace("versionCode = 87","versionCode = 88",1))
print("v0.50 post-PASSED content guard")
