import tkinter as tk
import tkinter.messagebox as msgbox
import urllib.request
import urllib.error
import json
import threading
import time
import winsound
import os
import sys
import subprocess
import tempfile
from PIL import Image, ImageTk


def _bundled(filename: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def _beside_exe(filename: str) -> str:
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)


# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────
APP_NAME    = "Diablo 4 Overlay"
VERSION     = "1.1.0"
GITHUB_REPO = "uh616/d4-world-boss-overlay"

API_URL          = "https://helltides.com/api/schedule"
GITHUB_API_URL   = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
REFRESH_INTERVAL = 300
ALERT_MINUTES    = 5
CUSTOM_SOUND     = _beside_exe("alert.wav")
LOGO_FILE        = _bundled("logo.png")
LOGO_SIZE        = 26

# Layout constants
H       = 36
HPAD    = 10
SEP_W   = 14
CLOSE_W = 20

HELLTIDE_DURATION = 55 * 60


def _version_tuple(v: str):
    return tuple(int(x) for x in v.strip("v").split("."))


class OverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        # ── Colors ──────────────────────────────
        self.bg          = "#0a0a0a"
        self.border      = "#8b0000"
        self.col_gold    = "#ffcc00"
        self.col_red     = "#ef4444"
        self.col_gray    = "#a1a1aa"
        self.col_dim     = "#3f3f46"
        self.col_update  = "#22c55e"   # green for update button
        self.transparent = "#fe00fe"

        # ── State ────────────────────────────────
        self.next_boss      = None
        self.next_helltide  = None
        self.alerted_id     = None
        self.update_tag     = None     # set when update is available
        self._drag_x = self._drag_y = 0
        self.W = 400

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

        self.LOGO_BOX_W = (LOGO_SIZE + 8) if self.logo_img else 0

        # ── Window setup ─────────────────────────
        self.root.geometry(f"{self.W}x{H}+20+20")
        self.root.config(bg=self.transparent)
        self.root.wm_attributes("-transparentcolor", self.transparent)

        # ── Canvas ───────────────────────────────
        self.cv = tk.Canvas(
            self.root, width=self.W, height=H,
            bg=self.transparent, highlightthickness=0
        )
        self.cv.pack(fill="both", expand=True)

        self.bg_rect = self.cv.create_rectangle(
            1, 1, self.W - 1, H - 1,
            fill=self.bg, outline=self.border, width=2
        )

        self.wb_item = self.cv.create_text(
            HPAD, H // 2, text="Loading...",
            anchor="w", font=("Consolas", 12, "bold"), fill=self.col_gold
        )

        self.sep_item = self.cv.create_text(
            0, H // 2, text="║",
            anchor="center", font=("Consolas", 12, "bold"), fill=self.col_dim
        )

        self.ht_item = self.cv.create_text(
            0, H // 2, text="HT: ...",
            anchor="w", font=("Consolas", 12, "bold"), fill=self.col_gray
        )

        # Update button (hidden until update available)
        self.update_btn = self.cv.create_text(
            0, H // 2, text="↑",
            anchor="center", font=("Segoe UI", 11, "bold"),
            fill=self.col_update, activefill="#4ade80", state="hidden"
        )
        self.cv.tag_bind(self.update_btn, "<Button-1>", self._on_update_click)

        # Logo
        self.logo_border_id = None
        self.logo_img_id    = None
        if self.logo_img:
            self.logo_border_id = self.cv.create_rectangle(
                0, 4, LOGO_SIZE + 8, H - 4,
                fill="#111111", outline=self.border, width=1
            )
            self.logo_img_id = self.cv.create_image(
                0, H // 2, image=self.logo_img, anchor="center"
            )

        self.close_btn = self.cv.create_text(
            0, H // 2, text="✕",
            anchor="center", font=("Segoe UI", 11, "bold"),
            fill=self.col_dim, activefill="#ef4444"
        )
        self.cv.tag_bind(self.close_btn, "<Button-1>", self._quit)

        self.cv.bind("<ButtonPress-1>",   self._drag_start)
        self.cv.bind("<ButtonRelease-1>", self._drag_stop)
        self.cv.bind("<B1-Motion>",       self._drag_move)

        threading.Thread(target=self._fetch_loop, daemon=True).start()
        threading.Thread(target=self._update_check_loop, daemon=True).start()
        self._tick()

    # ── Layout ──────────────────────────────────
    def _relayout(self):
        wb_bbox = self.cv.bbox(self.wb_item)
        ht_bbox = self.cv.bbox(self.ht_item)
        if not wb_bbox or not ht_bbox:
            return

        wb_w = wb_bbox[2] - wb_bbox[0]
        ht_w = ht_bbox[2] - ht_bbox[0]

        x = HPAD

        wb_x  = x;  x += wb_w + HPAD
        sep_x = x + SEP_W // 2;  x += SEP_W + HPAD
        ht_x  = x;  x += ht_w + HPAD

        # Update button (only visible when update available)
        upd_x = None
        if self.update_tag:
            upd_x = x + 10
            x += 20 + HPAD

        if self.logo_img:
            logo_left = x
            logo_cx   = x + self.LOGO_BOX_W // 2
            x += self.LOGO_BOX_W + HPAD

        close_x = x + CLOSE_W // 2
        x += CLOSE_W + HPAD // 2

        new_w = x

        self.cv.coords(self.wb_item,   wb_x,   H // 2)
        self.cv.coords(self.sep_item,  sep_x,  H // 2)
        self.cv.coords(self.ht_item,   ht_x,   H // 2)
        self.cv.coords(self.close_btn, close_x, H // 2)

        if upd_x is not None:
            self.cv.coords(self.update_btn, upd_x, H // 2)
            self.cv.itemconfig(self.update_btn, state="normal")
        else:
            self.cv.itemconfig(self.update_btn, state="hidden")

        if self.logo_img:
            self.cv.coords(self.logo_border_id,
                           logo_left, 4, logo_left + self.LOGO_BOX_W, H - 4)
            self.cv.coords(self.logo_img_id, logo_cx, H // 2)

        if new_w != self.W:
            self.W = new_w
            self.cv.config(width=new_w)
            self.cv.coords(self.bg_rect, 1, 1, new_w - 1, H - 1)
            x_pos = self.root.winfo_x()
            y_pos = self.root.winfo_y()
            self.root.geometry(f"{new_w}x{H}+{x_pos}+{y_pos}")

    # ── Drag ────────────────────────────────────
    def _drag_start(self, e):
        if e.x > self.W - (CLOSE_W + HPAD):
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
            req  = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
            data = json.loads(urllib.request.urlopen(req).read())
            now  = time.time()

            for ev in data.get("world_boss", []):
                if ev["timestamp"] > now:
                    self.next_boss = ev
                    break

            for ev in data.get("helltide", []):
                if ev["timestamp"] + HELLTIDE_DURATION > now:
                    self.next_helltide = ev
                    break
        except Exception as e:
            print(f"[fetch error] {e}")

    # ── Auto-update ─────────────────────────────
    def _update_check_loop(self):
        time.sleep(5)   # wait for UI to settle first
        while True:
            self._check_update()
            time.sleep(3600)    # re-check every hour

    def _check_update(self):
        try:
            req  = urllib.request.Request(
                GITHUB_API_URL, headers={"User-Agent": "Mozilla/5.0"}
            )
            data = json.loads(urllib.request.urlopen(req).read())
            tag  = data.get("tag_name", "")
            if not tag:
                return
            if _version_tuple(tag) > _version_tuple(VERSION):
                self.update_tag = tag
                print(f"[updater] New version available: {tag}")
        except Exception as e:
            print(f"[updater check error] {e}")

    def _on_update_click(self, _=None):
        if not self.update_tag:
            return
        tag = self.update_tag
        ans = msgbox.askyesno(
            "Update available",
            f"Version {tag} is available (you have v{VERSION}).\n\nDownload and install now?",
            parent=self.root
        )
        if ans:
            threading.Thread(target=self._do_update, args=(tag,), daemon=True).start()

    def _do_update(self, tag: str):
        try:
            exe_name = "D4-Overlay.exe"
            dl_url   = (
                f"https://github.com/{GITHUB_REPO}/releases/download/"
                f"{tag}/{exe_name}"
            )

            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                # Running as .py — nothing to replace, just open browser
                import webbrowser
                webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
                return

            # Download to temp file next to exe
            exe_dir  = os.path.dirname(current_exe)
            tmp_path = os.path.join(exe_dir, "D4-Overlay_update.exe")

            self.root.after(0, lambda: self.cv.itemconfig(
                self.update_btn, text="↓", fill="#facc15"
            ))

            req = urllib.request.Request(dl_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp, open(tmp_path, "wb") as f:
                f.write(resp.read())

            # Write a helper batch that replaces exe after we exit
            bat_path = os.path.join(exe_dir, "_d4_update.bat")
            with open(bat_path, "w") as f:
                f.write(
                    f"@echo off\n"
                    f"timeout /t 2 /nobreak >nul\n"
                    f"move /y \"{tmp_path}\" \"{current_exe}\"\n"
                    f"start \"\" \"{current_exe}\"\n"
                    f"del \"%~f0\"\n"
                )

            subprocess.Popen(
                ["cmd", "/c", bat_path],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.root.destroy()
            sys.exit(0)

        except Exception as e:
            print(f"[updater download error] {e}")
            msgbox.showerror("Update failed", str(e), parent=self.root)

    # ── Sound ───────────────────────────────────
    def _play_sound(self):
        if os.path.exists(CUSTOM_SOUND):
            winsound.PlaySound(CUSTOM_SOUND,
                               winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            winsound.PlaySound("SystemAsterisk",
                               winsound.SND_ALIAS | winsound.SND_ASYNC)

    # ── UI tick ─────────────────────────────────
    def _tick(self):
        now = time.time()

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

                if left <= ALERT_MINUTES * 60 and self.alerted_id != self.next_boss["id"]:
                    self._play_sound()
                    self.alerted_id = self.next_boss["id"]
            else:
                self.cv.itemconfig(self.wb_item,
                                   text="⚔  World Boss Active!", fill=self.col_red)
        else:
            self.cv.itemconfig(self.wb_item, text="WB: connecting...", fill=self.col_gray)

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

        self._relayout()
        self.root.after(1000, self._tick)


if __name__ == "__main__":
    root = tk.Tk()
    OverlayApp(root)
    root.mainloop()
