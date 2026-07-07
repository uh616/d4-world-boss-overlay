# Diablo 4 Overlay — World Boss & Helltide Timer

A lightweight always-on-top overlay for Diablo 4 that shows a live countdown to the next **World Boss** and the current **Helltide** status — without ever leaving the game.

Data is pulled from [helltides.com](https://helltides.com).

[![GitHub stars](https://img.shields.io/github/stars/uh616/d4-world-boss-overlay?style=flat-square&logo=github&color=gold)](https://github.com/uh616/d4-world-boss-overlay/stargazers)
[![GitHub downloads](https://img.shields.io/github/downloads/uh616/d4-world-boss-overlay/total?style=flat-square&logo=github&color=brightgreen&label=downloads)](https://github.com/uh616/d4-world-boss-overlay/releases)
[![GitHub release](https://img.shields.io/github/v/release/uh616/d4-world-boss-overlay?style=flat-square&logo=github&color=blue)](https://github.com/uh616/d4-world-boss-overlay/releases/latest)
[![Visitors](https://visitor-badge.laobi.icu/badge?page_id=uh616.d4-world-boss-overlay&style=flat-square&color=red)](https://github.com/uh616/d4-world-boss-overlay)

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

## 📖 Legend & UI

When running, the overlay looks like this:
```
Ashava & Avarice  01:23:45  ║  HT: 38:21  ║  LG: 12:00  ⚙  ✕
```

| Element | Description |
|---|---|
| **Boss name + timer** | Name of the next World Boss and time until it spawns |
| **⚔ World Boss Active!** | Boss has spawned — go go go! |
| **HT: XX:XX** | Helltide is active — time remaining |
| **HT in XX:XX** | Time until the next Helltide starts |
| **LG: XX:XX** | Time until the next Legion event |
| **⚙** | Click to open Settings (Themes, Alert Time, Auto-hide) |
| **✕** | Click to exit the overlay |

A **sound alert** plays automatically **before** the World Boss spawns (customizable via Settings).

## 🌟 Features

- **Live Countdown**: See exactly when the next World Boss spawns and its name.
- **Helltide Tracker**: Know if Helltide is currently active or when the next one begins.
- **Legion Events**: Tracks the next Legion event.
- **Always on Top**: Transparent, borderless window that stays above Diablo 4.
- **Settings Menu**: Click the ⚙ icon to customize the overlay:
  - **Themes**: Choose between different visual styles (Crimson, Gold, Neon Blue, etc.)
  - **Opacity**: Adjust the transparency of the overlay (10% - 100%).
  - **Display Toggles**: Choose exactly what you want to see. Hide World Boss, Helltide, or Legion timers if you don't need them.
  - **Alert Time**: Set when the sound plays (1, 5, 10, or 15 minutes before the boss).
  - **Auto-hide**: Automatically hides the overlay when Diablo 4 is closed.
  - *Note: All settings are auto-saved instantly!*
- **Click-through Mode**: Press `Ctrl + L` to lock the overlay and make clicks pass through it.
- **Audio Alerts**: Plays a sound before the World Boss spawns.
- **Custom Sounds**: Place your own `alert.wav` next to the `.exe` to use a custom sound!

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

---

## ❤️ Support

If you find this useful and want to say thanks:

**[→ Boosty (card / any currency)](https://boosty.to/6i6)**

Or crypto:

| Coin | Address |
|---|---|
| **GRAM** (prev. TON) | `UQCU_NuO-7aKcYYiEsnkSd1rFpBtylB1C6upKWv7jY9r8ARe` |
| **USDT TRC20** | `TMSLWBy3eXvR6m1h3Zthmek2SGozXvmXHK` |
| **USDT TON (GRAM)** | `UQB7K0h4JlvPB7PA-as39RsepNtSrw167v5cmmoJlIJp_dNb` |
| **Bitcoin** | `bc1qn93nz3m299lktk66vnxa5aha68kh9az3xpjvac` |

---

*Made for the viewers of [Twitch channel solnechniyre6enok](https://www.twitch.tv/solnechniyre6enok)*
