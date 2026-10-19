#!/usr/bin/env python3
"""v0.74: remove only the intentional 8px pre-ink padding after FIT ART."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='''            // 8px breathing room ABOVE the first stroke; never below it.
            return ((firstInk.toLong() * h / sh).toInt() - 8).coerceAtLeast(0)'''
b='''            // Land exactly on the first detected ink; no intentional top padding.
            return (firstInk.toLong() * h / sh).toInt().coerceAtLeast(0)'''
assert s.count(a)==1
s=s.replace(a,b,1)
a='"SCROLL DEBUG v0.73 | first ink after fit"'
assert s.count(a)==1
p.write_text(s.replace(a,'"SCROLL DEBUG v0.74 | first ink no padding"',1))
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 111")==1
p.write_text(s.replace("versionCode = 111","versionCode = 112",1))
print("v0.74 remove 8px only")
