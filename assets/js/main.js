// Progressive enhancement only: the site is fully usable without this file.
// Highlights the current section in the header nav (home page) and in the table of
// contents (paper pages) while scrolling.
(function () {
  "use strict";
  if (!("IntersectionObserver" in window)) return;

  function spy(linkSelector) {
    var links = Array.prototype.slice.call(document.querySelectorAll(linkSelector));
    var map = {};
    links.forEach(function (a) {
      var id = (a.getAttribute("href") || "").split("#")[1];
      if (id && document.getElementById(id)) map[id] = a;
    });
    var ids = Object.keys(map);
    if (!ids.length) return;
    var current = null;
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            if (current) current.removeAttribute("aria-current");
            current = map[e.target.id];
            current.setAttribute("aria-current", "true");
          }
        });
      },
      { rootMargin: "-20% 0px -70% 0px", threshold: 0 }
    );
    ids.forEach(function (id) { observer.observe(document.getElementById(id)); });
  }

  spy(".nav a[href*='#']");
  spy(".toc a[href^='#']");
})();
