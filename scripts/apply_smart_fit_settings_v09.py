#!/usr/bin/env python3
"""v0.9: persistent Smart Fit settings, pending safe per-image rendering."""
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/setting/ReaderPreferences.kt")
s=p.read_text()
anchor='    val smartScrollTopTrim: Preference<Boolean> = preferenceStore.getBoolean("smart_scroll_top_trim", true)'
if s.count(anchor)!=1: raise SystemExit("Missing Smart Scroll preferences anchor")
s=s.replace(anchor,anchor+'\n\n    val smartFitEnabled: Preference<Boolean> = preferenceStore.getBoolean("smart_fit_enabled", false)\n\n    val smartFitMaxReduction: Preference<Int> = preferenceStore.getInt("smart_fit_max_reduction", 20)')
p.write_text(s)
p=Path("app/src/main/java/eu/kanade/presentation/more/settings/screen/SettingsReaderScreen.kt")
s=p.read_text()
anchor='                    title = "Smart Scroll: Top Trim (experimental)",\n                ),'
if s.count(anchor)!=1: raise SystemExit("Missing webtoon settings anchor")
addition='''                    title = "Smart Scroll: Top Trim (experimental)",
                ),
                Preference.PreferenceItem.SwitchPreference(
                    preference = readerPreferences.smartFitEnabled,
                    title = "Smart Fit (preparazione: non ancora attivo)",
                ),
                Preference.PreferenceItem.SliderPreference(
                    preference = readerPreferences.smartFitMaxReduction,
                    valueRange = 5..33,
                    title = "Smart Fit: riduzione massima",
                    valueText = { "$it%" },
                ),'''
s=s.replace(anchor,addition)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
if s.count("versionCode = 41")!=1: raise SystemExit("Unexpected versionCode")
p.write_text(s.replace("versionCode = 41","versionCode = 42",1))
print("v0.9 Smart Fit preference controls installed")
