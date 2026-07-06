# Diablo 4 Overlay — World Boss & Helltide Timer

A lightweight always-on-top overlay for Diablo 4 that shows a live countdown to the next **World Boss** and the current **Helltide** status — without ever leaving the game.

Data is pulled from [helltides.com](https://helltides.com).

---

## ⬇️ Download

**[→ Latest Release](https://github.com/uh616/d4-world-boss-overlay/releases/latest)**

---

## Installation

1. Download **`D4-Overlay.exe`** from the latest [Release](https://github.com/uh616/d4-world-boss-overlay/releases/latest)
2. Place it anywhere you like (e.g. your Desktop)
3. Run it — the overlay will appear in the top-left corner of your screen

> ⚠️ Windows Defender may show an "Unknown publisher" warning since the exe isn't signed. Click **"More info" → "Run anyway"** to proceed.

---

## Usage

| Action | How |
|---|---|
| Move the overlay | Click and drag |
| Close the overlay | Click the **✕** button on the right |

---

## What it shows

```
Ashava & Avarice  01:23:45  ║  HT: 38:21  🖼  ✕
```

| Element | Description |
|---|---|
| **Boss name + timer** | Name of the next World Boss and time until it spawns |
| **⚔ World Boss Active!** | Boss has spawned — go go go! |
| **HT: XX:XX** (red) | Helltide is active — time remaining |
| **HT in XX:XX** (grey) | Time until the next Helltide starts |

A **sound alert** plays automatically **5 minutes before** the World Boss spawns.

---

## Custom Alert Sound

By default, a standard Windows sound plays. To use your own:

1. Get a `.wav` file (convert MP3 → WAV at [CloudConvert](https://cloudconvert.com/mp3-to-wav))
2. Place it in the **same folder** as `D4-Overlay.exe`
3. Rename it to **`alert.wav`**

To go back to the default — just delete `alert.wav`.

---

## For Developers

```bash
git clone https://github.com/uh616/d4-world-boss-overlay.git
cd d4-world-boss-overlay
pip install -r requirements.txt
python overlay.py
```

**Build the .exe yourself:**
```bash
python build.py
```

---

*Made for the viewers of [Twitch channel solnechniyre6enok](https://www.twitch.tv/solnechniyre6enok)*
