#!/usr/bin/env python3
"""v0.34: remove refinement entirely; ceil coarse gutter-to-screen conversion."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
start=s.index('    private var refinementDebug = "REFINE: WAIT"')
end=s.index("    override fun onDraw(canvas: Canvas)",start)
assert "fun refineGutterLanding(" in s[start:end]
s=s[:start]+s[end:]
assert s.count('            refinementDebug,')==1
s=s.replace('            refinementDebug,\n','',1)
assert s.count("val landing = end * content.height / sh")==1
s=s.replace("val landing = end * content.height / sh","val landing = ((end.toLong() * content.height + sh - 1) / sh).toInt()",1)
assert s.count('"SCROLL DEBUG v0.33 | seam refinement"')==1
s=s.replace('"SCROLL DEBUG v0.33 | seam refinement"','"SCROLL DEBUG v0.34 | ceil landing"',1)
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
a="""val distance = if (gutter != null) {
                debugOverlay.refineGutterLanding(recycler, gutter)
            } else {
                extended ?: recycler.height.coerceAtLeast(1)
            }"""
assert s.count(a)==1
s=s.replace(a,"val distance = gutter ?: extended ?: recycler.height.coerceAtLeast(1)",1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 71")==1
p.write_text(s.replace("versionCode = 71","versionCode = 72",1))
print("v0.34: removed refine; ceil current gutter landing")
