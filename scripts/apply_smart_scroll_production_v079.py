#!/usr/bin/env python3
"""v0.79 production cleanup: hide quick reader Visual Debug control."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/presentation/reader/settings/ReadingModePage.kt")
s=p.read_text()
a='''    CheckboxItem(
        label = "Visual Debug",
        pref = viewModel.preferences.smartScrollVisualDebug,
    )
'''
assert s.count(a)==1, "Quick reader Visual Debug control not found"
p.write_text(s.replace(a,"",1))
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 116")==1
p.write_text(s.replace("versionCode = 116","versionCode = 117",1))
print("v0.79: quick reader debug switch removed; core scrolling unchanged")
