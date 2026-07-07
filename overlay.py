import tkinter as tk
from tkinter import ttk
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
import ctypes
import psutil
import keyboard
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

class ModernSlider(tk.Canvas):
    def __init__(self, parent, width, height, bg, trough, fill_color, slider, command=None, initial=100):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0)
        self.command = command
        self.val = initial
        self.c_trough = trough
        self.c_fill = fill_color
        self.c_slider = slider
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self._draw()

    def _draw(self):
        self.delete("all")
        w, h = int(self['width']), int(self['height'])
        x = 10 + (self.val - 10) / 90 * (w - 20)
        
        # Empty track
        self.create_line(10, h//2, w-10, h//2, fill=self.c_trough, width=4, capstyle="round")
        # Filled track
        self.create_line(10, h//2, x, h//2, fill=self.c_fill, width=4, capstyle="round")
        # Handle
        self.create_oval(x-7, h//2-7, x+7, h//2+7, fill=self.c_slider, outline="")

    def _update_val(self, x):
        w = int(self['width'])
        x = max(10, min(w-10, x))
        self.val = int(10 + (x - 10) / (w - 20) * 90)
        self._draw()
        if self.command:
            self.command(self.val)

    def _on_click(self, e): self._update_val(e.x)
    def _on_drag(self, e): self._update_val(e.x)

# ─────────────────────────────────────────
# Configuration & Constants
# ─────────────────────────────────────────
APP_NAME    = "Diablo 4 Overlay"
VERSION     = "1.5.0"
GITHUB_REPO = "uh616/d4-world-boss-overlay"

API_URL          = "https://helltides.com/api/schedule"
GITHUB_API_URL   = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
REFRESH_INTERVAL = 300
CUSTOM_SOUND     = _beside_exe("alert.wav")
LOGO_FILE        = _bundled("logo.png")
LOGO_SIZE        = 26
CONFIG_FILE      = _beside_exe("config.json")

H       = 36
HPAD    = 10
SEP_W   = 14
BTN_W   = 20

HELLTIDE_DURATION = 55 * 60

# Windows API Constants for Click-through
GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000

STRINGS = {
    "en": {
        "settings_title": "⚙ Settings",
        "alert_time":     "Alert Time:",
        "mins":           "mins",
        "sound":          "Sound Alerts:",
        "auto_hide":      "Auto-hide on focus",
        "theme":          "Theme:",
        "opacity":        "Opacity:",
        "display":        "Display",
        "world_boss":     "World Boss",
        "helltide":       "Helltide",
        "legion":         "Legion",
        "language":       "Language:",
        "custom_sound":   "Custom Sound:",
        "browse":         "Browse...",
        "volume":         "Volume:",
        "test":           "Test",
        "hotkey":         "Lock Hotkey:",
        "bind_click":     "Click to Bind",
        "press_key":      "Press any key...",
        "tip":            "Tip: Use Lock Hotkey to enable click-through",
        "support":        "❤️ Support",
    },
    "ru": {
        "settings_title": "⚙ Настройки",
        "alert_time":     "Оповещение:",
        "mins":           "мин",
        "sound":          "Звук (за Х мин):",
        "auto_hide":      "Авто-скрытие",
        "theme":          "Тема:",
        "opacity":        "Прозрачность:",
        "display":        "Отображение",
        "world_boss":     "World Boss",
        "helltide":       "Helltide",
        "legion":         "Legion",
        "language":       "Язык:",
        "custom_sound":   "Свой звук:",
        "browse":         "Выбрать...",
        "volume":         "Громкость:",
        "test":           "Тест",
        "hotkey":         "Блок оверлея:",
        "bind_click":     "Изменить",
        "press_key":      "Нажмите клавишу...",
        "tip":            "Совет: Заблокируйте окно для кликов сквозь",
        "support":        "❤️ Поддержать",
    }
}

THEMES = {
    "Default Crimson": {"wb": "#ffcc00", "active": "#ef4444", "idle": "#a1a1aa", "border": "#8b0000"},
    "Neon Blue":       {"wb": "#38bdf8", "active": "#818cf8", "idle": "#94a3b8", "border": "#1e3a8a"},
    "Gold":            {"wb": "#fde047", "active": "#f59e0b", "idle": "#d6d3d1", "border": "#b45309"}
}

def _version_tuple(v: str):
    return tuple(int(x) for x in v.strip("v").split("."))

class OverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        
        self.hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())

        # ── Load Config ──────────────────────────
        self.config = {
            "alert_minutes": 5,
            "sound_wb": True,
            "sound_ht": False,
            "sound_legion": False,
            "sound_file": "",
            "sound_volume": 100,
            "hotkey": "ctrl+l",
            "auto_hide": False,
            "theme": "Default Crimson",
            "show_boss": True,
            "show_helltide": True,
            "show_legion": True,
            "opacity": 0.9,
            "pos_x": 20,
            "pos_y": 20,
            "language": "en",
        }
        self._load_config()
        if "sound_enabled" in self.config:
            self.config["sound_wb"] = self.config.pop("sound_enabled")
            self._save_config()

        # ── State ────────────────────────────────
        self.next_boss      = None
        self.next_helltide  = None
        self.next_legion    = None
        self.alerted_id     = None
        self.alerted_ht_id  = None
        self.alerted_lg_id  = None
        self.update_tag     = None
        self.locked         = False
        self.is_hidden      = False
        self.mini_mode      = False
        self._drag_x = self._drag_y = 0
        self.W = 400

        # ── Colors ──────────────────────────────
        self.bg          = "#0a0a0a"
        self.col_dim     = "#3f3f46"
        self.col_update  = "#22c55e"
        self.transparent = "#fe00fe"

        # ── Load logo ────────────────────────────
        self.logo_img = None
        if os.path.exists(LOGO_FILE):
            try:
                img = Image.open(LOGO_FILE).resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
            except Exception:
                pass

        self.LOGO_BOX_W = (LOGO_SIZE + 8) if self.logo_img else 0

        # ── Window setup ─────────────────────────
        px = self.config.get("pos_x", 20)
        py = self.config.get("pos_y", 20)
        self.root.geometry(f"{self.W}x{H}+{px}+{py}")
        self.root.config(bg=self.transparent)
        self.root.wm_attributes("-transparentcolor", self.transparent)

        # ── Canvas ───────────────────────────────
        self.cv = tk.Canvas(self.root, width=self.W, height=H, bg=self.transparent, highlightthickness=0)
        self.cv.pack(fill="both", expand=True)

        self.bg_rect = self.cv.create_rectangle(1, 1, self.W - 1, H - 1, fill=self.bg, width=2)

        font_main = ("Consolas", 12, "bold")
        font_icon = ("Segoe UI", 11, "bold")

        self.wb_item  = self.cv.create_text(HPAD, H // 2, text="Loading...", anchor="w", font=font_main)
        self.sep_1    = self.cv.create_text(0, H // 2, text="║", anchor="center", font=font_main, fill=self.col_dim)
        self.ht_item  = self.cv.create_text(0, H // 2, text="HT: ...", anchor="w", font=font_main)
        self.sep_2    = self.cv.create_text(0, H // 2, text="║", anchor="center", font=font_main, fill=self.col_dim)
        self.lg_item  = self.cv.create_text(0, H // 2, text="LG: ...", anchor="w", font=font_main)

        # Settings button
        self.settings_btn = self.cv.create_text(0, H // 2, text="⚙", anchor="center", font=font_icon, fill=self.col_dim, activefill="#ffffff")
        self.cv.tag_bind(self.settings_btn, "<Button-1>", self._open_settings)

        # Logo
        self.logo_border_id = None
        self.logo_img_id    = None
        if self.logo_img:
            self.logo_border_id = self.cv.create_rectangle(0, 4, LOGO_SIZE + 8, H - 4, fill="#111111", width=1)
            self.logo_img_id = self.cv.create_image(0, H // 2, image=self.logo_img, anchor="center")
            self.cv.tag_bind(self.logo_img_id,    "<Button-1>", self._toggle_mini)
            self.cv.tag_bind(self.logo_border_id, "<Button-1>", self._toggle_mini)

        # Close button
        self.close_btn = self.cv.create_text(0, H // 2, text="✕", anchor="center", font=font_icon, fill=self.col_dim, activefill="#ef4444")
        self.cv.tag_bind(self.close_btn, "<Button-1>", self._quit)

        # Lock indicator (hidden by default)
        self.lock_indicator = self.cv.create_text(0, H // 2, text="🔒", anchor="center", font=("Segoe UI", 9), fill="#ffffff", state="hidden")

        self.cv.bind("<ButtonPress-1>", self._drag_start)
        self.cv.bind("<ButtonRelease-1>", self._drag_stop)
        self.cv.bind("<B1-Motion>", self._drag_move)

        self._apply_theme()

        # Keyboard Hook for Lock Mode
        keyboard.add_hotkey(self.config.get("hotkey", "ctrl+l"), self._toggle_lock)

        threading.Thread(target=self._fetch_loop, daemon=True).start()
        threading.Thread(target=self._update_check_loop, daemon=True).start()
        if self.config["auto_hide"]:
            threading.Thread(target=self._auto_hide_loop, daemon=True).start()
        
        self._tick()

    # ── Config ──────────────────────────────────
    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.config.update(json.load(f))
            except: pass

    def _save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except: pass

    def _apply_theme(self):
        t = THEMES.get(self.config["theme"], THEMES["Default Crimson"])
        self.cv.itemconfig(self.bg_rect, outline=t["border"])
        if self.logo_border_id:
            self.cv.itemconfig(self.logo_border_id, outline=t["border"])
        self.root.attributes("-alpha", self.config.get("opacity", 0.9))
        self._relayout() # forces redraw with new colors in tick

    # ── Settings UI ─────────────────────────────
    def _open_settings(self, _=None):
        if self.locked: return
        if hasattr(self, "settings_win") and self.settings_win.winfo_exists():
            self.settings_win.lift()
            return

        BG    = "#0d0d0f"
        CARD  = "#1c1c1e"
        CARD2 = "#2c2c2e"
        SEP   = "#3a3a3c"
        FG    = "#ffffff"
        FG2   = "#ebebf5"
        FG3   = "#8e8e93"
        ACCENT= "#0a84ff"
        GREEN = "#30d158"
        ORANGE= "#ff9f0a"
        RED   = "#ff453a"
        import tkinter.font as tkfont
        FONT  = "SF Pro Display" if "SF Pro Display" in tkfont.families() else "Segoe UI"

        win = tk.Toplevel(self.root)
        self.settings_win = win
        win.title("Settings")
        win.geometry("360x780")
        win.resizable(False, False)
        win.configure(bg=BG)
        win.wm_attributes("-topmost", True)

        if self.logo_img:
            win.iconphoto(False, self.logo_img)

        # Apply Windows Acrylic blur
        try:
            win.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
            if hwnd == 0:
                hwnd = win.winfo_id()

            class ACCENTPOLICY(ctypes.Structure):
                _fields_ = [("AccentState", ctypes.c_uint), ("AccentFlags", ctypes.c_uint),
                             ("GradientColor", ctypes.c_uint), ("AnimationId", ctypes.c_uint)]
            class WCAD(ctypes.Structure):
                _fields_ = [("Attribute", ctypes.c_int),
                             ("Data", ctypes.POINTER(ctypes.c_int)), ("SizeOfData", ctypes.c_size_t)]
            policy = ACCENTPOLICY()
            policy.AccentState = 4
            policy.GradientColor = 0xCC0d0d0f
            data = WCAD()
            data.Attribute = 19
            data.Data = ctypes.cast(ctypes.pointer(policy), ctypes.POINTER(ctypes.c_int))
            data.SizeOfData = ctypes.sizeof(policy)
            ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
        except Exception as e:
            pass

        s = STRINGS.get(self.config.get("language", "en"), STRINGS["en"])

        alert_var    = tk.IntVar(value=self.config.get("alert_minutes", 5))
        sound_wb_var = tk.BooleanVar(value=self.config.get("sound_wb", True))
        sound_ht_var = tk.BooleanVar(value=self.config.get("sound_ht", False))
        sound_lg_var = tk.BooleanVar(value=self.config.get("sound_legion", False))
        hide_var     = tk.BooleanVar(value=self.config.get("auto_hide", False))
        boss_var     = tk.BooleanVar(value=self.config.get("show_boss", True))
        ht_var       = tk.BooleanVar(value=self.config.get("show_helltide", True))
        legion_var   = tk.BooleanVar(value=self.config.get("show_legion", True))
        opacity_var  = tk.IntVar(value=int(self.config.get("opacity", 0.9) * 100))
        vol_var      = tk.IntVar(value=self.config.get("sound_volume", 100))
        theme_var    = tk.StringVar(value=self.config.get("theme", "Default Crimson"))
        lang_var     = tk.StringVar(value=self.config.get("language", "en"))
        valid_times  = [1, 5, 10, 15]
        if alert_var.get() not in valid_times: alert_var.set(5)
        themes_list  = list(THEMES.keys())
        langs_list   = ["en", "ru"]
        lang_labels  = {"en": "English", "ru": "\u0420\u0443\u0441\u0441\u043a\u0438\u0439"}

        def _auto_save():
            self.config["alert_minutes"] = alert_var.get()
            self.config["sound_wb"]      = sound_wb_var.get()
            self.config["sound_ht"]      = sound_ht_var.get()
            self.config["sound_legion"]  = sound_lg_var.get()
            self.config["auto_hide"]     = hide_var.get()
            self.config["theme"]         = theme_var.get()
            self.config["show_boss"]     = boss_var.get()
            self.config["show_helltide"] = ht_var.get()
            self.config["show_legion"]   = legion_var.get()
            self.config["opacity"]       = opacity_var.get() / 100.0
            self.config["language"]      = lang_var.get()
            self._save_config()
            self._apply_theme()
            if self.config["auto_hide"] and not getattr(self, "_auto_hide_running", False):
                self._auto_hide_running = True
                threading.Thread(target=self._auto_hide_loop, daemon=True).start()

        # ── iOS helpers ──────────────────────────────────
        def section_label(parent, text):
            if not text:
                tk.Frame(parent, bg=BG, height=6).pack()
                return
            tk.Label(parent, text=text.upper(), font=(FONT, 8, "bold"), bg=BG, fg=FG3,
                     anchor="w").pack(fill="x", padx=20, pady=(14, 4))

        def card(parent):
            f = tk.Frame(parent, bg=CARD, bd=0, highlightthickness=1, highlightbackground=SEP)
            f.pack(fill="x", padx=16, pady=0)
            return f

        def row_frame(card_f, last=False):
            r = tk.Frame(card_f, bg=CARD)
            r.pack(fill="x")
            if not last:
                sep = tk.Frame(card_f, bg=SEP, height=1)
                sep.pack(fill="x", padx=14)
            return r

        def ios_label(parent, text):
            lbl = tk.Label(parent, text=text, font=(FONT, 11), bg=CARD, fg=FG2, anchor="w")
            lbl.pack(side="left", padx=(16, 6), pady=13)
            return lbl

        def ios_toggle(parent, var):
            TRACK_W, TRACK_H, KNOB_D = 44, 24, 20
            c = tk.Canvas(parent, width=TRACK_W, height=TRACK_H, bg=CARD,
                          highlightthickness=0, cursor="hand2")
            c.pack(side="right", padx=(0, 14), pady=10)
            def _draw():
                c.delete("all")
                color = GREEN if var.get() else SEP
                r = TRACK_H // 2
                c.create_arc(0, 0, TRACK_H, TRACK_H, start=90, extent=180, fill=color, outline=color)
                c.create_arc(TRACK_W-TRACK_H, 0, TRACK_W, TRACK_H, start=270, extent=180, fill=color, outline=color)
                c.create_rectangle(r, 0, TRACK_W-r, TRACK_H, fill=color, outline=color)
                knob_x = TRACK_W-2-KNOB_D if var.get() else 2
                c.create_oval(knob_x, 2, knob_x+KNOB_D, 2+KNOB_D, fill=FG, outline="")
            def _toggle(e):
                var.set(not var.get()); _draw(); _auto_save()
            _draw()
            c.bind("<Button-1>", _toggle)

        # ── Scrollable container ─────────────────────────
        outer = tk.Frame(win, bg=BG)
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0, bd=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview, bg=BG)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        sf = tk.Frame(canvas, bg=BG)
        sw = canvas.create_window((0, 0), window=sf, anchor="nw", width=360)
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        win.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # ─── HEADER ─────────────────────────────────────
        tk.Label(sf, text="\u2699  Settings", font=(FONT, 20, "bold"), bg=BG, fg=FG).pack(pady=(22, 6))

        # ─── NOTIFICATIONS ───────────────────────────────
        section_label(sf, "Notifications")
        c1 = card(sf)
        r_alert = row_frame(c1)
        ios_label(r_alert, s["alert_time"])
        af = tk.Frame(r_alert, bg=CARD)
        af.pack(side="right", padx=(0,14), pady=8)
        def chg_alert(d):
            idx = valid_times.index(alert_var.get())
            alert_var.set(valid_times[(idx+d) % len(valid_times)])
            lbl_av.config(text=f"{alert_var.get()} {s['mins']}")
            _auto_save()
        btn_al = tk.Label(af, text="\u2039", font=(FONT,18), bg=CARD, fg=ACCENT, cursor="hand2")
        btn_al.pack(side="left")
        btn_al.bind("<Button-1>", lambda _: chg_alert(-1))
        lbl_av = tk.Label(af, text=f"{alert_var.get()} {s['mins']}", font=(FONT,11,"bold"), bg=CARD2, fg=FG2, padx=10, pady=2)
        lbl_av.pack(side="left", padx=4)
        btn_ar = tk.Label(af, text="\u203a", font=(FONT,18), bg=CARD, fg=ACCENT, cursor="hand2")
        btn_ar.pack(side="left")
        btn_ar.bind("<Button-1>", lambda _: chg_alert(1))

        r_swb = row_frame(c1)
        ios_label(r_swb, "\U0001f514 " + s["world_boss"])
        ios_toggle(r_swb, sound_wb_var)
        r_sht = row_frame(c1)
        ios_label(r_sht, "\U0001f514 " + s["helltide"])
        ios_toggle(r_sht, sound_ht_var)
        r_slg = row_frame(c1, last=True)
        ios_label(r_slg, "\U0001f514 " + s["legion"])
        ios_toggle(r_slg, sound_lg_var)

        # ─── AUDIO ───────────────────────────────────────
        section_label(sf, "Audio")
        c2 = card(sf)
        r_sf = row_frame(c2)
        ios_label(r_sf, s["custom_sound"])
        def _pick_file(_):
            fpath = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")], title="Select Alert Sound")
            if fpath:
                self.config["sound_file"] = fpath; self._save_config()
                lbl_sfile.config(text="\u2713 Custom", fg=GREEN)
            else:
                self.config["sound_file"] = ""; self._save_config()
                lbl_sfile.config(text=s["browse"], fg=FG3)
        lbl_sfile = tk.Label(r_sf, text="\u2713 Custom" if self.config.get("sound_file") else s["browse"],
                             font=(FONT,11), bg=CARD, fg=GREEN if self.config.get("sound_file") else FG3, cursor="hand2")
        lbl_sfile.pack(side="right", padx=(0,4), pady=13)
        lbl_sfile.bind("<Button-1>", _pick_file)
        tk.Label(r_sf, text="\u203a", font=(FONT,14), bg=CARD, fg=FG3).pack(side="right", padx=(0,6))

        r_test = row_frame(c2)
        ios_label(r_test, "\u25b6  " + s["test"] + " sound")
        def _test_sound(_): self._play_sound()
        lbl_t = tk.Label(r_test, text=s["test"], font=(FONT,11,"bold"), bg=CARD, fg=ACCENT, cursor="hand2")
        lbl_t.pack(side="right", padx=(0,4), pady=13)
        lbl_t.bind("<Button-1>", _test_sound)
        tk.Label(r_test, text="\u203a", font=(FONT,14), bg=CARD, fg=ACCENT).pack(side="right", padx=(0,6))

        r_vol = row_frame(c2, last=True)
        ios_label(r_vol, "\U0001f50a " + s["volume"])
        vf = tk.Frame(r_vol, bg=CARD)
        vf.pack(side="right", padx=(0,14), pady=8)
        def on_vol(val):
            vol_var.set(val); self.config["sound_volume"] = val; self._save_config()
            lbl_vv.config(text=f"{val}%")
        sl_v = ModernSlider(vf, width=90, height=26, bg=CARD, trough=SEP,
                            fill_color=ACCENT, slider=FG, command=on_vol, initial=vol_var.get())
        sl_v.pack(side="left", padx=(0,4))
        lbl_vv = tk.Label(vf, text=f"{vol_var.get()}%", font=(FONT,10,"bold"), bg=CARD, fg=FG3, width=4)
        lbl_vv.pack(side="left")

        # ─── DISPLAY ─────────────────────────────────────
        section_label(sf, s["display"])
        c3 = card(sf)
        r_b = row_frame(c3); ios_label(r_b, "\U0001f479 " + s["world_boss"]); ios_toggle(r_b, boss_var)
        r_h = row_frame(c3); ios_label(r_h, "\U0001f525 " + s["helltide"]);   ios_toggle(r_h, ht_var)
        r_l = row_frame(c3); ios_label(r_l, "\u26a1 " + s["legion"]);          ios_toggle(r_l, legion_var)
        r_hd = row_frame(c3, last=True); ios_label(r_hd, "\U0001f441 " + s["auto_hide"]); ios_toggle(r_hd, hide_var)

        # ─── APPEARANCE ──────────────────────────────────
        section_label(sf, "Appearance")
        c4 = card(sf)
        r_th = row_frame(c4)
        ios_label(r_th, "\U0001f3a8 " + s["theme"])
        thf = tk.Frame(r_th, bg=CARD)
        thf.pack(side="right", padx=(0,14), pady=8)
        def chg_theme(d):
            theme_var.set(themes_list[(themes_list.index(theme_var.get())+d) % len(themes_list)])
            lbl_tv.config(text=theme_var.get()); _auto_save()
        btn_tl = tk.Label(thf, text="\u2039", font=(FONT,18), bg=CARD, fg=ACCENT, cursor="hand2")
        btn_tl.pack(side="left")
        btn_tl.bind("<Button-1>", lambda _: chg_theme(-1))
        lbl_tv = tk.Label(thf, text=theme_var.get(), font=(FONT,10,"bold"), bg=CARD2, fg=FG2, padx=8, pady=2)
        lbl_tv.pack(side="left", padx=4)
        btn_tr = tk.Label(thf, text="\u203a", font=(FONT,18), bg=CARD, fg=ACCENT, cursor="hand2")
        btn_tr.pack(side="left")
        btn_tr.bind("<Button-1>", lambda _: chg_theme(1))

        r_op = row_frame(c4)
        ios_label(r_op, "\U0001f4a7 " + s["opacity"])
        opf = tk.Frame(r_op, bg=CARD)
        opf.pack(side="right", padx=(0,14), pady=8)
        def on_op(val):
            opacity_var.set(val); lbl_ov.config(text=f"{val}%"); _auto_save()
        sl_op = ModernSlider(opf, width=90, height=26, bg=CARD, trough=SEP,
                             fill_color=ORANGE, slider=FG, command=on_op, initial=opacity_var.get())
        sl_op.pack(side="left", padx=(0,4))
        lbl_ov = tk.Label(opf, text=f"{opacity_var.get()}%", font=(FONT,10,"bold"), bg=CARD, fg=FG3, width=4)
        lbl_ov.pack(side="left")

        r_lg = row_frame(c4, last=True)
        ios_label(r_lg, "\U0001f310 " + s["language"])
        lgf = tk.Frame(r_lg, bg=CARD)
        lgf.pack(side="right", padx=(0,14), pady=8)
        def chg_lang(d):
            lang_var.set(langs_list[(langs_list.index(lang_var.get())+d) % len(langs_list)])
            lbl_lv.config(text=lang_labels[lang_var.get()]); _auto_save()
        btn_ll = tk.Label(lgf, text="\u2039", font=(FONT,18), bg=CARD, fg=ACCENT, cursor="hand2")
        btn_ll.pack(side="left")
        btn_ll.bind("<Button-1>", lambda _: chg_lang(-1))
        lbl_lv = tk.Label(lgf, text=lang_labels[lang_var.get()], font=(FONT,10,"bold"), bg=CARD2, fg=FG2, padx=8, pady=2)
        lbl_lv.pack(side="left", padx=4)
        btn_lr = tk.Label(lgf, text="\u203a", font=(FONT,18), bg=CARD, fg=ACCENT, cursor="hand2")
        btn_lr.pack(side="left")
        btn_lr.bind("<Button-1>", lambda _: chg_lang(1))

        # ─── HOTKEY ──────────────────────────────────────
        section_label(sf, s["hotkey"].rstrip(":"))
        c5 = card(sf)
        r_hk = row_frame(c5, last=True)
        ios_label(r_hk, "\u2328\ufe0f  " + s["hotkey"])
        hkf = tk.Frame(r_hk, bg=CARD)
        hkf.pack(side="right", padx=(0,14), pady=8)
        lbl_hkv = tk.Label(hkf, text=self.config.get("hotkey", "ctrl+l").upper(),
                            font=(FONT,10,"bold"), bg=CARD2, fg=FG2, padx=10, pady=3)
        lbl_hkv.pack(side="left", padx=(0,6))
        _hk_listening = [False]  # mutable flag to prevent double clicks

        def _listen_hotkey(_):
            if _hk_listening[0]: return  # already waiting for a key
            _hk_listening[0] = True
            lbl_hkv.config(text=s["press_key"], fg=ORANGE)
            btn_hkb.config(fg="#555555")  # dim button while listening

            def _do_listen():
                try:
                    hk = keyboard.read_hotkey(suppress=False)
                    # Skip if same hotkey — just restore label
                    if hk == self.config.get("hotkey", "ctrl+l"):
                        win.after(0, lambda: lbl_hkv.config(
                            text=hk.upper(), fg=FG2))
                    else:
                        try:
                            keyboard.remove_hotkey(self._toggle_lock)
                        except Exception:
                            pass
                        self.config["hotkey"] = hk
                        self._save_config()
                        keyboard.add_hotkey(hk, self._toggle_lock)
                        win.after(0, lambda: lbl_hkv.config(
                            text=hk.upper(), fg=FG2))
                except Exception:
                    win.after(0, lambda: lbl_hkv.config(text="ERROR", fg=RED))
                finally:
                    _hk_listening[0] = False
                    win.after(0, lambda: btn_hkb.config(fg=ACCENT))

            threading.Thread(target=_do_listen, daemon=True).start()

        btn_hkb = tk.Label(hkf, text=s["bind_click"], font=(FONT,10), bg=CARD, fg=ACCENT, cursor="hand2")
        btn_hkb.pack(side="left")
        btn_hkb.bind("<Button-1>", _listen_hotkey)

        # ─── SUPPORT ─────────────────────────────────────
        section_label(sf, "")
        c6 = card(sf)
        r_sup = row_frame(c6, last=True)
        ios_label(r_sup, "\u2764\ufe0f  " + s["support"].replace("\u2764\ufe0f ", ""))
        import webbrowser
        def open_support(_): webbrowser.open("https://boosty.to/6i6")
        lbl_su = tk.Label(r_sup, text="\u203a", font=(FONT,16), bg=CARD, fg=RED, cursor="hand2")
        lbl_su.pack(side="right", padx=(0,14), pady=13)
        lbl_su.bind("<Button-1>", open_support)
        r_sup.bind("<Button-1>", open_support)

        tk.Label(sf, text=s["tip"], font=(FONT, 9), bg=BG, fg=FG3).pack(pady=(12, 24))


    # ── Auto-hide ───────────────────────────────
    def _auto_hide_loop(self):
        user32 = ctypes.windll.user32
        my_pid = os.getpid()
        
        while self.config["auto_hide"]:
            hwnd = user32.GetForegroundWindow()
            fg_pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(fg_pid))
            
            is_active = False
            if fg_pid.value == my_pid:
                is_active = True
            elif fg_pid.value > 0:
                try:
                    p = psutil.Process(fg_pid.value)
                    if p.name() == "Diablo IV.exe":
                        is_active = True
                except:
                    pass
                    
            if is_active and self.is_hidden:
                self.root.deiconify()
                self.is_hidden = False
            elif not is_active and not self.is_hidden:
                self.root.withdraw()
                self.is_hidden = True
            time.sleep(1)
            
    # ── Click-through Lock ──────────────────────
    def _toggle_lock(self):
        self.locked = not self.locked
        ex_style = ctypes.windll.user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
        if self.locked:
            ctypes.windll.user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, ex_style | WS_EX_TRANSPARENT | WS_EX_LAYERED)
            self.root.after(0, lambda: self.cv.itemconfig(self.lock_indicator, state="normal"))
            self.root.after(0, lambda: self.cv.itemconfig(self.close_btn, state="hidden"))
            self.root.after(0, lambda: self.cv.itemconfig(self.settings_btn, state="hidden"))
        else:
            ctypes.windll.user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, ex_style & ~WS_EX_TRANSPARENT)
            self.root.after(0, lambda: self.cv.itemconfig(self.lock_indicator, state="hidden"))
            self.root.after(0, lambda: self.cv.itemconfig(self.close_btn, state="normal"))
            self.root.after(0, lambda: self.cv.itemconfig(self.settings_btn, state="normal"))

    # ── Layout ──────────────────────────────────
    def _relayout(self):
        show_boss     = self.config.get("show_boss", True)
        show_helltide = self.config.get("show_helltide", True)
        show_legion   = self.config.get("show_legion", True)

        mini = self.mini_mode

        # Show/hide items
        self.cv.itemconfig(self.wb_item,  state="normal" if show_boss     else "hidden")
        self.cv.itemconfig(self.ht_item,  state="normal" if show_helltide else "hidden")
        self.cv.itemconfig(self.lg_item,  state="normal" if show_legion   else "hidden")
        self.cv.itemconfig(self.sep_1,    state="normal" if (show_boss and show_helltide and not mini) else "hidden")
        self.cv.itemconfig(self.sep_2,    state="normal" if ((show_helltide and show_legion) or (show_boss and show_legion and not show_helltide)) and not mini else "hidden")

        wb_bbox = self.cv.bbox(self.wb_item) if show_boss else None
        ht_bbox = self.cv.bbox(self.ht_item) if show_helltide else None
        lg_bbox = self.cv.bbox(self.lg_item) if show_legion else None

        x = HPAD
        if show_boss:
            self.cv.coords(self.wb_item, x, H // 2)
            x += (wb_bbox[2] - wb_bbox[0]) + HPAD

        if show_boss and show_helltide:
            self.cv.coords(self.sep_1, x + SEP_W // 2, H // 2)
            x += SEP_W + HPAD
        elif show_boss and show_legion:
            self.cv.coords(self.sep_1, x + SEP_W // 2, H // 2)
            x += SEP_W + HPAD

        if show_helltide:
            self.cv.coords(self.ht_item, x, H // 2)
            x += (ht_bbox[2] - ht_bbox[0]) + HPAD

        if (show_helltide or show_boss) and show_legion:
            self.cv.coords(self.sep_2, x + SEP_W // 2, H // 2)
            x += SEP_W + HPAD

        if show_legion:
            self.cv.coords(self.lg_item, x, H // 2)
            x += (lg_bbox[2] - lg_bbox[0]) + HPAD

        if self.logo_img:
            logo_left = x; logo_cx = x + self.LOGO_BOX_W // 2; x += self.LOGO_BOX_W + HPAD

        set_x = x + BTN_W // 2; x += BTN_W + HPAD // 2
        close_x = x + BTN_W // 2; x += BTN_W + HPAD // 2

        new_w = x

        self.cv.coords(self.settings_btn, set_x, H // 2)
        self.cv.coords(self.close_btn, close_x, H // 2)
        self.cv.coords(self.lock_indicator, close_x, H // 2) # Shows in place of close btn when locked

        if self.logo_img:
            self.cv.coords(self.logo_border_id, logo_left, 4, logo_left + self.LOGO_BOX_W, H - 4)
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
        if self.locked or e.x > self.W - (BTN_W * 2 + HPAD): return
        self._drag_x, self._drag_y = e.x, e.y

    def _drag_stop(self, e):
        self.config["pos_x"] = self.root.winfo_x()
        self.config["pos_y"] = self.root.winfo_y()
        self._save_config()
        self._drag_x = self._drag_y = 0

    def _drag_move(self, e):
        if self._drag_x and not self.locked:
            x = self.root.winfo_x() + (e.x - self._drag_x)
            y = self.root.winfo_y() + (e.y - self._drag_y)
            self.root.geometry(f"+{x}+{y}")

    def _toggle_mini(self, _=None):
        if self.locked: return
        self.mini_mode = not self.mini_mode

    def _quit(self, _=None):
        if not self.locked:
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
            for ev in data.get("legion", []):
                if ev["timestamp"] > now:
                    self.next_legion = ev
                    break
        except: pass

    # ── Auto-update ─────────────────────────────
    def _update_check_loop(self):
        time.sleep(1)
        while True:
            self._check_update()
            time.sleep(3600)

    def _check_update(self):
        try:
            req  = urllib.request.Request(GITHUB_API_URL, headers={"User-Agent": "Mozilla/5.0"})
            data = json.loads(urllib.request.urlopen(req).read())
            tag  = data.get("tag_name", "")
            if tag and _version_tuple(tag) > _version_tuple(VERSION):
                self.update_tag = tag
                self.root.after(0, self._prompt_update, tag)
        except: pass

    def _prompt_update(self, tag):
        if self.locked: return
        ans = msgbox.askyesno("Update Available", f"A new version of Diablo 4 Overlay is available! ({tag})\n\nWould you like to download and install it now?", parent=self.root)
        if ans:
            threading.Thread(target=self._do_update, args=(tag,), daemon=True).start()

    def _do_update(self, tag: str):
        try:
            exe_name = "D4-Overlay.exe"
            dl_url   = f"https://github.com/{GITHUB_REPO}/releases/download/{tag}/{exe_name}"
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                import webbrowser
                webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
                return

            exe_dir  = os.path.dirname(current_exe)
            tmp_path = os.path.join(exe_dir, "D4-Overlay_update.exe")

            req = urllib.request.Request(dl_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp, open(tmp_path, "wb") as f:
                f.write(resp.read())

            bat_path = os.path.join(exe_dir, "_d4_update.bat")
            with open(bat_path, "w") as f:
                f.write(f"@echo off\ntimeout /t 2 /nobreak >nul\nmove /y \"{tmp_path}\" \"{current_exe}\"\nstart \"\" \"{current_exe}\"\ndel \"%~f0\"\n")
            subprocess.Popen(["cmd", "/c", bat_path], creationflags=subprocess.CREATE_NO_WINDOW)
            self.root.destroy()
            sys.exit(0)
        except Exception as e:
            msgbox.showerror("Update failed", str(e), parent=self.root)

    # ── Sound ───────────────────────────────────
    def _set_volume(self, vol_percent):
        try:
            # Convert 0-100 to 0-0xFFFF
            vol = int(0xFFFF * (vol_percent / 100))
            ctypes.windll.winmm.waveOutSetVolume(None, (vol << 16) | vol)
        except Exception as e:
            print("Volume error:", e)

    def _play_sound(self):
        self._set_volume(self.config.get("sound_volume", 100))
        custom_file = self.config.get("sound_file", "")
        if custom_file and os.path.exists(custom_file):
            winsound.PlaySound(custom_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        elif os.path.exists(CUSTOM_SOUND):
            winsound.PlaySound(CUSTOM_SOUND, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)

    # ── UI tick ─────────────────────────────────
    def _tick(self):
        now = time.time()
        t = THEMES.get(self.config["theme"], THEMES["Default Crimson"])

        # World Boss
        if self.config.get("show_boss", True):
            if self.next_boss:
                left = int(self.next_boss["timestamp"] - now)
                if left > 0:
                    h, rem = left // 3600, left % 3600
                    m, sec = rem // 60, rem % 60
                    if self.mini_mode:
                        total_m = left // 60
                        self.cv.itemconfig(self.wb_item, text=f"👹 {total_m:02d}:{sec:02d}", fill=t["wb"])
                    else:
                        names = list({z["boss"] for z in self.next_boss.get("zone", []) if "boss" in z})
                        if not names: names = [self.next_boss.get("boss", "World Boss")]
                        zones = list({z.get("name", "") for z in self.next_boss.get("zone", []) if z.get("name")})
                        boss_str = " & ".join(names)
                        if zones: boss_str += f" ({zones[0]})"
                        self.cv.itemconfig(self.wb_item, text=f"{boss_str}  {h:02d}:{m:02d}:{sec:02d}", fill=t["wb"])
                    if self.config.get("sound_wb", True) and left <= self.config["alert_minutes"] * 60 and self.alerted_id != self.next_boss["id"]:
                        self._play_sound()
                        self.alerted_id = self.next_boss["id"]
                else:
                    self.cv.itemconfig(self.wb_item, text="⚔" if self.mini_mode else "⚔  World Boss Active!", fill=t["active"])
            else:
                self.cv.itemconfig(self.wb_item, text="👹 ..." if self.mini_mode else "WB: connecting...", fill=t["idle"])

        # Helltide
        if self.config.get("show_helltide", True):
            if self.next_helltide:
                ht_start = self.next_helltide["timestamp"]
                ht_end   = ht_start + HELLTIDE_DURATION
                if now < ht_start:
                    left = int(ht_start - now)
                    txt = f"🔥 {left//60:02d}:{left%60:02d}" if self.mini_mode else f"HT in {left//60:02d}:{left%60:02d}"
                    self.cv.itemconfig(self.ht_item, text=txt, fill=t["idle"])
                    if self.config.get("sound_ht", False) and left <= self.config["alert_minutes"] * 60 and self.alerted_ht_id != self.next_helltide["id"]:
                        self._play_sound()
                        self.alerted_ht_id = self.next_helltide["id"]
                elif now < ht_end:
                    left = int(ht_end - now)
                    txt = f"🔥 {left//60:02d}:{left%60:02d}" if self.mini_mode else f"HT: {left//60:02d}:{left%60:02d}"
                    self.cv.itemconfig(self.ht_item, text=txt, fill=t["active"])
                else:
                    self.cv.itemconfig(self.ht_item, text="🔥 ..." if self.mini_mode else "HT starting...", fill=t["idle"])
            else:
                self.cv.itemconfig(self.ht_item, text="🔥 ..." if self.mini_mode else "HT: ...", fill=t["idle"])

        # Legion
        if self.config.get("show_legion", True):
            if self.next_legion:
                left = int(self.next_legion["timestamp"] - now)
                if left > 0:
                    txt = f"⚡ {left//60:02d}:{left%60:02d}" if self.mini_mode else f"LG: {left//60:02d}:{left%60:02d}"
                    self.cv.itemconfig(self.lg_item, text=txt, fill=t["idle"])
                    if self.config.get("sound_legion", False) and left <= self.config["alert_minutes"] * 60 and self.alerted_lg_id != self.next_legion["id"]:
                        self._play_sound()
                        self.alerted_lg_id = self.next_legion["id"]
                else:
                    self.cv.itemconfig(self.lg_item, text="⚡" if self.mini_mode else "⚔ LG Active!", fill=t["active"])
            else:
                self.cv.itemconfig(self.lg_item, text="⚡ ..." if self.mini_mode else "LG: ...", fill=t["idle"])

        self._relayout()
        self.root.after(1000, self._tick)

if __name__ == "__main__":
    root = tk.Tk()
    OverlayApp(root)
    root.mainloop()
