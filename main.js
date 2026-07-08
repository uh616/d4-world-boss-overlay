const { app, BrowserWindow, ipcMain, globalShortcut, dialog, shell, screen } = require('electron');
const path = require('path');
const fs = require('fs');

// Disable autoplay policy to allow overlay to play sounds without interaction
app.commandLine.appendSwitch('autoplay-policy', 'no-user-gesture-required');

const CONFIG_FILE = path.join(__dirname, 'config.json');

let overlayWindow = null;
let settingsWindow = null;
let isLocked = false;
let config = {};

const THEMES = {
    "Default Crimson": {"wb": "#ffcc00", "active": "#ef4444", "idle": "#a1a1aa", "border": "#8b0000"},
    "Neon Blue":       {"wb": "#38bdf8", "active": "#818cf8", "idle": "#94a3b8", "border": "#1e3a8a"},
    "Gold":            {"wb": "#fde047", "active": "#f59e0b", "idle": "#d6d3d1", "border": "#b45309"}
};

// Default config
config = {
    "alert_minutes": 5, "sound_wb": true, "sound_ht": false, "sound_legion": false,
    "sound_file": "", "sound_volume": 100, "hotkey": "ctrl+l", "auto_hide": false,
    "theme": "Default Crimson", "show_boss": true, "show_helltide": true, "show_legion": true,
    "opacity": 0.9, "pos_x": 0, "pos_y": 0, "language": "en", "font_size": 12
};

function loadConfig() {
    try {
        if (fs.existsSync(CONFIG_FILE)) {
            const data = fs.readFileSync(CONFIG_FILE, 'utf8');
            config = { ...config, ...JSON.parse(data) };
        }
    } catch (e) { console.error("Config load error", e); }
}

function saveConfig() {
    try {
        fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 4), 'utf8');
    } catch (e) { console.error("Config save error", e); }
}

loadConfig();

function createOverlay() {
    const display = screen.getPrimaryDisplay();
    const { width } = display.workAreaSize;

    let x = config.pos_x || 0;
    let y = config.pos_y || 0;
    if (x === 0 && y === 0) {
        x = Math.floor(width / 2) - 200;
        y = 20;
    }

    overlayWindow = new BrowserWindow({
        width: 450,
        height: 40,
        x: x,
        y: y,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        skipTaskbar: true,
        resizable: false,
        show: false,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        }
    });

    // Keep overlay truly on top of everything including game
    overlayWindow.setAlwaysOnTop(true, 'screen-saver');

    overlayWindow.loadFile(path.join(__dirname, 'web', 'index.html'));
    overlayWindow.setIgnoreMouseEvents(false);

    overlayWindow.on('moved', () => {
        const bounds = overlayWindow.getBounds();
        config.pos_x = bounds.x;
        config.pos_y = bounds.y;
        saveConfig();
    });

    overlayWindow.webContents.on('did-finish-load', () => {
        overlayWindow.show();
    });

    // overlayWindow.webContents.openDevTools({ mode: 'detach' });
}

function createSettings() {
    settingsWindow = new BrowserWindow({
        width: 390,
        height: 680,
        // NO transparent:true — that breaks drag regions on scrollable content
        frame: false,
        backgroundColor: '#09090b', // solid dark background, no white flash
        resizable: false,
        show: false,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false
        }
    });

    settingsWindow.loadFile(path.join(__dirname, 'web', 'settings.html'));

    settingsWindow.on('close', (e) => {
        // Always hide, never fully close (prevents app from quitting)
        e.preventDefault();
        settingsWindow.hide();
    });

    // Keep settings on top of game too, but below overlay
    settingsWindow.setAlwaysOnTop(true, 'floating');

    // DEV: uncomment to debug
    // settingsWindow.webContents.openDevTools({ mode: 'detach' });
}

function toggleLock() {
    isLocked = !isLocked;
    if (isLocked) {
        overlayWindow.setIgnoreMouseEvents(true, { forward: true });
    } else {
        overlayWindow.setIgnoreMouseEvents(false);
    }
    if (overlayWindow) overlayWindow.webContents.send('lock-changed', isLocked);
}

app.whenReady().then(() => {
    createOverlay();
    createSettings();

    if (config.hotkey) {
        try {
            const hk = config.hotkey.toLowerCase().trim();
            // Only register ASCII-compatible hotkeys
            if (/^[a-z0-9+\-\s]+$/.test(hk)) {
                globalShortcut.register(hk, toggleLock);
            } else {
                console.warn("Invalid hotkey (non-ascii):", hk);
            }
        } catch(e) { console.error("Hotkey register error:", e); }
    }

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createOverlay();
    });

    startWatcher();
});

app.on('window-all-closed', () => {
    // Only quit if user explicitly closed via close-overlay IPC
    // Settings window hides instead of closing, so this only fires on true quit
    if (process.platform !== 'darwin') app.quit();
});

// ─── IPC Handlers ──────────────────────────────────────────────────────────

ipcMain.handle('get-config', () => JSON.stringify(config));
ipcMain.handle('get-themes', () => JSON.stringify(Object.keys(THEMES)));

ipcMain.handle('save-config', (event, key, value) => {
    config[key] = value;
    saveConfig();

    // Broadcast config change to overlay
    if (overlayWindow) overlayWindow.webContents.send('config-changed', JSON.stringify(config));

    // Re-register hotkey if changed
    if (key === 'hotkey') {
        globalShortcut.unregisterAll();
        try {
            const hk = value.toLowerCase().trim();
            if (/^[a-z0-9+\-\s]+$/.test(hk)) {
                globalShortcut.register(hk, toggleLock);
            }
        } catch(e) {}
    }
});

ipcMain.on('save-position', (event, x, y) => {
    config.pos_x = x;
    config.pos_y = y;
    saveConfig();
});

ipcMain.on('move-settings-window', (event, x, y) => {
    if (settingsWindow) settingsWindow.setPosition(Math.round(x), Math.round(y));
});

ipcMain.on('resize-window', (event, w, h) => {
    if (overlayWindow) {
        const clampedW = Math.max(200, Math.min(800, w || 450));
        const clampedH = Math.max(30, Math.min(80, h || 40));
        overlayWindow.setSize(clampedW, clampedH);
    }
});

ipcMain.on('open-settings', () => {
    if (!isLocked && settingsWindow) {
        // Position settings window below the overlay bar
        const overlayBounds = overlayWindow ? overlayWindow.getBounds() : { x: 100, y: 20 };
        const settingsX = overlayBounds.x;
        const settingsY = overlayBounds.y + 50; // 50px below overlay
        
        const { width: sw, height: sh } = require('electron').screen.getPrimaryDisplay().workAreaSize;
        const clampX = Math.min(settingsX, sw - 390);
        const clampY = Math.min(settingsY, sh - 680);
        
        settingsWindow.setPosition(Math.max(0, clampX), Math.max(0, clampY));
        settingsWindow.show();
        settingsWindow.focus();
    }
});

ipcMain.on('close-settings', () => {
    if (settingsWindow) settingsWindow.hide();
});

ipcMain.on('close-overlay', () => {
    if (settingsWindow) settingsWindow.destroy();
    app.quit();
});

ipcMain.on('open-support', () => {
    shell.openExternal("https://boosty.to/6i6");
});

ipcMain.handle('browse-sound', async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog(settingsWindow, {
        title: "Select Alert Sound",
        filters: [{ name: 'WAV files', extensions: ['wav'] }],
        properties: ['openFile']
    });
    if (!canceled && filePaths.length > 0) {
        config.sound_file = filePaths[0];
        saveConfig();
        return filePaths[0];
    }
    return "";
});

ipcMain.handle('listen-hotkey', async (event) => {
    // Tell the settings renderer to start capturing
    if (settingsWindow) settingsWindow.webContents.send('start-listening-hotkey');
    
    return new Promise((resolve) => {
        const timeout = setTimeout(() => {
            ipcMain.removeListener('hotkey-captured', handler);
            resolve('');
        }, 10000); // 10s timeout

        function handler(e, hk) {
            clearTimeout(timeout);
            ipcMain.removeListener('hotkey-captured', handler);
            // Save and register the new hotkey
            config.hotkey = hk;
            saveConfig();
            globalShortcut.unregisterAll();
            try {
                if (/^[a-z0-9+\-\s]+$/.test(hk)) {
                    globalShortcut.register(hk, toggleLock);
                }
            } catch(e) {}
            resolve(hk);
        }
        ipcMain.once('hotkey-captured', handler);
    });
});

ipcMain.on('test-sound', () => {
    // In packaged app, extraResources are in process.resourcesPath; in dev, next to main.js
    const defaultSoundFile = app.isPackaged
        ? path.join(process.resourcesPath, 'alert.wav')
        : path.join(__dirname, 'alert.wav');
    // If user has a custom sound_file set, use that; otherwise fall back to the bundled one
    const userCustom = config.sound_file ? path.join(path.dirname(defaultSoundFile), config.sound_file) : null;
    const soundFile = (userCustom && fs.existsSync(userCustom)) ? userCustom : defaultSoundFile;
    const vol = config.sound_volume !== undefined ? config.sound_volume : 100;
    if (fs.existsSync(soundFile)) {
        try {
            const buffer = fs.readFileSync(soundFile);
            const base64 = buffer.toString('base64');
            const dataUri = 'data:audio/wav;base64,' + base64;
            if (overlayWindow) {
                overlayWindow.webContents.send('play-audio', { dataUri, volume: vol });
            }
        } catch(e) { console.error('Audio read error:', e); }
    }
});

// ─── API Fetch Loop ────────────────────────────────────────────────────────

const API_URL = "https://helltides.com/api/schedule";

async function fetchAPI() {
    try {
        const response = await fetch(API_URL, { headers: { 'User-Agent': 'Mozilla/5.0' }});
        const data = await response.json();

        const now = Date.now() / 1000;
        function getNext(items, type) {
            if (!items) return null;
            if (!Array.isArray(items)) items = [items];
            const future = items.filter(i => (i.timestamp || i.expectedTime || 0) > now - 10);
            if (future.length === 0) return null;
            const closest = future.reduce((prev, curr) =>
                ((prev.timestamp || prev.expectedTime) < (curr.timestamp || curr.expectedTime) ? prev : curr)
            );
            return {
                time: closest.timestamp || closest.expectedTime,
                type: type,
                name: closest.name || "",
                zone: closest.zone || ""
            };
        }

        const boss     = getNext(data.world_boss || data.boss, "boss");

        // Helltide lasts 55 minutes — a helltide that started up to 55min ago is still active
        const helltideRaw = data.helltide;
        let helltide = null;
        if (helltideRaw) {
            const arr = Array.isArray(helltideRaw) ? helltideRaw : [helltideRaw];
            // Find the most recent helltide that either hasn't started yet, or started within last 55 min
            const HELLTIDE_DURATION = 55 * 60;
            const relevant = arr.filter(i => (i.timestamp || 0) > now - HELLTIDE_DURATION);
            if (relevant.length > 0) {
                const closest = relevant.reduce((prev, curr) =>
                    (prev.timestamp < curr.timestamp ? prev : curr)
                );
                helltide = { time: closest.timestamp, type: "helltide", name: closest.name || "", zone: closest.zone || "" };
            }
        }

        const legion   = getNext(data.legion, "legion");

        if (overlayWindow) {
            overlayWindow.webContents.send('api-update', { boss, helltide, legion });
        }
    } catch (e) { console.error("Fetch API Error:", e); }
}

setInterval(fetchAPI, 5 * 60 * 1000);
setTimeout(fetchAPI, 2000);

// ─── Auto Hide Logic ───────────────────────────────────────────────────────
let psWatcher = null;

function startWatcher() {
    if (psWatcher) return;
    const watcherScript = path.join(__dirname, 'watcher.ps1');
    const scriptContent = `
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
}
"@

$sb = New-Object System.Text.StringBuilder 256
while ($true) {
    $hwnd = [Win32]::GetForegroundWindow()
    if ([Win32]::GetWindowText($hwnd, $sb, 256) -gt 0) {
        [Console]::WriteLine($sb.ToString())
    } else {
        [Console]::WriteLine("UNKNOWN")
    }
    Start-Sleep -Seconds 1
}
`;
    fs.writeFileSync(watcherScript, scriptContent, 'utf8');
    
    const { spawn } = require('child_process');
    psWatcher = spawn('powershell', ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', watcherScript]);
    
    psWatcher.stdout.on('data', (data) => {
        if (!config.auto_hide) {
            if (overlayWindow && !overlayWindow.isVisible() && (!settingsWindow || !settingsWindow.isVisible())) {
                overlayWindow.showInactive();
            }
            return;
        }

        const lines = data.toString().trim().split('\n');
        const title = lines[lines.length - 1].trim(); // Get latest
        const isActive = title.includes('Diablo IV');
        
        if (overlayWindow) {
            const isSettingsOpen = settingsWindow && settingsWindow.isVisible();
            // Should be visible if D4 is active, or settings are open, or we are not locked (moving overlay)
            const shouldBeVisible = isActive || isSettingsOpen || !isLocked;
            
            if (shouldBeVisible && !overlayWindow.isVisible()) {
                overlayWindow.showInactive();
            } else if (!shouldBeVisible && overlayWindow.isVisible()) {
                overlayWindow.hide();
            }
        }
    });

    psWatcher.stderr.on('data', (data) => console.error("Watcher error:", data.toString()));
}
