const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

// Define your list of lists of URLs
const webURLs = {
  business: [
    "https://finance.yahoo.com/",
    "https://www.bloomberg.com/",
    "https://www.foxbusiness.com/",
    "https://www.youtube.com/c/garyvee"
  ],
  politics: [
    "https://www.theatlantic.com/",
    "https://therecord.media/",
    "https://www.wired.com/",
    "https://www.zdnet.com/",
    "https://medium.com/",
    "https://www.theepochtimes.com/",
    "https://www.dailywire.com/",
    "https://www.yahoo.com/",
    "https://www.nytimes.com/",
    "https://www.washingtonpost.com/",
    "https://www.foxnews.com/",
    "https://www.politico.eu/",
    "https://www.reuters.com/",
    "https://www.youtube.com/c/FactsMatterwithRomanBalmakov",
    "https://www.youtube.com/c/Timcast",
    "https://www.youtube.com/c/BenShapiro",
    "https://www.youtube.com/c/MichaelKnowles",
    "https://www.youtube.com/c/Candaceshow",
    "https://www.youtube.com/c/StevenCrowder",
    "https://www.cnbc.com/",
    "https://www.cnn.com/",
    "https://www.msnbc.com/"
  ],
};

let mainWindow;
let currentCategory = 'business'; // Default category
let currentURLIndex = 0; // Default index for the current URL

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: false,
      enableRemoteModule: false,
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  // Open the DevTools.
  mainWindow.webContents.openDevTools();

  // Load the URL based on the current category and index
  mainWindow.loadURL(webURLs[currentCategory][currentURLIndex]);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Add the following lines to clear cache when the window is created
  const ses = mainWindow.webContents.session;
  ses.clearCache(() => {
    console.log('Cache cleared');
  });
}

app.whenReady().then(() => {
  createWindow();

  // Example: Change the category to 'politics' when the page loads
  changeCategory('politics');
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Function to change the category and load the first URL of that category
function changeCategory(category) {
  currentCategory = category;
  currentURLIndex = 0; // Reset the index when changing the category
  mainWindow.loadURL(webURLs[currentCategory][currentURLIndex]);
}

// Function to navigate to the next or previous URL in the current category
function navigate(direction) {
  currentURLIndex = (currentURLIndex + direction + webURLs[currentCategory].length) % webURLs[currentCategory].length;
  mainWindow.loadURL(webURLs[currentCategory][currentURLIndex]);
}

// Listen for navigation events from renderer process
ipcMain.on('navigate', (event, direction) => {
  navigate(direction);
});

// Listen for 'dom-ready' event from renderer process
ipcMain.on('dom-ready', () => {
  // Add event listeners for the navigation arrows
  mainWindow.webContents.send('add-event-listeners');
});

// Listen for 'category-change' event from renderer process
ipcMain.on('category-change', (event, category) => {
  changeCategory(category);
});