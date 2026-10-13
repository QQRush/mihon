#!/usr/bin/env python3
from pathlib import Path
p=Path("app/build.gradle.kts")
s=p.read_text()
old='''            isUniversalApk = true
            reset()
            include("armeabi-v7a", "arm64-v8a", "x86", "x86_64")'''
new='''            isUniversalApk = false
            reset()
            include("arm64-v8a")'''
if s.count(old)!=1: raise SystemExit("ABI split anchor changed")
p.write_text(s.replace(old,new))
print("arm64-v8a only, universal APK disabled")
