// Range map. The polygons are real shapes, so they can be pointed at,
// measured and switched off. The readout and the toggles sit in a sticky
// header: the map is often taller than the window, and a readout that
// scrolls out of view while you are still pointing at the map is useless.
(() => {
  const map = document.querySelector('.rangemap');
  if (!map) return;

  const readout = map.querySelector('.rangemap__readout');
  const idle = readout ? readout.innerHTML : '';
  const LABEL = { resident: 'Resident', possible: 'Possibly resident' };

  const clear = () => map.querySelectorAll('.rp.is-on').forEach(p => p.classList.remove('is-on'));
  const reset = () => { clear(); readout.innerHTML = idle; };

  const show = (el) => {
    clear();
    el.classList.add('is-on');
    readout.innerHTML = '<b></b><span class="rangemap__share"></span>';
    readout.querySelector('b').textContent = LABEL[el.dataset.band] || '';
    readout.querySelector('.rangemap__share').textContent =
      ' — ' + el.dataset.share + '% of this species’ mapped range';
  };

  map.addEventListener('pointerover', (e) => {
    const t = e.target.closest('.rp');
    if (t) show(t);
  });
  map.addEventListener('pointerleave', reset);
  map.addEventListener('click', (e) => {
    const t = e.target.closest('.rp');
    if (t) show(t);
  });

  // The frame scrolls only once the reader activates it. Until then it
  // is a picture, and the page scrolls normally over the top of it.
  const stage = map.querySelector('.rangemap__stage');
  if (stage) {
    const svg = stage.querySelector('.rangemap__svg');
    const vb = (svg.getAttribute('viewBox') || '0 0 1 1').split(/\s+/).map(Number);
    const ratio = vb[2] / vb[3];

    // Fill the frame in both axes. Width alone leaves dead space whenever
    // the frame is taller than the map's aspect, which is most phones.
    const cover = () => {
      const w = stage.clientWidth, h = stage.clientHeight;
      svg.style.width = Math.max(w, Math.ceil(h * ratio)) + 'px';
      svg.style.height = 'auto';
    };

    const centre = () => {
      cover();
      stage.scrollTop = Math.max(0, (stage.scrollHeight - stage.clientHeight) / 2);
      stage.scrollLeft = Math.max(0, (stage.scrollWidth - stage.clientWidth) / 2);
    };
    const live = (on) => {
      stage.classList.toggle('is-live', on);
      if (on) centre();
    };
    // Start showing the middle of the range rather than its top edge.
    // The SVG has to be laid out first, so this runs again after load.
    requestAnimationFrame(centre);
    window.addEventListener('load', centre);
    window.addEventListener('resize', () => {
      if (!stage.classList.contains('is-live')) centre();
    });
    setTimeout(centre, 400);
    stage.addEventListener('click', () => live(true));
    stage.addEventListener('focus', () => live(true));
    stage.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { live(false); stage.blur(); }
    });
    document.addEventListener('click', (e) => {
      if (!stage.contains(e.target)) live(false);
    });
  }

  // Hiding a band is only possible because the shapes are drawn live.
  map.querySelectorAll('.rmtoggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const on = btn.getAttribute('aria-pressed') === 'true';
      btn.setAttribute('aria-pressed', String(!on));
      map.classList.toggle('hide-' + btn.dataset.band, on);
      reset();
    });
  });
})();
