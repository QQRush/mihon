#!/usr/bin/env python3
from pathlib import Path
p=Path("app/src/main/java/eu/kanade/presentation/reader/settings/ReadingModePage.kt")
s=p.read_text()
anchor='''    CheckboxItem(
        label = stringResource(MR.strings.pref_crop_borders),
        pref = viewModel.preferences.cropBordersWebtoon,
    )'''
addition='''    // E-Ink Smart Scroll controls in the reader's own Reading mode dialog.
    Text("Smart Scroll", style = MaterialTheme.typography.titleMedium)
    CheckboxItem(
        label = "Smart Scroll (E-Ink)",
        pref = viewModel.preferences.smartScrollEnabled,
    )
    CheckboxItem(
        label = "Top Trim",
        pref = viewModel.preferences.smartScrollTopTrim,
    )
    CheckboxItem(
        label = "Visual Debug",
        pref = viewModel.preferences.smartScrollVisualDebug,
    )

'''
if s.count(anchor)!=1: raise SystemExit("ReadingModePage anchor changed")
p.write_text(s.replace(anchor,addition+anchor))
print("Smart Scroll controls added to reader dialog")
