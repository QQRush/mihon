#!/usr/bin/env python3
"""v0.59: after Smart Fit, align to the next visible content.
Reuse existing firstContentAfterBoundary scanner (v0.18); only for fit->next.
Do not change normal Smart Scroll, Smart Fit, or its source coordinates."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt")
s=p.read_text()
a='''            try { recycler.scrollBy(0, distance) } finally { fitting = false }
            updateSmartScrollDebug()
            applyFitIfEligible()
            return'''
b='''            try {
                recycler.scrollBy(0, distance)
                // The fitted artwork ends at the START of a blank gutter.
                // The old fitEnd jump may land inside that gutter. Reuse the
                // existing content-alignment scanner instead of a second
                // separator detector. This only runs after a fitted page.
                val nextContent = debugOverlay.firstContentAfterBoundary(recycler, 0)
                if (nextContent > 0) recycler.scrollBy(0, nextContent)
            } finally { fitting = false }
            updateSmartScrollDebug()
            applyFitIfEligible()
            return'''
assert s.count(a)==1, "fit next anchor mismatch"
s=s.replace(a,b,1)
p.write_text(s)
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
# v0.20 removed the old boundary helper. Restore it from v0.18's
# original patch source (same scanner, no newly invented detector).
if "fun firstContentAfterBoundary(content: View, boundary: Int): Int" not in s:
    old_patch = Path("scripts/apply_smart_scroll_v018.py").read_text()
    begin = old_patch.index("    fun firstContentAfterBoundary(content: View, boundary: Int): Int")
    finish = old_patch.index('\\n\\n"""+s[b:]', begin)
    helper = old_patch[begin:finish]
    marker = "    override fun onDraw(canvas: Canvas) {"
    assert s.count(marker)==1
    s=s.replace(marker,helper+"\\n\\n"+marker,1)
assert s.count('"SCROLL DEBUG v0.58 | gap-start fit"')==1
s=s.replace('"SCROLL DEBUG v0.58 | gap-start fit"','"SCROLL DEBUG v0.59 | fit next aligned"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 96")==1
p.write_text(s.replace("versionCode = 96","versionCode = 97",1))
print("v0.59 post-fit Next alignment using existing scanner")
