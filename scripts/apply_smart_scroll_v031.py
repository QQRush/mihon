#!/usr/bin/env python3
"""v0.31: hide obsolete Top Trim controls, preserve stored behavior."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/presentation/more/settings/screen/SettingsReaderScreen.kt")
s=p.read_text()
a='''                Preference.PreferenceItem.SwitchPreference(
                    preference = readerPreferences.smartScrollTopTrim,
                    title = "Smart Scroll: Top Trim",
                ),
'''
assert s.count(a)==1
p.write_text(s.replace(a,"",1))
p=Path("app/src/main/java/eu/kanade/presentation/reader/settings/ReadingModePage.kt")
s=p.read_text()
a='''    CheckboxItem(
        label = "Top Trim",
        pref = viewModel.preferences.smartScrollTopTrim,
    )
'''
assert s.count(a)==1
p.write_text(s.replace(a,"",1))
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 68")==1
p.write_text(s.replace("versionCode = 68","versionCode = 69",1))
print("v0.31: Top Trim hidden in both menus, behavior preserved")
