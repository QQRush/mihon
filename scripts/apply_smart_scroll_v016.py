#!/usr/bin/env python3
"""v0.16: honor gaps crossing the 65% boundary and measure actual scroll."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
old="""            val firstRow = sh * 65 / 100
            var row = firstRow
"""
new="""            val firstRow = sh * 65 / 100
            // Scan from the beginning so a gap starting BEFORE the last 35%
            // is not accidentally ignored when its end falls inside it.
            var row = 0
"""
if s.count(old)!=1:raise SystemExit("scan anchor mismatch")
s=s.replace(old,new)
old="if (start <= firstRow || end >= sh - 3 || (end - start) * content.height / sh < 50) continue"
new="if (end <= firstRow || end >= sh - 3 || (end - start) * content.height / sh < 50) continue"
if s.count(old)!=1:raise SystemExit("boundary anchor mismatch")
s=s.replace(old,new)
s=s.replace("SCROLL DEBUG v0.15 | bottom 35%","SCROLL DEBUG v0.16 | gap landing")
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
old="""            val beforeItem = layoutManager.findFirstVisibleItemPosition()
            val beforeTop = layoutManager.findViewByPosition(beforeItem)?.top ?: 0
            recycler.scrollBy(0, distance)
            val afterItem = layoutManager.findFirstVisibleItemPosition()
            val afterTop = layoutManager.findViewByPosition(afterItem)?.top ?: 0
"""
new="""            val beforeItem = layoutManager.findFirstVisibleItemPosition()
            val beforeTop = layoutManager.findViewByPosition(beforeItem)?.top ?: 0
            val beforeOffset = recycler.computeVerticalScrollOffset()
            recycler.scrollBy(0, distance)
            val afterOffset = recycler.computeVerticalScrollOffset()
            val afterItem = layoutManager.findFirstVisibleItemPosition()
            val afterTop = layoutManager.findViewByPosition(afterItem)?.top ?: 0
"""
if s.count(old)!=1:raise SystemExit("scroll anchor mismatch")
s=s.replace(old,new)
old="val measured = if (beforeItem == afterItem) beforeTop - afterTop else 0"
new="val measured = afterOffset - beforeOffset"
if s.count(old)!=1:raise SystemExit("measurement anchor mismatch")
s=s.replace(old,new)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 48")!=1:raise SystemExit("versionCode mismatch")
p.write_text(s.replace("versionCode = 48","versionCode = 49",1))
print("v0.16 boundary and measurement fix installed")
