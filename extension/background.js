const PROJECT = "<PROJECT>";
const BASE = "https://" + PROJECT + ".appspot.com/";
const GO = BASE + "visit?link=";
const LIST = BASE + "list";

chrome.webRequest.onBeforeRequest.addListener(function(details) {
    let url = new URL(details.url);
    // TODO: Consider forwarding query parameters too?
    if (url.hostname == "go") {
      return {redirectUrl: GO + encodeURIComponent(url.pathname.slice(1))};
    }
    return {};
  },
  {
    urls: [
      "<all_urls>",
    ],
    types: ["main_frame"]
  },
  ["blocking"]
);

chrome.browserAction.onClicked.addListener(function(tab) { 
  chrome.tabs.create({ url: LIST });
});

