// Scroll reveal — shared by every page. Loaded with defer so the
// markup (including the components) exists before we observe it.

const reveals = document.querySelectorAll('.reveal');
const show = (el) => el.classList.add('visible');

// Anyone who has asked for less motion gets the content, not the animation.
const stillMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

if (stillMotion.matches || !('IntersectionObserver' in window)) {
  reveals.forEach(show);
} else {
  // threshold must stay 0. It is a fraction of the ELEMENT's own area, so
  // any positive value is unreachable once an element is taller than the
  // viewport — a long .prose block would then never reveal and the page
  // below the lede would stay blank. rootMargin does the "wait until it is
  // properly on screen" job instead, and works at any element height.
  const observer = new IntersectionObserver(
    (entries) => entries.forEach(e => {
      if (e.isIntersecting) { show(e.target); observer.unobserve(e.target); }
    }),
    { threshold: 0, rootMargin: '0px 0px -80px 0px' }
  );
  reveals.forEach(el => observer.observe(el));

  // Last resort. Content must never be permanently invisible because an
  // observer did not fire.
  window.setTimeout(() => reveals.forEach(show), 2500);
}

// Species call to action: the monthly amount chips behave as one choice.
document.querySelectorAll('.cta__amounts').forEach(group => {
  group.addEventListener('click', (e) => {
    const b = e.target.closest('.cta__amt');
    if (!b) return;
    group.querySelectorAll('.cta__amt').forEach(x => {
      const on = x === b;
      x.classList.toggle('is-on', on);
      x.setAttribute('aria-pressed', String(on));
    });
  });
});
