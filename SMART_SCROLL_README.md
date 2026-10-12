# Mihon Smart Scroll v0.3 — separator diagnostic
- Experimental green lines: near-uniform white or black horizontal gutters detected in the **visible viewport only**.
- Red: fixed scroll target; blue: overlap reference.
- Scanning uses a downsampled 64-pixel-wide image and runs only when Visual Debug is enabled.
- No separator-guided navigation yet; no scanning beyond the viewport yet.
- A future version will add a quick Smart Scroll toggle to the reader's bottom toolbar.
- Build through GitHub Actions. Turn off Visual Debug for normal reading.
