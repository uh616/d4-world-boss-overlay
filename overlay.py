import tkinter as tk
import urllib.request
import json
import threading
import time
import winsound
import os
import sys
from PIL import Image, ImageTk

# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────
APP_NAME    = "Diablo 4 Overlay"
VERSION     = "1.0.0"
GITHUB_REPO = "uh616/d4-world-boss-overlay"

API_URL          = "https://helltides.com/api/schedule"
REFRESH_INTERVAL = 300      # seconds between API refreshes
ALERT_MINUTES    = 5        # alert N minutes before world boss
CUSTOM_SOUND     = "alert.wav"
LOGO_FILE        = "logo.png"
LOGO_SIZE        = 26       # px

# Helltide lasts 55 minutes
HELLTIDE_DURATION = 55 * 60


class OverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        # ── Colors ──────────────────────────────
        self.bg           = "#0a0a0a"
        self.border       = "#8b0000"
        self.col_gold     = "#ffcc00"   # world boss / idle timers
        self.col_red      = "#ef4444"   # helltide active
        self.col_gray     = "#a1a1aa"   # helltide countdown
        self.col_dim      = "#3f3f46"   # separator / close btn
        self.transparent  = "black"

        # ── State ────────────────────────────────
        self.next_boss     = None
        self.next_helltide = None
        self.alerted_id    = None
        self._drag_x = self._drag_y = 0

        # ── Load logo ────────────────────────────
        self.logo_img = None
        if os.path.exists(LOGO_FILE):
            try:
                img = Image.open(LOGO_FILE).resize(
                    (LOGO_SIZE, LOGO_SIZE), Image.LANCZOS
                )
                self.logo_img = ImageTk.PhotoImage(img)
            except Exception:
                pass

        # ── Layout dimensions ────────────────────
        # [ WB text (270) | sep (20) | HT text (140) | sep (16) | logo (30) | close (24) ]
        self.W = 510 + (LOGO_SIZE + 10 if self.logo_img else 0)
        self.H = 36

        self.root.geometry(f"{self.W}x{self.H}+20+20")
        self.root.config(bg=self.transparent)
        self.root.wm_attributes("-transparentcolor", self.transparent)

        # ── Canvas ───────────────────────────────
        self.cv = tk.Canvas(
            self.root, width=self.W, height=self.H,
            bg=self.transparent, highlightthickness=0
        )
        self.cv.pack(fill="both", expand=True)

        # Background rect
        self.cv.create_rectangle(
            1, 1, self.W - 1, self.H - 1,
            fill=self.bg, outline=self.border, width=2
        )

        # World Boss text (left side)
        self.wb_item = self.cv.create_text(
            155, 18,
            text="Loading...", anchor="center",
            font=("Consolas", 12, "bold"), fill=self.col_gold
        )

        # Separator
        self.cv.create_text(
            310, 18, text="║", anchor="center",
            font=("Consolas", 12, "bold"), fill=self.col_dim
        )

        # Helltide text
        self.ht_item = self.cv.create_text(
            390, 18,
            text="HT: ...", anchor="center",
            font=("Consolas", 12, "bold"), fill=self.col_gray
        )

        # Logo image (optional)
        logo_x = self.W - 44
        if self.logo_img:
            logo_border_x = logo_x - LOGO_SIZE // 2 - 4
            self.cv.create_rectangle(
                logo_border_x, 4,
                logo_border_x + LOGO_SIZE + 8, self.H - 4,
                fill="#111111", outline=self.border, width=1
            )
            self.cv.create_image(logo_border_x + 4 + LOGO_SIZE // 2, 18,
                                  image=self.logo_img, anchor="center")
            close_x = self.W - 14
        else:
            close_x = self.W - 14

        # Close button
        self.close_btn = self.cv.create_text(
            close_x, 18, text="✕", anchor="center",
            font=("Segoe UI", 11, "bold"),
            fill=self.col_dim, activefill="#ef4444"
        )
        self.cv.tag_bind(self.close_btn, "<Button-1>", self._quit)

        # Drag bindings
        self.cv.bind("<ButtonPress-1>",   self._drag_start)
        self.cv.bind("<ButtonRelease-1>", self._drag_stop)
        self.cv.bind("<B1-Motion>",       self._drag_move)

        # Start background fetch
        threading.Thread(target=self._fetch_loop, daemon=True).start()
        self._tick()

    # ── Drag ────────────────────────────────────
    def _drag_start(self, e):
        if e.x > self.W - 28:   # near X button — don't drag
            return
        self._drag_x, self._drag_y = e.x, e.y

    def _drag_stop(self, e):
        self._drag_x = self._drag_y = 0

    def _drag_move(self, e):
        if self._drag_x:
            x = self.root.winfo_x() + (e.x - self._drag_x)
            y = self.root.winfo_y() + (e.y - self._drag_y)
            self.root.geometry(f"+{x}+{y}")

    def _quit(self, _=None):
        self.root.destroy()
        sys.exit(0)

    # ── Data fetch ──────────────────────────────
    def _fetch_loop(self):
        self._fetch()
        while True:
            time.sleep(REFRESH_INTERVAL)
            self._fetch()

    def _fetch(self):
        try:
            req = urllib.request.Request(
                API_URL, headers={"User-Agent": "Mozilla/5.0"}
            )
            data = json.loads(urllib.request.urlopen(req).read())
            now  = time.time()

            # Next world boss
            for ev in data.get("world_boss", []):
                if ev["timestamp"] > now:
                    self.next_boss = ev
                    break

            # Current or next helltide
            for ev in data.get("helltide", []):
                if ev["timestamp"] + HELLTIDE_DURATION > now:
                    self.next_helltide = ev
                    break
        except Exception as e:
            print(f"[fetch error] {e}")

    # ── Sound ───────────────────────────────────
    def _play_sound(self):
        if os.path.exists(CUSTOM_SOUND):
            winsound.PlaySound(CUSTOM_SOUND,
                               winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            winsound.PlaySound("SystemAsterisk",
                               winsound.SND_ALIAS | winsound.SND_ASYNC)

    # ── UI tick (every 1 s) ─────────────────────
    def _tick(self):
        now = time.time()

        # ── World Boss ──────────────────────────
        if self.next_boss:
            left = int(self.next_boss["timestamp"] - now)
            if left > 0:
                h, m, s = left // 3600, (left % 3600) // 60, left % 60

                names = list({z["boss"] for z in self.next_boss.get("zone", [])
                              if "boss" in z})
                if not names:
                    names = [self.next_boss.get("boss", "World Boss")]
                label = " & ".join(names) + f"  {h:02d}:{m:02d}:{s:02d}"

                self.cv.itemconfig(self.wb_item, text=label, fill=self.col_gold)

                # Alert
                if left <= ALERT_MINUTES * 60 and self.alerted_id != self.next_boss["id"]:
                    self._play_sound()
                    self.alerted_id = self.next_boss["id"]
            else:
                self.cv.itemconfig(self.wb_item,
                                   text="⚔  World Boss Active!", fill=self.col_red)
        else:
            self.cv.itemconfig(self.wb_item, text="WB: connecting...", fill=self.col_gray)

        # ── Helltide ────────────────────────────
        if self.next_helltide:
            ht_start = self.next_helltide["timestamp"]
            ht_end   = ht_start + HELLTIDE_DURATION

            if now < ht_start:
                left = int(ht_start - now)
                m, s = left // 60, left % 60
                self.cv.itemconfig(self.ht_item,
                                   text=f"HT in {m:02d}:{s:02d}", fill=self.col_gray)
            elif now < ht_end:
                left = int(ht_end - now)
                m, s = left // 60, left % 60
                self.cv.itemconfig(self.ht_item,
                                   text=f"HT: {m:02d}:{s:02d}", fill=self.col_red)
            else:
                self.cv.itemconfig(self.ht_item,
                                   text="HT starting...", fill=self.col_gray)
        else:
            self.cv.itemconfig(self.ht_item, text="HT: ...", fill=self.col_gray)

        self.root.after(1000, self._tick)


if __name__ == "__main__":
    root = tk.Tk()
    OverlayApp(root)
    root.mainloop()
