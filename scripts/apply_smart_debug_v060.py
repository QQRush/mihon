#!/usr/bin/env python3
"""v0.60: movement diagnostics only. No changes to detection or navigation."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
anchor='    private var extendedDebug = "EXT: WAIT"'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
    private var navigationTrace = "NAV: WAIT"
    fun recordNavigationTrace(trace: String) {
        navigationTrace = "NAV: " + trace
        invalidate()
    }
''',1)
anchor='            extendedDebug,'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n            navigationTrace,',1)
assert s.count('"SCROLL DEBUG v0.59 | fit next aligned"')==1
s=s.replace('"SCROLL DEBUG v0.59 | fit next aligned"','"SCROLL DEBUG v0.60 | navigation trace"',1)
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
anchor='''            debugOverlay.recordJump('''
assert s.count(anchor)==1
s=s.replace(anchor,'''            // Snapshot the actual chosen route; debug overlay's live detector
            // can be recomputed after scroll and otherwise mislead analysis.
            debugOverlay.recordNavigationTrace(
                "NORMAL chosen=" + (if (gutter != null) "CURRENT@" + gutter
                    else if (extended != null) "EXTENDED@" + extended else "FALLBACK") +
                    " req=" + distance + " actual=" + (afterOffset - beforeOffset) +
                    " before=" + beforeOffset + " after=" + afterOffset
            )
'''+anchor,1)
anchor='''                if (nextContent > 0) recycler.scrollBy(0, nextContent)
            } finally { fitting = false }'''
assert s.count(anchor)==1
s=s.replace(anchor,'''                if (nextContent > 0) recycler.scrollBy(0, nextContent)
                debugOverlay.recordNavigationTrace(
                    "FIT_NEXT probeEnd=" + distance + " align=" + nextContent +
                        " totalReq=" + (distance + nextContent) +
                        " scrollY=" + recycler.computeVerticalScrollOffset()
                )
            } finally { fitting = false }''',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 97")==1
p.write_text(s.replace("versionCode = 97","versionCode = 98",1))
print("v0.60 navigation trace only; movement logic untouched")
