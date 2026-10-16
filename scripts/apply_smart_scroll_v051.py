#!/usr/bin/env python3
"""v0.51: keep v0.50; after PASSED recognize the same isolated opening
stroke that normal scanning preserves, instead of requiring a 50px gutter."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
start=s.index('    fun extendedLanding(recycler:')
end=s.index('    override fun onDraw(canvas: Canvas)',start)
part=s[start:end]
a='''                val stop = y'''
assert part.count(a)==1
part=part.replace(a,'''                val stop = y
                // Same mechanical idea as normal PRESERVED: a short ink
                // stroke after clear space can be the beginning of a balloon.
                // Only active AFTER a passed closing stroke. No shape test.
                if (afterIsolated && stop > resumeRow && stop < sh - 5) {
                    val maxStrokeRows = ((12L * sh + span - 1) / span).toInt().coerceAtLeast(1)
                    var strokeEnd = stop
                    while (strokeEnd < sh && !blank[strokeEnd] &&
                        strokeEnd - stop <= maxStrokeRows) strokeEnd++
                    if (strokeEnd > stop && strokeEnd - stop <= maxStrokeRows &&
                        strokeEnd < sh && blank[strokeEnd]) {
                        val contextRows = ((110L * sh + span - 1) / span).toInt().coerceAtLeast(1)
                        var inkAbove = 0
                        for (cy in (stop - contextRows).coerceAtLeast(0) until stop) {
                            var ink = 0
                            for (cx in 5 until 91) {
                                val c = pixels[cy * sw + cx]
                                if (Color.red(c) < 170 && Color.green(c) < 170 &&
                                    Color.blue(c) < 170) ink++
                            }
                            if (ink >= 5) inkAbove++
                        }
                        if (inkAbove < 2) {
                            val top = from + stop * span / sh
                            val landing = (top - 8).coerceAtLeast(isolatedResumeY + 1)
                            postPassLandingY = landing
                            extendedNotRun("available=" + (end - h) + "/" + maximum +
                                " PRESERVED@" + top + " LANDING@" + landing +
                                " REJECTED_SHORT=" + postPassRejected)
                            return landing
                        }
                    }
                }''',1)
s=s[:start]+part+s[end:]
assert s.count('"SCROLL DEBUG v0.50 | post-pass content guard"')==1
s=s.replace('"SCROLL DEBUG v0.50 | post-pass content guard"','"SCROLL DEBUG v0.51 | post-pass preserved top"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 88")==1
p.write_text(s.replace("versionCode = 88","versionCode = 89",1))
print("v0.51 extended isolated opening stroke detection applied")
