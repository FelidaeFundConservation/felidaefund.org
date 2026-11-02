// Felidae homepage — counters and scroll reveal.
// No libraries. Both effects degrade safely: without this file the
// numbers show their final values and the sections simply appear.
(function () {
  'use strict';
  var root = document.querySelector('.fx-home');
  if (!root) return;

  if (!('IntersectionObserver' in window)) {           // very old browser
    root.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('visible'); });
    root.querySelectorAll('[data-target]').forEach(function (el) {
      el.textContent = el.dataset.format === 'M'
        ? (el.dataset.target / 1000000).toFixed(1) + 'M'
        : (+el.dataset.target).toLocaleString();
    });
    return;
  }

  // ── Animated counters ─────────────────────────────────────────────
  // data-format: 'M' → 3.6M, 'k' → 150k; else 488 / 9,957. data-suffix (e.g. '+') is
  // appended so it sits on the same line as the number.
  function fmtCounter(el, val) {
    const f = el.dataset.format;
    const n = f === 'M' ? (val / 1000000).toFixed(1) + 'M'
            : f === 'k' ? Math.floor(val / 1000) + 'k'
            : Math.floor(val).toLocaleString();
    return n + (el.dataset.suffix || '');
  }
  function animateCounter(el, target, duration = 1800) {
    const start = performance.now();
    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const val = eased * target;
      el.textContent = fmtCounter(el, val);
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = fmtCounter(el, target);
    };
    requestAnimationFrame(step);
  }
    const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const target = parseInt(e.target.dataset.target, 10);
        animateCounter(e.target, target);
        counterObserver.unobserve(e.target);
      }
    });
  }, { threshold: 0.5 });
  root.querySelectorAll('[data-target]').forEach(el => counterObserver.observe(el));

  // The hero fills whatever the Joomla header leaves. Its own height does not
  // affect its top, so this is safe to read at any scroll position.
  var setHeroOffset = function () {
    var hero = root.querySelector('.hero');
    if (!hero) return;
    var top = Math.round(hero.getBoundingClientRect().top + window.scrollY);
    document.documentElement.style.setProperty('--fx-hero-offset', top + 'px');
  };
  setHeroOffset();
  window.addEventListener('resize', setHeroOffset);

  var revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('visible'); revealObserver.unobserve(e.target); }
    });
  }, { threshold: 0.12 });
  root.querySelectorAll('.reveal').forEach(function (el) { revealObserver.observe(el); });
})();
