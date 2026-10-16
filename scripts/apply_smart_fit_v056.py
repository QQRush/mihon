#!/usr/bin/env python3
"""v0.56: uniform proportional Smart Fit and trim blank gutter from snapshot.
Navigation still uses the same separator END in original coordinates."""
from pathlib import Path
base=Path("app/src/main/java/eu/kanade/tachiyomi/ui/reader/viewer/webtoon")
p=base/"SmartScrollDebugOverlay.kt"
s=p.read_text()
a='''    private var smartFitTarget = -1
    fun fitTarget(): Int = smartFitTarget'''
assert s.count(a)==1
s=s.replace(a,'''    private var smartFitTarget = -1
    private var smartFitArtEnd = -1
    fun fitTarget(): Int = smartFitTarget
    fun fitArtEnd(): Int = smartFitArtEnd''',1)
a='''        smartFitTarget = -1
        if (h < 100'''
assert s.count(a)==1
s=s.replace(a,'''        smartFitTarget = -1
        smartFitArtEnd = -1
        if (h < 100''',1)
a='''            var found = -1
            while (y < sh)'''
assert s.count(a)==1
s=s.replace(a,'''            var found = -1
            var artEnd = -1
            while (y < sh)''',1)
a='''                found = gapFinish
                break'''
assert s.count(a)==1
s=s.replace(a,'''                found = gapFinish
                artEnd = finish
                break''',1)
a='''                if (smartFitMarkerEligible) smartFitTarget = found'''
assert s.count(a)==1
s=s.replace(a,'''                if (smartFitMarkerEligible && artEnd > h) {
                    smartFitTarget = found
                    smartFitArtEnd = (artEnd + 3).coerceAtMost(found)
                }''',1)
assert s.count('"SCROLL DEBUG v0.55 | live fit snapshot"')==1
s=s.replace('"SCROLL DEBUG v0.55 | live fit snapshot"','"SCROLL DEBUG v0.56 | proportional art fit"',1)
p.write_text(s)
p=base/"WebtoonViewer.kt"
s=p.read_text()
a='''import android.graphics.Canvas
import android.graphics.Color'''
assert s.count(a)==1
s=s.replace(a,'''import android.graphics.Canvas
import android.graphics.Matrix
import android.graphics.Color''',1)
a='''        val target = debugOverlay.fitTarget()
        if (target <= recycler.height || target > recycler.height * 13 / 10 ||
            recycler.width < 20) {'''
assert s.count(a)==1
s=s.replace(a,'''        val target = debugOverlay.fitTarget()
        val artEnd = debugOverlay.fitArtEnd()
        if (target <= recycler.height || target > recycler.height * 13 / 10 ||
            artEnd <= recycler.height || artEnd > target ||
            recycler.width < 20) {''',1)
a='''Bitmap.createBitmap(recycler.width, target, Bitmap.Config.ARGB_8888)'''
assert s.count(a)==1
s=s.replace(a,'''Bitmap.createBitmap(recycler.width, artEnd, Bitmap.Config.ARGB_8888)''',1)
a='''        fitImage.setImageBitmap(bmp)
        fitImage.visibility = View.VISIBLE'''
assert s.count(a)==1
s=s.replace(a,'''        fitImage.setImageBitmap(bmp)
        // Same factor on both axes: preserve aspect ratio.
        // Align top, center the narrower image horizontally.
        val factor = recycler.height.toFloat() / artEnd.toFloat()
        val matrix = Matrix()
        matrix.setScale(factor, factor)
        matrix.postTranslate((recycler.width * (1f - factor)) / 2f, 0f)
        fitImage.imageMatrix = matrix
        fitImage.visibility = View.VISIBLE''',1)
a='''        fitImage.scaleType = ImageView.ScaleType.FIT_XY'''
assert s.count(a)==1
s=s.replace(a,'''        fitImage.scaleType = ImageView.ScaleType.MATRIX''',1)
p.write_text(s)
p=Path("app/build.gradle.kts")
s=p.read_text()
assert s.count("versionCode = 93")==1
p.write_text(s.replace("versionCode = 93","versionCode = 94",1))
print("v0.56 proportional Smart Fit, crop before blank gap, navigation unchanged")
