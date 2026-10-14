# Codex working agreement — Mihon Smart Scroll

## Project and source of truth
- Repository: `QQRush/mihon`; working branch: `feature/smart-scroll`.
- Custom Android Mihon reader for E-Ink/BOOX, with instant tap-to-scroll for vertical webtoons.
- As of 2026-10-14 the reference is **v0.23**, commit `9b086d8`, versionCode **61**. Check Git HEAD and workflow before making assumptions; this reference may become outdated.
- **Important:** most Smart Scroll changes are applied by ordered `scripts/apply_smart_scroll_*.py` steps inside `.github/workflows/smart-scroll-apk.yml`. The unpatched Kotlin files in the repository are NOT necessarily the effective build sources. Inspect workflow order and patch scripts before editing. Prefer the smallest compatible new patch at the end of the existing sequence; avoid silent rewrites.

## Non-negotiable behavior
- Smart Scroll is an explicit reader option. **OFF means stock Mihon behavior**.
- When ON, a tap scrolls immediately (no animation) through a vertical webtoon.
- Treat consecutive JPGs/pages as a **continuous virtual strip**; file boundaries are technical, not panel boundaries. Do not stitch full-resolution images into a giant bitmap.
- In the currently accepted algorithm, scan the **bottom ~35% of the visible viewport** for a clear horizontal white/black gutter, then align the next content at the top if safe. If no valid separator, advance one viewport. Do not skip or repeat story content or crop speech bubbles.
- Smart Back should restore the actual previous position. Manual scrolling invalidates Smart Back history.
- **Top Trim is back and ON by default as of v0.22**, separately switchable. It trims only verified blank whitespace at the beginning of the newly displayed viewport, leaving a safety margin; never remove text, dialogue, or artwork.
- Preserve existing BOOX/E-Ink-friendly behavior and lightweight code. Do not add contrast/saturation settings already provided by the BOOX app.

## Visual Debug v0.23
- **Red line:** fixed start of scan region, 65% down the viewport.
- **Green lines:** candidate gutters from the diagnostic probe; these are not necessarily the navigation detector's accepted gutter.
- **Blue line:** chosen landing from the same viewport separator detector, if visible. No visible blue line when there is no accepted landing. In that case the normal full-viewport fallback applies.
- Visual Debug should be diagnostic only, not alter navigation decisions. Verify what the build actually draws before claiming success.
- Values such as `computeVerticalScrollOffset()` deltas can be misleading when crossing RecyclerView items. Do not treat them as ground-truth movement across JPG boundaries.

## Known rejected approaches and constraints
- Avoid many extra guards, special cases, or chapter-specific fixes. The user prefers a **small, general algorithm** over layered heuristics.
- Do not revive v0.20/v0.20D2 special next-JPG boundary scans, which rejected valid gutters. v0.21 intentionally returned to unified viewport navigation.
- Do not assume old debug lines mean real selected positions: the original red/blue lines were static `step`/mirror markers, which v0.23 was designed to correct.
- Do not change page-fit, orientation, navigation, or Top Trim rules merely because a screenshot looks unusual. Explain the diagnosis and ask before behavioral changes.
- Do not rebuild repeatedly to experiment without a clear hypothesis. Preserve working baselines and make focused changes.

## Working process
1. Communicate with the user in **Italian**.
2. First inspect `git status`, branch, relevant workflow/scripts and effective code. Report what you found.
3. For ambiguous requests, explain a small proposed change and ask before implementing it. For explicit requests, make the smallest change needed.
4. Before any write, install, `git reset`, force push, destructive cleanup, or ADB action that changes the device, explain and obtain approval if not already explicitly authorized.
5. Prefer verifying with existing tests and a single controlled build. Do not claim APK builds, installation, tests or device effects succeeded without checking.
6. Keep the same signing identity/application ID for upgrades when possible; do not expose or commit keystores, passwords, signing secrets or personal data.
7. If a command fails, show the actual error and diagnose it; do not guess. Avoid changing unrelated files.
8. After changes, summarize files touched, version/commit, tests performed, remaining uncertainty and how to reproduce.
