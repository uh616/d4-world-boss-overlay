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
VERSION     = "1.4.0"
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
        "sound":          "Sound Alerts",
        "auto_hide":      "Auto-hide on focus",
        "theme":          "Theme:",
        "opacity":        "Opacity:",
        "display":        "Display",
        "world_boss":     "World Boss",
        "helltide":       "Helltide",
        "legion":         "Legion",
        "language":       "Language:",
        "tip":            "Tip: Press Ctrl + L to lock/unlock overlay",
        "support":        "❤️ Support",
    },
    "ru": {
        "settings_title": "⚙ Настройки",
        "alert_time":     "Оповещение:",
        "mins":           "мин",
        "sound":          "Звук",
        "auto_hide":      "Авто-скрытие",
        "theme":          "Тема:",
        "opacity":        "Прозрачность:",
        "display":        "Отображение",
        "world_boss":     "World Boss",
        "helltide":       "Helltide",
        "legion":         "Legion",
        "language":       "Язык:",
        "tip":            "Совет: Ctrl + L — заблокировать оверлей",
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
            "sound_enabled": True,
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

        # ── State ────────────────────────────────
        self.next_boss      = None
        self.next_helltide  = None
        self.next_legion    = None
        self.alerted_id     = None
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
        keyboard.add_hotkey('ctrl+l', self._toggle_lock)

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
            
        win = tk.Toplevel(self.root)
        self.settings_win = win
        win.title("Overlay Settings")
        win.geometry("350x545")
        win.resizable(False, False)
        win.configure(bg="#111111")
        win.wm_attributes("-topmost", True)
        
        if self.logo_img:
            win.iconphoto(False, self.logo_img)
        
        s = STRINGS.get(self.config.get("language", "en"), STRINGS["en"])

        # Helper to auto-save and apply
        def _auto_save():
            self.config["alert_minutes"]  = alert_var.get()
            self.config["sound_enabled"]  = sound_var.get()
            self.config["auto_hide"]      = hide_var.get()
            self.config["theme"]          = theme_var.get()
            self.config["show_boss"]      = boss_var.get()
            self.config["show_helltide"]  = ht_var.get()
            self.config["show_legion"]    = legion_var.get()
            self.config["opacity"]        = opacity_var.get() / 100.0
            self.config["language"]       = lang_var.get()
            
            self._save_config()
            self._apply_theme()
            
            # Restart auto-hide thread if just enabled
            if self.config["auto_hide"] and not getattr(self, "_auto_hide_running", False):
                self._auto_hide_running = True
                threading.Thread(target=self._auto_hide_loop, daemon=True).start()
                
        # Header
        tk.Label(win, text=s["settings_title"], font=("Segoe UI", 16, "bold"), bg="#111111", fg="#ffffff").pack(pady=(20, 10))

        # Container
        f = tk.Frame(win, bg="#111111")
        f.pack(fill="x", padx=30)
        
        # ── Alert Time (Custom Spinner) ──
        tk.Label(f, text=s["alert_time"], bg="#111111", fg="#e4e4e7", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=8)
        
        alert_frame = tk.Frame(f, bg="#111111")
        alert_frame.grid(row=0, column=1, columnspan=2, sticky="e")
        
        alert_var = tk.IntVar(value=self.config.get("alert_minutes", 5))
        valid_times = [1, 5, 10, 15]
        if alert_var.get() not in valid_times:
            alert_var.set(5)
            
        def change_alert(delta):
            idx = valid_times.index(alert_var.get())
            new_idx = (idx + delta) % len(valid_times)
            alert_var.set(valid_times[new_idx])
            lbl_alert.config(text=f"{alert_var.get()} {s['mins']}")
            _auto_save()

        btn_minus = tk.Label(alert_frame, text="◀", bg="#111111", fg="#a1a1aa", font=("Segoe UI", 10), cursor="hand2")
        btn_minus.pack(side="left", padx=5)
        btn_minus.bind("<Button-1>", lambda _: change_alert(-1))
        
        lbl_alert = tk.Label(alert_frame, text=f"{alert_var.get()} {s['mins']}", bg="#27272a", fg="white", width=8, font=("Segoe UI", 10, "bold"))
        lbl_alert.pack(side="left")
        
        btn_plus = tk.Label(alert_frame, text="▶", bg="#111111", fg="#a1a1aa", font=("Segoe UI", 10), cursor="hand2")
        btn_plus.pack(side="left", padx=5)
        btn_plus.bind("<Button-1>", lambda _: change_alert(1))

        # ── Toggles ──
        sound_var = tk.BooleanVar(value=self.config.get("sound_enabled", True))
        hide_var  = tk.BooleanVar(value=self.config.get("auto_hide", False))

        def create_toggle(parent, text, var, row):
            tk.Label(parent, text=text, bg="#111111", fg="#e4e4e7", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=6)
            btn = tk.Label(parent, text="ON" if var.get() else "OFF", width=6, font=("Segoe UI", 9, "bold"),
                           bg="#22c55e" if var.get() else "#3f3f46", fg="white", cursor="hand2")
            btn.grid(row=row, column=1, columnspan=2, sticky="e")
            def toggle(_):
                var.set(not var.get())
                btn.config(text="ON" if var.get() else "OFF", bg="#22c55e" if var.get() else "#3f3f46")
                _auto_save()
            btn.bind("<Button-1>", toggle)

        create_toggle(f, s["sound"], sound_var, 1)
        create_toggle(f, s["auto_hide"], hide_var, 2)

        # ── Theme (Custom Selector) ──
        tk.Label(f, text=s["theme"], bg="#111111", fg="#e4e4e7", font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", pady=8)
        
        theme_frame = tk.Frame(f, bg="#111111")
        theme_frame.grid(row=3, column=1, columnspan=2, sticky="e")
        
        theme_var = tk.StringVar(value=self.config.get("theme", "Default Crimson"))
        themes_list = list(THEMES.keys())
        if theme_var.get() not in themes_list:
            theme_var.set(themes_list[0])
            
        def change_theme(delta):
            idx = themes_list.index(theme_var.get())
            new_idx = (idx + delta) % len(themes_list)
            theme_var.set(themes_list[new_idx])
            lbl_theme.config(text=theme_var.get())
            _auto_save()

        btn_t_minus = tk.Label(theme_frame, text="◀", bg="#111111", fg="#a1a1aa", font=("Segoe UI", 10), cursor="hand2")
        btn_t_minus.pack(side="left", padx=5)
        btn_t_minus.bind("<Button-1>", lambda _: change_theme(-1))
        
        lbl_theme = tk.Label(theme_frame, text=theme_var.get(), bg="#27272a", fg="white", width=14, font=("Segoe UI", 10, "bold"))
        lbl_theme.pack(side="left")
        
        btn_t_plus = tk.Label(theme_frame, text="▶", bg="#111111", fg="#a1a1aa", font=("Segoe UI", 10), cursor="hand2")
        btn_t_plus.pack(side="left", padx=5)
        btn_t_plus.bind("<Button-1>", lambda _: change_theme(1))
        
        # ── Opacity (Slider) ──
        tk.Label(f, text=s["opacity"], bg="#111111", fg="#e4e4e7", font=("Segoe UI", 10)).grid(row=4, column=0, sticky="w", pady=8)
        
        op_frame = tk.Frame(f, bg="#111111")
        op_frame.grid(row=4, column=1, columnspan=2, sticky="e")
        
        opacity_var = tk.IntVar(value=int(self.config.get("opacity", 0.9) * 100))
        
        def on_opacity_slide(val):
            opacity_var.set(val)
            _auto_save()
            
        slider = ModernSlider(op_frame, width=100, height=30, bg="#111111", trough="#27272a", fill_color="#3b82f6", slider="#ffffff", 
                              command=on_opacity_slide, initial=opacity_var.get())
        slider.pack(side="left", padx=(0, 2))
        
        lbl_op = tk.Label(op_frame, textvariable=opacity_var, bg="#27272a", fg="white", width=4, font=("Segoe UI", 9, "bold"))
        lbl_op.pack(side="left")
        tk.Label(op_frame, text="%", bg="#111111", fg="white", font=("Segoe UI", 9, "bold")).pack(side="left")

        # ── Language (Custom Selector) ──
        tk.Label(f, text=s["language"], bg="#111111", fg="#e4e4e7", font=("Segoe UI", 10)).grid(row=5, column=0, sticky="w", pady=8)
        
        lang_frame = tk.Frame(f, bg="#111111")
        lang_frame.grid(row=5, column=1, columnspan=2, sticky="e")
        
        lang_var = tk.StringVar(value=self.config.get("language", "en"))
        langs_list = ["en", "ru"]
        lang_labels = {"en": "English", "ru": "Русский"}
        if lang_var.get() not in langs_list:
            lang_var.set("en")
            
        def change_lang(delta):
            idx = langs_list.index(lang_var.get())
            new_idx = (idx + delta) % len(langs_list)
            lang_var.set(langs_list[new_idx])
            lbl_lang.config(text=lang_labels[lang_var.get()])
            _auto_save()

        btn_l_minus = tk.Label(lang_frame, text="◀", bg="#111111", fg="#a1a1aa", font=("Segoe UI", 10), cursor="hand2")
        btn_l_minus.pack(side="left", padx=5)
        btn_l_minus.bind("<Button-1>", lambda _: change_lang(-1))
        
        lbl_lang = tk.Label(lang_frame, text=lang_labels[lang_var.get()], bg="#27272a", fg="white", width=10, font=("Segoe UI", 10, "bold"))
        lbl_lang.pack(side="left")
        
        btn_l_plus = tk.Label(lang_frame, text="▶", bg="#111111", fg="#a1a1aa", font=("Segoe UI", 10), cursor="hand2")
        btn_l_plus.pack(side="left", padx=5)
        btn_l_plus.bind("<Button-1>", lambda _: change_lang(1))

        # ── Display section ──
        sep_line = tk.Frame(win, bg="#27272a", height=1)
        sep_line.pack(fill="x", padx=30, pady=(12, 0))
        tk.Label(win, text=s["display"], bg="#111111", fg="#71717a", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=30, pady=(4, 0))

        fd = tk.Frame(win, bg="#111111")
        fd.pack(fill="x", padx=30)

        boss_var   = tk.BooleanVar(value=self.config.get("show_boss",     True))
        ht_var     = tk.BooleanVar(value=self.config.get("show_helltide", True))
        legion_var = tk.BooleanVar(value=self.config.get("show_legion",   True))

        create_toggle(fd, s["world_boss"], boss_var,   0)
        create_toggle(fd, s["helltide"],   ht_var,     1)
        create_toggle(fd, s["legion"],     legion_var, 2)
        
        # ── Support & Hotkey ──
        import webbrowser
        def open_support(_): webbrowser.open("https://boosty.to/6i6")
            
        btn_support = tk.Label(win, text=s["support"], bg="#111111", fg="#ef4444", font=("Segoe UI", 10, "bold"), cursor="hand2")
        btn_support.pack(side="bottom", pady=(0, 15))
        btn_support.bind("<Button-1>", open_support)
        
        tk.Label(win, text=s["tip"], bg="#111111", fg="#94a3b8", font=("Segoe UI", 9)).pack(side="bottom", pady=(15, 5))

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
    def _play_sound(self):
        if not self.config["sound_enabled"]: return
        if os.path.exists(CUSTOM_SOUND):
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
                        self.cv.itemconfig(self.wb_item, text=" & ".join(names) + f"  {h:02d}:{m:02d}:{sec:02d}", fill=t["wb"])
                    if left <= self.config["alert_minutes"] * 60 and self.alerted_id != self.next_boss["id"]:
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
