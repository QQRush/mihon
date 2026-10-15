#!/usr/bin/env python3
"""v0.47: land at the END of the first valid blank interval after PASSED.
Keep v0.46 debug, stroke classification and all navigation safeguards."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
old='''                if ((afterIsolated && start <= resumeRow) ||
                    (!afterIsolated && (start >= edge || stop <= edge))) {'''
new='''                // The blank interval immediately following a PASSED stroke
                // can START before resumeRow (sampling/rounding). Do not
                // discard it: stop is the start of the next visible content.
                if ((afterIsolated && stop <= resumeRow) ||
                    (!afterIsolated && (start >= edge || stop <= edge))) {'''
assert s.count(old)==1
s=s.replace(old,new,1)
assert s.count('"SCROLL DEBUG v0.46 | border-band recovery"')==1
s=s.replace('"SCROLL DEBUG v0.46 | border-band recovery"','"SCROLL DEBUG v0.47 | first gap after pass"',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 84")==1
p.write_text(s.replace("versionCode = 84","versionCode = 85",1))
print("v0.47: first valid gap after PASSED, land at gap end")
