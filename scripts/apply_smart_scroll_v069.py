#!/usr/bin/env python3
"""v0.69: Smart Scroll owns normal lookahead. Reuse v0.51 extended
PRESERVED search even without PASSED, but only for a gutter starting
within the viewport. Keep Smart Fit entirely independent."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
start=s.index('    fun extendedLanding(recycler:')
end=s.index('    override fun onDraw(canvas: Canvas)',start)
part=s[start:end]
a='''                if (afterIsolated && stop > resumeRow && stop < sh - 5) {'''
assert part.count(a)==1
part=part.replace(a,'''                if (stop > resumeRow && stop < sh - 5 &&
                    (afterIsolated || (start < edge && stop > edge))) {''',1)
a='''                            val landing = (top - 8).coerceAtLeast(isolatedResumeY + 1)'''
assert part.count(a)==1
part=part.replace(a,'''                            val landing = if (afterIsolated) {
                                (top - 8).coerceAtLeast(isolatedResumeY + 1)
                            } else (top - 8).coerceAtLeast(1)''',1)
# Ensure normal crossing case cannot return a border outside the search window.
s=s[:start]+part+s[end:]
assert s.count('"SCROLL DEBUG v0.68 | fit standby / super safe scroll"')==1
s=s.replace('"SCROLL DEBUG v0.68 | fit standby / super safe scroll"','"SCROLL DEBUG v0.69 | scroll preserved lookahead"',1)
p.write_text(s)
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
a='''            val distance = gutter ?: extended ?: if (afterIsolated) {
                // No reliable next separator: don't skip unseen content.
                (recycler.height / 2).coerceAtLeast(1)
            } else recycler.height.coerceAtLeast(1)'''
b='''            val distance = gutter ?: extended ?: if (afterIsolated) {
                // Keep the SUPER SAFE post-PASSED fallback.
                (recycler.height / 2).coerceAtLeast(1)
            } else {
                // No verified next start: do not blindly cross unseen ink.
                (recycler.height * 3 / 4).coerceAtLeast(1)
            }'''
assert s.count(a)==1
s=s.replace(a,b,1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 106")==1
p.write_text(s.replace("versionCode = 106","versionCode = 107",1))
print("v0.69 independent extended PRESERVED and conservative fallback")
