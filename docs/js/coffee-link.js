(function () {
  "use strict";

  var href = "https://buymeacoffee.com/backtoengineering";

  function addCoffeeLink() {
    if (document.querySelector(".b2e-coffee-link")) return;

    var link = document.createElement("a");
    link.className = "b2e-coffee-link";
    link.href = href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Buy me a coffee";
    document.body.appendChild(link);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", addCoffeeLink);
  } else {
    addCoffeeLink();
  }
})();
