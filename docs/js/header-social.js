(function () {
  "use strict";

  function moveSocialLinks() {
    var social = document.querySelector(".md-footer .md-social");
    var source = document.querySelector(".md-header__source");
    if (!social || !source || social.classList.contains("b2e-header-social")) {
      return;
    }

    social.classList.add("b2e-header-social");
    source.insertAdjacentElement("afterend", social);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", moveSocialLinks);
  } else {
    moveSocialLinks();
  }
})();
