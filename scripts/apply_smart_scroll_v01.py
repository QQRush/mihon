#!/usr/bin/env python3
"""Apply Smart Scroll v0.1 to Mihon sources. Idempotent."""
from pathlib import Path

def replace(path, old, new):
    p = Path(path)
    content = p.read_text(encoding="utf-8")
    if new in content:
        print(f"Already patched: {path}")
        return
    if content.count(old) != 1:
        raise SystemExit(f"Expected exactly one match in {path}: {old!r}")
    p.write_text(content.replace(old, new), encoding="utf-8")
    print(f"Patched: {path}")

replace("app/build.gradle.kts",
    'applicationId = "app.mihon"',
    'applicationId = "app.mihon.smartscroll"')
replace("app/src/main/java/eu/kanade/tachiyomi/ui/reader/setting/ReaderPreferences.kt",
    '    val webtoonSidePadding: Preference<Int>',
    '    val smartScrollEnabled: Preference<Boolean> = preferenceStore.getBoolean("smart_scroll_enabled", false)\n\n    val webtoonSidePadding: Preference<Int>')
replace("app/src/main/java/eu/kanade/presentation/more/settings/screen/SettingsReaderScreen.kt",
    '                Preference.PreferenceItem.SliderPreference(\n                    preference = readerPreferences.webtoonSidePadding,',
    '                Preference.PreferenceItem.SwitchPreference(\n                    preference = readerPreferences.smartScrollEnabled,\n                    title = "Smart Scroll (E-Ink): instant tap navigation",\n                ),\n                Preference.PreferenceItem.SliderPreference(\n                    preference = readerPreferences.webtoonSidePadding,')
p="app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon/WebtoonViewer.kt"
old='if (config.usePageTransitions) {'
path=Path(p)
src=path.read_text(encoding="utf-8")
new='if (config.usePageTransitions && !readerPreferences.smartScrollEnabled.get()) {'
if src.count(new) >= 2:
    print("Already patched WebtoonViewer")
else:
    if src.count(old) < 2:
        raise SystemExit("Could not find both scroll transitions")
    # Limit edits to the scrollUp/scrollDown functions.
    start=src.index('private fun scrollUp()')
    end=src.index('private fun scrollDown()', start)
    before=src[start:end]
    if before.count(old)!=1:
        raise SystemExit("scrollUp structure changed")
    src=src[:start]+before.replace(old,new,1)+src[end:]
    start=src.index('private fun scrollDown()')
    end=src.find('\n    private fun ', start+1)
    if end<0: end=len(src)
    segment=src[start:end]
    if segment.count(old)!=1:
        raise SystemExit("scrollDown structure changed")
    src=src[:start]+segment.replace(old,new,1)+src[end:]
    path.write_text(src,encoding="utf-8")
    print("Patched WebtoonViewer")
