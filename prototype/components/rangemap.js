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
