#!/usr/bin/env python3
"""v0.20D2: diagnose WHY offset scan returns null. Navigation unchanged."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
old="""        if (item.width < 2 || item.height < 2 || offset < 0 || offset >= item.height) return null
        val length = minOf(scanLength, item.height - offset)
        if (length < 60) return null
"""
new="""        if (item.width < 2 || item.height < 2 || offset < 0 || offset >= item.height) {
            android.util.Log.d("SmartScrollScan", "reject=BOUNDS width=" + item.width + " height=" + item.height + " offset=" + offset)
            return null
        }
        val length = minOf(scanLength, item.height - offset)
        if (length < 60) {
            android.util.Log.d("SmartScrollScan", "reject=SHORT length=" + length)
            return null
        }
"""
if s.count(old)!=1:raise SystemExit("bounds anchor changed")
s=s.replace(old,new)
old="""            if (!blank(0) || !blank(1)) return null
            var y = 0
            while (y < sh && blank(y)) y++
            if (y >= sh || y < 3) return null
            if (y + 2 >= sh || blank(y + 1) || blank(y + 2)) return null
            return offset + (y.toLong() * length / sh).toInt()
"""
new="""            val first = (0 until minOf(sh, 32)).joinToString("") { if (blank(it)) "W" else "C" }
            val b0 = blank(0)
            val b1 = blank(1)
            if (!b0 || !b1) {
                android.util.Log.d("SmartScrollScan", "reject=START_CONTENT offset=" + offset + " length=" + length + " rows=" + sh + " pattern=" + first)
                return null
            }
            var y = 0
            while (y < sh && blank(y)) y++
            if (y >= sh || y < 3) {
                android.util.Log.d("SmartScrollScan", "reject=" + (if (y >= sh) "ALL_BLANK" else "SHORT_GAP") + " offset=" + offset + " firstContentRow=" + y + " rows=" + sh + " pattern=" + first)
                return null
            }
            if (y + 2 >= sh || blank(y + 1) || blank(y + 2)) {
                android.util.Log.d("SmartScrollScan", "reject=UNSTABLE_CONTENT offset=" + offset + " firstContentRow=" + y + " rows=" + sh + " pattern=" + first)
                return null
            }
            val landing = offset + (y.toLong() * length / sh).toInt()
            android.util.Log.d("SmartScrollScan", "accept offset=" + offset + " gapRows=" + y + " landing=" + landing + " length=" + length + " pattern=" + first)
            return landing
"""
if s.count(old)!=1:raise SystemExit("scan anchor changed")
s=s.replace(old,new)
s=s.replace("SCROLL DEBUG v0.20D | target trace","SCROLL DEBUG v0.20D2 | scan reasons")
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 57")!=1:raise SystemExit("version mismatch")
p.write_text(s.replace("versionCode = 57","versionCode = 58",1))
print("v0.20D2 detailed scan rejection diagnostics installed; no navigation changes")
