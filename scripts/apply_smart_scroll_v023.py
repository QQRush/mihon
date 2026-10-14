from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
a="        candidates = probe(content)\n        invalidate()"
b="        candidates = probe(content)\n        // Preview the same detector used for navigation, only in debug.\n        if (visibility == VISIBLE) nextContentAlignedDistance(content, content.height)\n        invalidate()"
assert s.count(a)==1;s=s.replace(a,b)
a="""        val lineY = step.toFloat().coerceIn(0f, h - 4f)
        paint.strokeWidth = 2f * resources.displayMetrics.density
        paint.color = Color.RED
        canvas.drawLine(0f, lineY, w, lineY, paint)
        paint.color = Color.BLUE
        canvas.drawLine(0f, (h - lineY).coerceAtLeast(0f), w, (h - lineY).coerceAtLeast(0f), paint)
        paint.color = Color.GREEN"""
b="""        paint.strokeWidth = 2f * resources.displayMetrics.density
        paint.color = Color.RED
        canvas.drawLine(0f, h * 0.65f, w, h * 0.65f, paint)
        paint.color = Color.BLUE
        if (chosenLandingY in 0 until height) {
            val landing = chosenLandingY.toFloat()
            canvas.drawLine(0f, landing, w, landing, paint)
        }
        paint.color = Color.GREEN"""
assert s.count(a)==1;s=s.replace(a,b)
s=s.replace("SCROLL DEBUG v0.22 | top trim","SCROLL DEBUG v0.23 | red=scan blue=landing")
p.write_text(s)
p=Path("app/build.gradle.kts");s=p.read_text();assert s.count("versionCode = 60")==1;p.write_text(s.replace("versionCode = 60","versionCode = 61",1))
print("v0.23 debug-only line semantics")
