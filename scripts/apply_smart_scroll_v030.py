#!/usr/bin/env python3
"""v0.30: advance one extra pixel only for visible gutters at 99–100%."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
old="val distance = gutter ?: extended ?: recycler.height.coerceAtLeast(1)"
assert s.count(old)==1
new="""val distance = if (gutter != null && gutter >= recycler.height * 99 / 100 &&
                gutter <= recycler.height) {
                gutter + 1
            } else {
                gutter ?: extended ?: recycler.height.coerceAtLeast(1)
            }"""
s=s.replace(old,new,1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 67")==1
p.write_text(s.replace("versionCode = 67","versionCode = 68",1))
print("v0.30: +1px only at 99-100% visible gutter")
