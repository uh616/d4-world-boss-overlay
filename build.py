"""
build.py — Build D4 Overlay into a standalone .exe
Run: python build.py
"""
import os
import subprocess
import sys
from PIL import Image

# ── Convert logo.png → logo.ico ─────────────────────────────────────────────
print("[1/3] Converting logo.png to logo.ico...")
img = Image.open("logo.png").convert("RGBA")
icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save("logo.ico", format="ICO", sizes=icon_sizes)
print("      Done — logo.ico created")

# ── Run PyInstaller ──────────────────────────────────────────────────────────
print("[2/3] Running PyInstaller...")
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",                      # single .exe
    "--windowed",                     # no console window
    "--icon=logo.ico",                # exe icon
    "--add-data=logo.png;.",          # bundle logo inside exe
    "--name=D4-Overlay",             # output filename
    "--clean",                        # clean cache before build
    "overlay.py",
]
result = subprocess.run(cmd)
if result.returncode != 0:
    print("ERROR: PyInstaller failed!")
    sys.exit(1)
print("      Done — dist/D4-Overlay.exe created")

# ── Create release zip ───────────────────────────────────────────────────────
print("[3/3] Creating release zip...")
import zipfile, shutil

zip_name = "D4-Overlay-v1.0.0.zip"
with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write("dist/D4-Overlay.exe", "D4-Overlay.exe")
    zf.write("README.md", "README.md")
    # Include empty placeholder so users know about the sound feature
    if os.path.exists("alert.wav"):
        zf.write("alert.wav", "alert.wav")

print(f"      Done — {zip_name} created")
print()
print("===================================================")
print(f"  Release ready: {zip_name}")
print("  Upload to: https://github.com/uh616/d4-world-boss-overlay/releases/new")
print("===================================================")
