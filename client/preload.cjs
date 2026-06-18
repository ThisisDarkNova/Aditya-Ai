const { contextBridge, ipcRenderer } = require('electron');

// Protect channel communication from crashes using a defensive try/catch interface
const safeInvoke = async (channel, ...args) => {
    try {
        return await ipcRenderer.invoke(channel, ...args);
    } catch (error) {
        console.error(`[IPC BRIDGE ERROR] Failed to invoke channel "${channel}":`, error);
        return { error: error.message };
    }
};

const safeSend = (channel, ...args) => {
    try {
        ipcRenderer.send(channel, ...args);
    } catch (error) {
        console.error(`[IPC BRIDGE ERROR] Failed to send to channel "${channel}":`, error);
    }
};

contextBridge.exposeInMainWorld('electronAPI', {
    invoke: safeInvoke,
    send: safeSend,
    on: (channel, callback) => {
        try {
            const subscription = (event, ...args) => callback(event, ...args);
            ipcRenderer.on(channel, subscription);
            return () => ipcRenderer.removeListener(channel, subscription);
        } catch (error) {
            console.error(`[IPC BRIDGE ERROR] Failed to subscribe to channel "${channel}":`, error);
            return () => {};
        }
    }
});

contextBridge.exposeInMainWorld('aditya', {
    openApp: (appName) => safeInvoke('aditya:openApp', appName)
});
