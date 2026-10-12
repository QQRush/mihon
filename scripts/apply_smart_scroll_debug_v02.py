#!/usr/bin/env python3
"""Add a lightweight visual scroll diagnostic overlay; no separator detection yet."""
from pathlib import Path
def patch(path, old, new):
    p=Path(path); s=p.read_text(encoding="utf-8")
    if new in s: return
    if s.count(old)!=1: raise SystemExit(f"Patch anchor mismatch: {path}: {old[:80]}")
    p.write_text(s.replace(old,new),encoding="utf-8")
base="app/src/main/java/eu/kanade/tachiyomi/ui/reader/"
patch(base+"setting/ReaderPreferences.kt",
    '    val smartScrollEnabled: Preference<Boolean> = preferenceStore.getBoolean("smart_scroll_enabled", false)',
    '    val smartScrollEnabled: Preference<Boolean> = preferenceStore.getBoolean("smart_scroll_enabled", false)\n\n    val smartScrollVisualDebug: Preference<Boolean> = preferenceStore.getBoolean("smart_scroll_visual_debug", false)')
settings="app/src/main/java/eu/kanade/presentation/more/settings/screen/SettingsReaderScreen.kt"
patch(settings,
    '                    title = "Smart Scroll (E-Ink): instant tap navigation",\n                ),',
    '                    title = "Smart Scroll (E-Ink): instant tap navigation",\n                ),\n                Preference.PreferenceItem.SwitchPreference(\n                    preference = readerPreferences.smartScrollVisualDebug,\n                    title = "Smart Scroll: visual debug",\n                ),')
viewer=base+"viewer/webtoon/WebtoonViewer.kt"
patch(viewer,'import android.graphics.PointF','import android.graphics.PointF\nimport android.widget.FrameLayout')
patch(viewer,
    '    private val frame = WebtoonFrame(activity)',
    '    private val frame = WebtoonFrame(activity)\n\n    private val debugOverlay = SmartScrollDebugOverlay(activity)')
patch(viewer,
    '        frame.addView(recycler)',
    '        frame.addView(recycler)\n        frame.addView(debugOverlay, FrameLayout.LayoutParams(MATCH_PARENT, MATCH_PARENT))\n        debugOverlay.isClickable = false\n        debugOverlay.isFocusable = false')
patch(viewer,
    '                    onScrolled()',
    '                    onScrolled()\n                    updateSmartScrollDebug()')
patch(viewer,
    '    private fun scrollUp() {',
    '    private fun updateSmartScrollDebug() {\n        val enabled = readerPreferences.smartScrollEnabled.get() && readerPreferences.smartScrollVisualDebug.get()\n        debugOverlay.visibility = if (enabled) View.VISIBLE else View.GONE\n        if (enabled) {\n            val first = layoutManager.findFirstVisibleItemPosition()\n            val offset = layoutManager.findViewByPosition(first)?.top ?: 0\n            debugOverlay.update(first, offset, recycler.computeVerticalScrollOffset(), scrollDistance)\n        }\n    }\n\n    private fun scrollUp() {')
patch(viewer,
    '    private fun scrollDown() {',
    '    private fun scrollDown() {\n        updateSmartScrollDebug()')
patch(viewer,
    '    private fun scrollUp() {\n',
    '    private fun scrollUp() {\n        updateSmartScrollDebug()\n')
# Ensure debug appears even if no scroll event has yet fired.
patch(viewer,
    '        debugOverlay.isFocusable = false',
    '        debugOverlay.isFocusable = false\n        frame.post { updateSmartScrollDebug() }')
print("Visual debug patch applied")
