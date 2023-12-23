// script.js

// Add a function to change the category and load the first URL of that category
function changeCategory(category) {
  currentCategory = category;
  mainWindow.loadURL(webURLs[currentCategory][0]);
}

// Add a function to navigate to the next or previous URL in the current category
function navigate(direction) {
  const currentIndex = webURLs[currentCategory].indexOf(mainWindow.webContents.getURL());

  // Calculate the next index based on the direction
  const nextIndex = (currentIndex + direction + webURLs[currentCategory].length) % webURLs[currentCategory].length;

  // Load the URL at the next index
  mainWindow.loadURL(webURLs[currentCategory][nextIndex]);
}

// Example: Change the category to 'politics' when the page loads
document.addEventListener('DOMContentLoaded', function () {
  changeCategory('politics');
});

// Add event listeners for the navigation arrows using ipcRenderer
console.log('Adding event listener for prev-arrow');
document.getElementById('prev-arrow').addEventListener('click', function () {
  require('electron').ipcRenderer.send('navigate', -1);
});

console.log('Adding event listener for next-arrow');
document.getElementById('next-arrow').addEventListener('click', function () {
  require('electron').ipcRenderer.send('navigate', 1);
});
