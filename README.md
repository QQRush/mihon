<div align="center">

<img src="./.github/assets/logo.png" alt="Mihon logo" width="80" />

# Mihon Smart Scroll

**A community-maintained Mihon fork for comfortable, one-tap webtoon reading — especially on E-Ink devices.**

[![Production APK](https://github.com/QQRush/mihon/actions/workflows/smart-scroll-production.yml/badge.svg?branch=feature%2Fsmart-scroll)](https://github.com/QQRush/mihon/actions/workflows/smart-scroll-production.yml)
[![Development APK](https://github.com/QQRush/mihon/actions/workflows/smart-scroll-apk.yml/badge.svg?branch=feature%2Fsmart-scroll)](https://github.com/QQRush/mihon/actions/workflows/smart-scroll-apk.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

[Download](#download) · [Features](#features) · [Setup](#getting-started) · [How it works](#how-it-works) · [Credits](#credits)

</div>

> [!IMPORTANT]
> This is an **unofficial fork** of [Mihon](https://github.com/mihonapp/mihon), not an official Mihon release. It does not include manga, webtoons, sources, or copyrighted content.

## Why Smart Scroll?

Conventional webtoon scrolling advances by a fixed distance. This can leave a large blank area at the top of the screen or split a speech balloon or drawing across two views. Smart Scroll aims to find suitable visual transitions and move the next content toward the top, while preserving reading continuity.

It is particularly useful on **E-Ink readers**, where instantaneous, predictable taps are preferable to animated scrolling. It can also be used on conventional Android phones and tablets.

## Features

- **One-tap intelligent scrolling:** searches for suitable whitespace separators instead of always moving by a fixed percentage.
- **Content-preserving navigation:** conservative checks protect panel borders, speech balloons, and small marks near transitions.
- **Smart Fit:** where eligible, fits a longer section of webtoon art into the visible area and aligns the next tap to following content.
- **Immediate movement:** no animated transition required for Smart Scroll.
- **Safe fallback:** when a reliable separator cannot be found, advance by a full viewport (100%) rather than guessing.
- **Back navigation:** checkpoint-based return toward previously visited positions, with tolerance for small manual adjustments.
- **Reader controls:** enable or disable Smart Scroll in the reader settings and quick reading controls.
- **Production variant:** visual diagnostics are hidden; the underlying content-analysis logic remains in use.

> [!NOTE]
> Detection is heuristic, not perfect. Complex artwork, unconventional layouts, or page boundaries may still require manual adjustment. Smart Fit is only applied when its eligibility checks pass.

## Download

**Latest production build (optimized, signed, ARM64):**

[**Smart Scroll Production — GitHub Actions**](https://github.com/QQRush/mihon/actions/workflows/smart-scroll-production.yml)

1. Open the latest **successful** workflow run.
2. Under **Artifacts**, download `mihon-smart-scroll-v0.78-production-arm64-signed` (or the newest production artifact).
3. Extract the ZIP and install the APK on an **ARM64 Android device**.

The production workflow builds an optimized Release APK using R8 and resource shrinking. The current custom build uses the package ID `app.mihon.dev`, to stay separate from the official Mihon app. It is signed using this fork's signing key; updates require the same signing key.

**Development/debug builds:** [Smart Scroll APK workflow](https://github.com/QQRush/mihon/actions/workflows/smart-scroll-apk.yml). Use these for reporting issues or inspecting visual diagnostics.

GitHub may require you to sign in to download Actions artifacts. These are **workflow artifacts**, not GitHub Releases.

## Getting started

1. Install the production APK. Back up your Mihon library before switching builds.
2. Open a webtoon in the **Webtoon** reader mode.
3. Enable **Smart Scroll (E-Ink)** in reader settings or the quick reader controls.
4. Tap to advance. Where a suitable separator is detected, the reader aims to place the next content near the top.
5. Enable **Smart Fit** in the reader settings if you want eligible longer artwork sections fitted to the viewport.

Smart Scroll is designed for the webtoon/vertical reader. It is not a replacement for the standard paged manga reader.

## How it works

The reader examines rendered image content around the current viewport and, when needed, a bounded lookahead area. It looks for candidate whitespace gaps while applying guards that avoid crossing meaningful ink, thin lines, or partial content. When no candidate is safe, it uses a **100% viewport fallback**.

Smart Fit is a separate path: it can show a temporary fitted snapshot of eligible content, then continue into the original scroll coordinates on the next tap. After a fitted view, a dedicated first-content alignment pass handles the transition. The current implementation also includes a guarded treatment for a small remnant of preceding artwork.

The algorithm favors **not skipping content** over always producing a perfectly aligned page. Results vary with the artwork and rendering conditions.

## Development and builds

The current working development branch is [`feature/smart-scroll`](https://github.com/QQRush/mihon/tree/feature/smart-scroll).

- [Production workflow](.github/workflows/smart-scroll-production.yml): applies the Smart Scroll patches, removes the diagnostic UI, builds a signed ARM64 Release APK.
- [Development workflow](.github/workflows/smart-scroll-apk.yml): retains visual diagnostics for testing.
- [Patch scripts](scripts/): incremental Python patches used by the GitHub Actions build.
- [Upstream Mihon](https://github.com/mihonapp/mihon): original reader and general app functionality.

The production variant is based on the **v0.77 behavior**, with a v0.78 production packaging pass. Removing the diagnostic view does **not** remove the underlying scanner, which is used by Smart Scroll and Smart Fit.

For reproducibility, inspect the workflow and its referenced patch scripts. This branch currently applies patches sequentially rather than storing all Smart Scroll modifications directly in the base Kotlin sources.

## Reporting problems

Please open an [issue](https://github.com/QQRush/mihon/issues) and include the app version, Android/device model, reading mode, and a description of the tap sequence. If possible, compare the same scene using a development build with visual diagnostics and attach screenshots **that you have permission to share**.

Useful cases include missed speech-balloon tips, a sliver of the previous panel at the top, incorrect Smart Fit transitions, or backward navigation landing in the wrong place.

## Credits

- **[Mihon Open Source Project](https://github.com/mihonapp/mihon)** and the upstream contributors for the Android manga/webtoon reader.
- **[QQRush](https://github.com/QQRush)** for the Smart Scroll / Smart Fit experiments and this fork.
- The open-source manga and webtoon reader community for ideas, feedback, and testing.

The original Mihon project's copyright and Apache-2.0 license terms remain applicable.

---

<div align="center">

### Disclaimer

The developer(s) of this application does not have any affiliation with the content providers available, and this application hosts zero content.

### License

<pre>
Copyright © 2015 Javier Tomás
Copyright © 2024 Mihon Open Source Project

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
</pre>

</div>


</div>
