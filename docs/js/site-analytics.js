(function () {
  "use strict";

  function loadTracker() {
    var config = window.B2E_ANALYTICS || {};
    if (!config.scriptUrl || !config.websiteId || document.querySelector("script[data-website-id]")) {
      return;
    }

    var script = document.createElement("script");
    script.defer = true;
    script.src = config.scriptUrl;
    script.setAttribute("data-website-id", config.websiteId);
    script.setAttribute("data-domains", config.domains || window.location.hostname);
    script.setAttribute("data-do-not-track", "true");
    document.head.appendChild(script);
  }

  function track(eventName, data) {
    if (!window.umami || typeof window.umami.track !== "function") return;
    window.umami.track(eventName, data || {});
  }

  loadTracker();

  document.addEventListener("click", function (event) {
    var link = event.target.closest && event.target.closest("a[href]");
    if (!link) return;

    if (link.classList.contains("next-node")) {
      track("Next node", {
        node: link.dataset.umamiEventNode || "",
        type: link.dataset.umamiEventType || ""
      });
      return;
    }

    if (link.classList.contains("tree-node-link")) {
      track("See in tree", {
        node: link.dataset.umamiEventNode || ""
      });
      return;
    }

    if (link.id === "i-read") {
      track("Tree read more", {
        node: link.dataset.nodeId || "",
        url: link.getAttribute("href") || ""
      });
      return;
    }

    if (/^https?:\/\//.test(link.href) && link.hostname !== window.location.hostname) {
      track("External link", {
        host: link.hostname,
        url: link.href
      });
    }
  });

  document.addEventListener("pointerdown", function (event) {
    var embed = event.target.closest && event.target.closest(".video-embed");
    if (embed) track("Video interaction", { page: window.location.pathname });
  });

  document.addEventListener("DOMContentLoaded", function () {
    var tree = document.getElementById("tech-tree");
    if (tree) track("Homepage tree viewed");
  });
})();
