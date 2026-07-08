const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'electronAPI', {
    getConfig: () => ipcRenderer.invoke('get-config'),
    saveConfig: (key, value) => ipcRenderer.invoke('save-config', key, value),
    getThemes: () => ipcRenderer.invoke('get-themes'),
    testSound: () => ipcRenderer.send('test-sound'),
    browseSound: () => ipcRenderer.invoke('browse-sound'),
    listenHotkey: () => ipcRenderer.invoke('listen-hotkey'),
    captureHotkey: (hk) => ipcRenderer.send('hotkey-captured', hk),
    onStartListeningHotkey: (cb) => ipcRenderer.on('start-listening-hotkey', () => cb()),
    openSupport: () => ipcRenderer.send('open-support'),
    closeSettings: () => ipcRenderer.send('close-settings'),
    moveSettingsWindow: (x, y) => ipcRenderer.send('move-settings-window', x, y),
    openSettings: () => ipcRenderer.send('open-settings'),
    closeOverlay: () => ipcRenderer.send('close-overlay'),
    toggleMini: () => ipcRenderer.send('toggle-mini'),
    savePosition: (x, y) => ipcRenderer.send('save-position', x, y),
    resizeWindow: (w, h) => ipcRenderer.send('resize-window', w, h || 40),
    onApiUpdate: (callback) => ipcRenderer.on('api-update', (event, data) => callback(data)),
    onConfigChanged: (callback) => ipcRenderer.on('config-changed', (event, data) => callback(data)),
    onLockChanged: (callback) => ipcRenderer.on('lock-changed', (event, isLocked) => callback(isLocked)),
    onPlayAudio: (callback) => ipcRenderer.on('play-audio', (event, data) => callback(data)),
    onUpdateAvailable: (callback) => ipcRenderer.on('update-available', (event, data) => callback(data)),
    openUrl: (url) => ipcRenderer.send('open-url', url)
  }
);
