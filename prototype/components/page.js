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
//
// The same reading drives the jump pill, which is what narrow screens get
// in place of the rail: the rail is display:none under 1040px, and a six
// section page with no way to see its own shape is worse on a phone than
// on a desktop, not better.
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

  // ── Jump pill ──────────────────────────────────────────────────────
  const still = window.matchMedia('(prefers-reduced-motion: reduce)');
  const behavior = () => (still.matches ? 'auto' : 'smooth');

  const jump = document.createElement('div');
  jump.className = 'jump';
  jump.innerHTML =
    '<button type="button" class="jump__fab" aria-expanded="false" aria-controls="jump-sheet">' +
      '<span class="jump__here"></span>' +
      '<svg class="jump__caret" width="11" height="7" viewBox="0 0 11 7" aria-hidden="true">' +
        '<path d="M1 5.5 5.5 1 10 5.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>' +
      '</svg>' +
    '</button>' +
    '<div class="jump__scrim" hidden></div>' +
    '<div class="jump__sheet" id="jump-sheet" role="dialog" aria-modal="true" aria-label="Jump to a section" hidden>' +
      '<div class="jump__grip"></div>' +
      '<p class="jump__title">On this page</p>' +
      '<div class="jump__ends">' +
        '<button type="button" class="jump__end" data-end="top">&uarr; Top of page</button>' +
        '<button type="button" class="jump__end" data-end="bottom">&darr; Bottom</button>' +
      '</div>' +
      '<ul class="jump__list"></ul>' +
    '</div>';

  const fab = jump.querySelector('.jump__fab');
  const here = jump.querySelector('.jump__here');
  const scrim = jump.querySelector('.jump__scrim');
  const sheet = jump.querySelector('.jump__sheet');
  const list = jump.querySelector('.jump__list');

  targets.forEach((t, i) => {
    const li = document.createElement('li');
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'jump__link';
    b.textContent = t.a.textContent.trim();
    b.addEventListener('click', () => {
      close();
      t.el.scrollIntoView({ behavior: behavior(), block: 'start' });
    });
    t.jumpLink = b;
    li.appendChild(b);
    list.appendChild(li);
  });

  // hidden is removed on open and restored on close, so the sheet and the
  // scrim stay out of the tab order while they are off screen.
  let open = false;
  const setOpen = (next) => {
    open = next;
    if (next) {
      scrim.hidden = false; sheet.hidden = false;
      // Flush layout synchronously so the sheet animates up from off
      // screen. A rAF would do it too, but rAF is throttled when the tab
      // is not being painted, and the class would then lag the open and
      // close timers and leave the two out of step.
      void sheet.offsetHeight;
    }
    jump.classList.toggle('is-open', next);
    fab.setAttribute('aria-expanded', String(next));
    if (next) sheet.querySelector('.jump__link[aria-current="true"], .jump__link').focus();
  };
  const close = () => {
    if (!open) return;
    setOpen(false);
    fab.focus();
    const tidy = () => { if (!open) { scrim.hidden = true; sheet.hidden = true; } };
    still.matches ? tidy() : window.setTimeout(tidy, 280);
  };

  fab.addEventListener('click', () => (open ? close() : setOpen(true)));
  scrim.addEventListener('click', close);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });

  jump.querySelectorAll('.jump__end').forEach(b => {
    b.addEventListener('click', () => {
      close();
      window.scrollTo({
        top: b.dataset.end === 'top' ? 0 : document.documentElement.scrollHeight,
        behavior: behavior()
      });
    });
  });

  document.body.appendChild(jump);

  // ── Shared position reading ────────────────────────────────────────
  let frame = null;
  const mark = () => {
    frame = null;
    const line = window.scrollY + navH + 90;
    let current = targets[0];
    for (const t of targets) {
      if (t.el.getBoundingClientRect().top + window.scrollY <= line) current = t;
    }
    for (const t of targets) {
      t.a.classList.toggle('is-current', t === current);
      t.jumpLink.setAttribute('aria-current', String(t === current));
    }
    here.textContent = current.a.textContent.trim();
    // The pill appears once the first section is in play. offsetTop is no
    // use here: it is measured from the offset parent, not the page.
    const firstTop = targets[0].el.getBoundingClientRect().top + window.scrollY;
    jump.classList.toggle('is-ready', window.scrollY > firstTop - navH - 160);
  };
  const queue = () => { if (!frame) frame = requestAnimationFrame(mark); };

  window.addEventListener('scroll', queue, { passive: true });
  window.addEventListener('resize', queue);
  mark();
})();
