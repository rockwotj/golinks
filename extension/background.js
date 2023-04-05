chrome.action.onClicked.addListener((_) => { 
  chrome.tabs.create({ url: "https://example.com/list" });
});

export {}

