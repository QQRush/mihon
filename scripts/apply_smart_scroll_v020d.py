#!/usr/bin/env python3
"""v0.20 diagnostic: log offset, detected next-content coordinate and target.
No change to the actual scrolling decision or bitmap detector.
"""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"WebtoonViewer.kt"
s=p.read_text()
old="""                val nextContent = debugOverlay.contentAfterOffset(nextView, offset, recycler.height)
                nextContent?.let { nextTop + it }
"""
new="""                val nextContent = debugOverlay.contentAfterOffset(nextView, offset, recycler.height)
                val target = nextContent?.let { nextTop + it }
                android.util.Log.d("SmartScrollTrace", "boundary proposed=" + proposed +
                    " nextTop=" + nextTop + " offset=" + offset +
                    " nextContent=" + nextContent + " target=" + target +
                    " scanLength=" + recycler.height + " nextHeight=" + nextView.height)
                target
"""
if s.count(old)!=1:raise SystemExit("v0.20 target anchor mismatch")
s=s.replace(old,new)
old2="""            val distance = boundaryTarget ?: proposed
            val origin = currentSmartPosition()
"""
new2="""            val distance = boundaryTarget ?: proposed
            android.util.Log.d("SmartScrollTrace", "choice proposed=" + proposed +
                " boundaryTarget=" + boundaryTarget + " distance=" + distance +
                " firstItem=" + firstItem + " nextTop=" + nextTop +
                " gutter=" + gutter)
            val origin = currentSmartPosition()
"""
if s.count(old2)!=1:raise SystemExit("choice anchor mismatch")
s=s.replace(old2,new2)
p.write_text(s)
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
s=s.replace("SCROLL DEBUG v0.20 | offset scan","SCROLL DEBUG v0.20D | target trace")
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 56")!=1:raise SystemExit("version mismatch")
p.write_text(s.replace("versionCode = 56","versionCode = 57",1))
print("v0.20 diagnostic trace applied; navigation unchanged")
