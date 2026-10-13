#!/usr/bin/env python3
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
old="""        paint.color = Color.BLACK
        canvas.drawRect(0f, 0f, w, (lines.size * 18f + 8f) * density, paint)
        paint.color = Color.WHITE"""
new="""        paint.color = Color.argb(128, 0, 0, 0)
        canvas.drawRect(0f, 0f, w, (lines.size * 18f + 8f) * density, paint)
        paint.color = Color.WHITE"""
if s.count(old)!=1: raise SystemExit("Debug header anchor changed")
p.write_text(s.replace(old,new))
print("Debug background set to 50 percent opacity")
