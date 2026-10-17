#!/usr/bin/env python3
"""v0.64: conservative overlap only when neither current nor extended
scanner has a safe landing. Keep v0.51 PASSED/PRESERVED and v0.63 Fit."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
a='''            val distance = gutter ?: extended ?: if (afterIsolated) {
                // No reliable next separator: don't skip unseen content.
                (recycler.height / 2).coerceAtLeast(1)
            } else recycler.height.coerceAtLeast(1)'''
b='''            val distance = gutter ?: extended ?: if (afterIsolated) {
                // Keep the established conservative post-PASSED behavior.
                (recycler.height / 2).coerceAtLeast(1)
            } else {
                // No detected landing: a full viewport can cut a balloon
                // beginning near the lower edge. Keep 25% visible overlap.
                (recycler.height * 3 / 4).coerceAtLeast(1)
            }'''
assert s.count(a)==1, "fallback selection anchor changed"
s=s.replace(a,b,1)
a='''else if (extended != null) "EXTENDED@" + extended else "FALLBACK")'''
b='''else if (extended != null) "EXTENDED@" + extended
                    else if (afterIsolated) "FALLBACK_POST_PASS_50%"
                    else "FALLBACK_OVERLAP_75%")'''
assert s.count(a)==1
s=s.replace(a,b,1)
p.write_text(s)
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a='"SCROLL DEBUG v0.63 | visible gap standby"'
assert s.count(a)==1
s=s.replace(a,'"SCROLL DEBUG v0.64 | safe fallback overlap"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 101")==1
p.write_text(s.replace("versionCode = 101","versionCode = 102",1))
print("v0.64 conservative 75% fallback; all detected landings unchanged")
