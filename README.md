# Diablo 4 Overlay — World Boss & Helltide Timer

A lightweight always-on-top overlay for Diablo 4 that shows a live countdown to the next **World Boss** and the current **Helltide** status — without ever leaving the game. Built with Electron for maximum performance and a seamless, borderless experience.

Data is pulled from [helltides.com](https://helltides.com).

[![GitHub stars](https://img.shields.io/github/stars/uh616/d4-world-boss-overlay?style=flat-square&logo=github&color=gold)](https://github.com/uh616/d4-world-boss-overlay/stargazers)
[![GitHub downloads](https://img.shields.io/github/downloads/uh616/d4-world-boss-overlay/total?style=flat-square&logo=github&color=brightgreen&label=downloads)](https://github.com/uh616/d4-world-boss-overlay/releases)
[![GitHub release](https://img.shields.io/github/v/release/uh616/d4-world-boss-overlay?style=flat-square&logo=github&color=blue)](https://github.com/uh616/d4-world-boss-overlay/releases/latest)
[![Visitors](https://visitor-badge.laobi.icu/badge?page_id=uh616.d4-world-boss-overlay&style=flat-square&color=red)](https://github.com/uh616/d4-world-boss-overlay)

---

## ⬇️ Download

**[→ Latest Release](https://github.com/uh616/d4-world-boss-overlay/releases/latest)**

---

## 🚀 Installation & Usage

1. Download **`D4-Overlay-2.0.0.exe`** from the latest [Release](https://github.com/uh616/d4-world-boss-overlay/releases/latest).
2. Run it! It's a completely portable executable, so you can place it anywhere (e.g., your Desktop) without installing anything.
3. The overlay will appear in the top-left corner of your screen. You can grab it by the bar to drag it anywhere.

> ⚠️ Windows Defender may show an "Unknown publisher" warning since the exe isn't signed. Click **"More info" → "Run anyway"** to proceed.

---

## 📖 Legend & UI

The overlay is a compact horizontal bar that stays on top of your screen at all times. It contains:

| Element | Description |
|---|---|
| **Logo** | Your app logo on the left side. Click it to toggle Mini Mode (hides timers, shows only the logo) |
| **Boss name + timer** | Name of the next World Boss and time until it spawns |
| **⚔ World Boss Active!** | Boss has spawned — go go go! |
| **HT: XX:XX** | Helltide is active — time remaining |
| **HT in XX:XX** | Time until the next Helltide starts |
| **LG: XX:XX** | Time until the next Legion event |
| **⚙** | Click to open Settings |
| **✕** | Click to completely close the app |

A **sound alert** plays automatically before events spawn (fully customizable via Settings).

## 🌟 Features

- **Always on Top**: Transparent, borderless window that stays permanently above Diablo 4 using Electron's `screen-saver` level.
- **Auto-Hide**: Automatically hides the overlay when you Alt-Tab out of Diablo 4, keeping your desktop clean.
- **Lock & Click-through**: Press a fully customizable hotkey (default `Ctrl+L`) to lock the overlay in place and make all mouse clicks pass straight through it.
- **Smart Settings Menu**: 
  - **Themes**: Choose between Crimson, Gold, or Neon Blue.
  - **Scale & Opacity**: Adjust text size (from tiny UI to large text) and window transparency.
  - **Volume Control**: Change the volume of the alert sounds via a slider.
  - **Event Toggles**: Show or hide World Boss, Helltide, and Legion timers independently.
  - *All settings are auto-saved instantly.*
- **Custom Sounds**: Place your own `alert.wav` next to the `.exe` to use a custom sound!

---

## 🎵 Custom Alert Sound

The default alert sound is already **bundled inside the app** — no extra files needed. To replace it with your own:

1. Get a `.wav` file (convert MP3 → WAV at [CloudConvert](https://cloudconvert.com/mp3-to-wav)).
2. Place it in the **same folder** as your `D4 Overlay.exe`.
3. Rename it to **`alert.wav`**.

The app will automatically detect and use your custom file instead of the built-in default.

---

## 💻 For Developers

This project was completely rewritten from Python to **Node.js + Electron** for perfect rendering performance and click-through mechanics on Windows.

**Run locally:**
```bash
git clone https://github.com/uh616/d4-world-boss-overlay.git
cd d4-world-boss-overlay
npm install
npm start
```

**Build the .exe yourself:**
```bash
npm run build
```
The compiled, portable `.exe` will be located in the `dist/` directory.

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

*Made for the viewers of [Twitch channel solnechniyre6enok](https://www.twitch.tv/solnechniyre6enok)*
