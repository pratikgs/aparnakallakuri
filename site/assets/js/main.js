/* aparnakallakuri.com — no dependencies */
(function () {
  "use strict";

  var root = document.documentElement;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasIO = "IntersectionObserver" in window;

  /* ---------- Theme ---------- */
  var toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var sysDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      var now = root.getAttribute("data-theme") || (sysDark ? "dark" : "light");
      var next = now === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("ak-theme", next); } catch (e) {}
    });
  }

  /* ---------- Sticky nav hairline ---------- */
  var nav = document.getElementById("nav");
  if (nav) {
    var stick = function () { nav.setAttribute("data-stuck", window.scrollY > 8 ? "true" : "false"); };
    stick();
    window.addEventListener("scroll", stick, { passive: true });
  }

  /* ---------- Reveal on scroll ---------- */
  var reveals = document.querySelectorAll("[data-reveal]");
  if (reduced || !hasIO) {
    Array.prototype.forEach.call(reveals, function (el) { el.classList.add("in"); });
  } else {
    var ro = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); ro.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.06 });
    Array.prototype.forEach.call(reveals, function (el) { ro.observe(el); });
  }

  /* ---------- Count-up ---------- */
  var counters = document.querySelectorAll("[data-count]");
  function runCount(el) {
    var target = parseInt(el.getAttribute("data-count"), 10);
    if (isNaN(target)) return;
    if (reduced) { el.textContent = String(target); return; }
    var start = null;
    (function step(now) {
      if (start === null) start = now;
      var p = Math.min((now - start) / 1000, 1);
      el.textContent = String(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(step); else el.textContent = String(target);
    })(performance.now());
  }
  if (!hasIO) {
    Array.prototype.forEach.call(counters, runCount);
  } else {
    var co = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { runCount(e.target); co.unobserve(e.target); }
      });
    }, { threshold: 0.6 });
    Array.prototype.forEach.call(counters, function (el) {
      el.textContent = "0";
      co.observe(el);
    });
  }

  /* ---------- Draw-in for the chart and the fan diagram ---------- */
  function drawWhenSeen(el) {
    if (!el) return;
    if (reduced || !hasIO) { el.setAttribute("data-drawn", "true"); return; }
    var o = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { e.target.setAttribute("data-drawn", "true"); o.unobserve(e.target); }
      });
    }, { threshold: 0.25 });
    o.observe(el);
  }
  drawWhenSeen(document.getElementById("chart"));
  drawWhenSeen(document.getElementById("fan"));

  /* ---------- Experience: company marks as tabs ---------- */
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.mk[role="tab"]'));
  var panels = Array.prototype.slice.call(document.querySelectorAll('.panel[role="tabpanel"]'));
  var chartRows = Array.prototype.slice.call(document.querySelectorAll(".ct-row"));

  function select(key, focusTab) {
    tabs.forEach(function (t) {
      var on = t.getAttribute("data-key") === key;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      if (on && focusTab) t.focus();
    });
    panels.forEach(function (p) { p.hidden = p.id !== "p-" + key; });
    // The chart is a second control surface for the same state.
    chartRows.forEach(function (r) {
      r.setAttribute("data-active", r.getAttribute("data-target") === key ? "true" : "false");
    });
  }

  tabs.forEach(function (tab, i) {
    tab.addEventListener("click", function () { select(tab.getAttribute("data-key")); });
    tab.addEventListener("keydown", function (e) {
      var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (d) {
        e.preventDefault();
        select(tabs[(i + d + tabs.length) % tabs.length].getAttribute("data-key"), true);
      } else if (e.key === "Home" || e.key === "End") {
        e.preventDefault();
        select(tabs[e.key === "Home" ? 0 : tabs.length - 1].getAttribute("data-key"), true);
      }
    });
  });

  // Clicking a bar in the career chart opens that company and scrolls to it.
  chartRows.forEach(function (row) {
    function open() {
      var key = row.getAttribute("data-target");
      select(key);
      var marks = document.querySelector(".roster__marks");
      if (marks) marks.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "center" });
    }
    row.addEventListener("click", open);
    row.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); }
    });
  });

  if (tabs.length) select(tabs[0].getAttribute("data-key"));

  /* ---------- Active section in nav ---------- */
  var links = Array.prototype.slice.call(document.querySelectorAll(".nav__links a"));
  var sections = links.map(function (a) {
    return { link: a, el: document.getElementById(a.getAttribute("href").slice(1)) };
  }).filter(function (s) { return s.el; });

  if (sections.length && hasIO) {
    var ratios = {};
    var so = new IntersectionObserver(function (es) {
      es.forEach(function (e) { ratios[e.target.id] = e.isIntersecting ? e.intersectionRatio : 0; });
      var best = null, top = 0;
      sections.forEach(function (s) {
        var r = ratios[s.el.id] || 0;
        if (r > top) { top = r; best = s.el.id; }
      });
      sections.forEach(function (s) {
        if (s.el.id === best) s.link.setAttribute("aria-current", "true");
        else s.link.removeAttribute("aria-current");
      });
    }, { threshold: [0, 0.15, 0.4, 0.75], rootMargin: "-15% 0px -45% 0px" });
    sections.forEach(function (s) { so.observe(s.el); });
  }

  /* ---------- Footer year ---------- */
  var y = document.getElementById("year");
  if (y) y.textContent = String(new Date().getFullYear());
})();
