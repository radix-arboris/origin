// preload.js

// Expose the 'ipcRenderer' object to the window context
const { ipcRenderer } = require('electron');
window.ipcRenderer = ipcRenderer;
