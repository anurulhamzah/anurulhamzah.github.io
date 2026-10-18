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

// Approach pipeline: turns the list of stages into a tabbed rail on wide screens.
// Without JavaScript, or on narrow screens, every stage stays visible as a plain list.
(function () {
  "use strict";
  document.documentElement.classList.add("js");
  var rail = document.querySelector("[data-flow]");
  var list = document.querySelector("[data-pipe]");
  if (!rail || !list) return;
  var tabs = Array.prototype.slice.call(rail.querySelectorAll("[role=tab]"));
  var panels = Array.prototype.slice.call(list.querySelectorAll("[role=tabpanel]"));
  var wide = window.matchMedia("(min-width: 900px)");

  function select(i, focus) {
    tabs.forEach(function (t, k) {
      var on = k === i;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      if (on && focus) t.focus();
    });
    panels.forEach(function (p, k) { p.classList.toggle("is-active", k === i); });
    list.style.setProperty("--pos", i);
  }
  function apply() {
    list.classList.toggle("is-tabs", wide.matches);
    if (wide.matches) select(Math.max(0, tabs.findIndex(function (t) { return t.getAttribute("aria-selected") === "true"; })), false);
  }
  tabs.forEach(function (t, i) {
    t.addEventListener("click", function () { select(i, false); });
    t.addEventListener("keydown", function (e) {
      var k = e.key, n = tabs.length;
      if (k === "ArrowRight") { e.preventDefault(); select((i + 1) % n, true); }
      else if (k === "ArrowLeft") { e.preventDefault(); select((i - 1 + n) % n, true); }
      else if (k === "Home") { e.preventDefault(); select(0, true); }
      else if (k === "End") { e.preventDefault(); select(n - 1, true); }
    });
  });
  if (wide.addEventListener) wide.addEventListener("change", apply); else wide.addListener(apply);
  apply();
})();