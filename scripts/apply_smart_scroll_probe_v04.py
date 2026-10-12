#!/usr/bin/env python3
"""Harden the v0.3 separator probe against inter-line whitespace."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/SmartScrollDebugOverlay.kt")
s=p.read_text()
replacements=[
('val sampleHeight = (content.height / 8).coerceIn(32, 240)','val sampleHeight = (content.height / 4).coerceIn(64, 480)'),
('if (end - start >= 3 && start > 8 && end < sampleHeight - 4) {',
 '''// A gutter must be at least 60 physical pixels tall.
                    // This rejects most gaps between lines of dialogue.
                    val gutterPixels = (end - start) * content.height / sampleHeight
                    if (gutterPixels >= 60 && start > 8 && end < sampleHeight - 4) {'''),
('val center = (start + end) / 2','val center = (start + end) / 2'),
('"SCROLL DEBUG v0.3 | visible viewport only"','"SCROLL DEBUG v0.4 | min gutter 60px"'),
]
for old,new in replacements:
    if s.count(old)!=1: raise SystemExit("Unexpected v0.3 source: "+old)
    s=s.replace(old,new)
p.write_text(s)
print("v0.4 safety filter applied")
