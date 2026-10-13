#!/usr/bin/env python3
"""Diagnostic-only: v0.17r scrolling, log stable item coordinates before/after."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
old="""            val beforeOffset = recycler.computeVerticalScrollOffset()
            recycler.scrollBy(0, distance)
            val afterOffset = recycler.computeVerticalScrollOffset()
"""
new="""            val beforeOffset = recycler.computeVerticalScrollOffset()
            val anchorItem = beforeItem
            val anchorTop = layoutManager.findViewByPosition(anchorItem)?.top
            val nextTop = layoutManager.findViewByPosition(anchorItem + 1)?.top
            // Diagnostic ONLY: leave the v0.17r scroll command untouched.
            recycler.scrollBy(0, distance)
            val afterOffset = recycler.computeVerticalScrollOffset()
            val sameAnchorTop = layoutManager.findViewByPosition(anchorItem)?.top
            val afterFirst = layoutManager.findFirstVisibleItemPosition()
            val afterFirstTop = layoutManager.findViewByPosition(afterFirst)?.top
            android.util.Log.d("SmartScrollTrace", "immediate req=" + distance + " kind=" + (if (gutter != null) "GUTTER" else "FULL") + " before=" + anchorItem + "/" + anchorTop + " next=" + nextTop + " after=" + afterFirst + "/" + afterFirstTop + " anchorAfter=" + sameAnchorTop + " offset=" + beforeOffset + "->" + afterOffset)
            recycler.post {
                val postFirst = layoutManager.findFirstVisibleItemPosition()
                val postTop = layoutManager.findViewByPosition(postFirst)?.top
                val postAnchorTop = layoutManager.findViewByPosition(anchorItem)?.top
                android.util.Log.d("SmartScrollTrace", "postLayout req=" + distance + " first=" + postFirst + "/" + postTop + " anchor=" + anchorItem + "/" + postAnchorTop + " next=" + layoutManager.findViewByPosition(anchorItem + 1)?.top + " offset=" + recycler.computeVerticalScrollOffset())
            }
"""
if s.count(old)!=1:raise SystemExit("expected v0.17r scrolling anchor not found")
s=s.replace(old,new)
p.write_text(s)
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
if s.count("SCROLL DEBUG v0.17r | v0.16 navigation")!=1:raise SystemExit("debug label mismatch")
p.write_text(s.replace("SCROLL DEBUG v0.17r | v0.16 navigation","SCROLL DEBUG DIAG | v0.17r"))
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 52")!=1:raise SystemExit("version mismatch")
p.write_text(s.replace("versionCode = 52","versionCode = 54",1))
print("Diagnostic-only patch installed")
