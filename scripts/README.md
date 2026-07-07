# Developer Scripts

This folder contains helper scripts for **building and packaging** the overlay.  
End users do **not** need these files — they are for maintainers only.

## Files

| File | Description |
|------|-------------|
| `build.py` | Compiles `overlay.py` into a standalone Windows `.exe` using PyInstaller |
| `makezip.ps1` | PowerShell script to package the release into a `.zip` archive |

## Build Instructions

### 1. Install dependencies
```
pip install -r ../requirements.txt
pip install pyinstaller
```

### 2. Build the exe
```
python build.py
```
The output `.exe` will be placed in `../dist/`.

### 3. Package for release (optional)
```
powershell -ExecutionPolicy Bypass -File makezip.ps1
```
