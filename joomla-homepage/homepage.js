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
  function animateCounter(el, target, duration = 1800) {
    const fmt = el.dataset.format;
    const start = performance.now();
    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const val = eased * target;
      if (fmt === 'M') {
        el.textContent = (val / 1000000).toFixed(1) + 'M';
      } else {
        el.textContent = Math.floor(val).toLocaleString();
      }
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = fmt === 'M' ? (target / 1000000).toFixed(1) + 'M' : target.toLocaleString();
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
