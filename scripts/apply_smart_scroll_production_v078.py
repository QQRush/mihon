#!/usr/bin/env python3
"""Production variant of v0.77: remove debug UI, preserve scanner and navigation."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader")
p=base/"viewer/webtoon/WebtoonViewer.kt"
s=p.read_text()
a='''        frame.addView(debugOverlay, FrameLayout.LayoutParams(MATCH_PARENT, MATCH_PARENT))
        debugOverlay.isClickable = false
        debugOverlay.isFocusable = false'''
assert s.count(a)==1, "overlay view anchor changed"
s=s.replace(a,'''        // Production: scanner remains available, but diagnostic view is not attached.''',1)
p.write_text(s)
p=Path("app/src/main/java/eu/kanade/presentation/more/settings/screen/SettingsReaderScreen.kt")
s=p.read_text()
a='''                Preference.PreferenceItem.SwitchPreference(
                    preference = readerPreferences.smartScrollVisualDebug,
                    title = "Smart Scroll: visual debug",
                ),'''
assert s.count(a)==1, "debug settings anchor changed"
s=s.replace(a,"",1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
a='''        val release = getByName("release") {
            isMinifyEnabled = true'''
assert s.count(a)==1
s=s.replace(a,'''        val release = getByName("release") {
            // Same package as signed .dev builds: retain installed app data.
            applicationIdSuffix = ".dev"
            isMinifyEnabled = true''',1)
assert s.count("versionCode = 115")==1
s=s.replace("versionCode = 115","versionCode = 116",1)
p.write_text(s)
print("Production v0.78: no diagnostic UI; preserve algorithms; optimized signed release, same .dev package")
