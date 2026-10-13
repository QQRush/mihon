#!/usr/bin/env python3
"""v0.18.1: remove stale Top Trim option in reader quick settings."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/presentation/reader/settings/ReadingModePage.kt")
s=p.read_text()
old='''    CheckboxItem(
        label = "Top Trim",
        pref = viewModel.preferences.smartScrollTopTrim,
    )
'''
if s.count(old)!=1:
    raise SystemExit("Expected one Top Trim quick setting")
p.write_text(s.replace(old,""))
print("v0.18.1: removed stale reader Top Trim setting")
