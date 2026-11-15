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

// Contents rail: mark the section being read. Uses scroll position rather
// than an IntersectionObserver because sections vary from one short
// paragraph to a screenful, and "which heading did I last pass" is the
// question the rail answers.
(() => {
  const toc = document.querySelector('.toc');
  if (!toc) return;
  const links = [...toc.querySelectorAll('a[href^="#"]')];
  const targets = links
    .map(a => ({ a, el: document.getElementById(a.getAttribute('href').slice(1)) }))
    .filter(t => t.el);
  if (!targets.length) return;

  const navH = parseInt(getComputedStyle(document.documentElement)
    .getPropertyValue('--nav-h'), 10) || 86;

  let frame = null;
  const mark = () => {
    frame = null;
    const line = window.scrollY + navH + 90;
    let current = targets[0];
    for (const t of targets) {
      if (t.el.getBoundingClientRect().top + window.scrollY <= line) current = t;
    }
    for (const t of targets) t.a.classList.toggle('is-current', t === current);
  };
  const queue = () => { if (!frame) frame = requestAnimationFrame(mark); };

  window.addEventListener('scroll', queue, { passive: true });
  window.addEventListener('resize', queue);
  mark();
})();
