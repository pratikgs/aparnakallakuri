/* aparnakallakuri.com — no dependencies */
(function () {
  "use strict";

  var root = document.documentElement;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Theme toggle ---------- */
  var toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      var current = root.getAttribute("data-theme") || (systemDark ? "dark" : "light");
      var next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("ak-theme", next); } catch (e) {}
    });
  }

  /* ---------- Sticky nav hairline ---------- */
  var nav = document.getElementById("nav");
  if (nav) {
    var onScroll = function () {
      nav.setAttribute("data-stuck", window.scrollY > 8 ? "true" : "false");
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- Scroll reveal ---------- */
  var revealables = document.querySelectorAll("[data-reveal]");
  if (reduced || !("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(revealables, function (el) { el.classList.add("is-in"); });
  } else {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          revealObserver.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    Array.prototype.forEach.call(revealables, function (el) { revealObserver.observe(el); });
  }

  /* ---------- Count-up statistics ---------- */
  var counters = document.querySelectorAll("[data-count]");
  var runCount = function (el) {
    var target = parseInt(el.getAttribute("data-count"), 10);
    if (isNaN(target)) return;
    if (reduced) { el.textContent = String(target); return; }

    var duration = 1100;
    var start = null;
    var step = function (now) {
      if (start === null) start = now;
      var p = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = String(Math.round(target * eased));
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = String(target);
    };
    requestAnimationFrame(step);
  };

  if (!("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(counters, runCount);
  } else {
    var countObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          runCount(entry.target);
          countObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });
    Array.prototype.forEach.call(counters, function (el) {
      el.textContent = "0";
      countObserver.observe(el);
    });
  }

  /* ---------- Fan diagram draw-in ---------- */
  var fan = document.getElementById("fan");
  if (fan) {
    if (reduced || !("IntersectionObserver" in window)) {
      fan.setAttribute("data-drawn", "true");
    } else {
      var fanObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            // Stagger each link so the fan unfolds left to right.
            var links = entry.target.querySelectorAll(".fan-link");
            Array.prototype.forEach.call(links, function (link, i) {
              link.style.animationDelay = (i < 3 ? i * 0.08 : 0.28 + (i - 3) * 0.045) + "s";
            });
            entry.target.setAttribute("data-drawn", "true");
            fanObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.3 });
      fanObserver.observe(fan);
    }
  }

  /* ---------- Active section in nav ---------- */
  var links = document.querySelectorAll(".nav__links a");
  var sections = [];
  Array.prototype.forEach.call(links, function (link) {
    var id = link.getAttribute("href").slice(1);
    var el = document.getElementById(id);
    if (el) sections.push({ link: link, el: el });
  });

  if (sections.length && "IntersectionObserver" in window) {
    var visible = {};
    var sectionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        visible[entry.target.id] = entry.isIntersecting ? entry.intersectionRatio : 0;
      });
      var bestId = null, bestRatio = 0;
      sections.forEach(function (s) {
        var r = visible[s.el.id] || 0;
        if (r > bestRatio) { bestRatio = r; bestId = s.el.id; }
      });
      sections.forEach(function (s) {
        if (s.el.id === bestId) s.link.setAttribute("aria-current", "true");
        else s.link.removeAttribute("aria-current");
      });
    }, { threshold: [0, 0.15, 0.4, 0.75], rootMargin: "-20% 0px -40% 0px" });
    sections.forEach(function (s) { sectionObserver.observe(s.el); });
  }

  /* ---------- Footer year ---------- */
  var year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
})();
