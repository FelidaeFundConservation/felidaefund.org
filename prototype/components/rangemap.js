// Range map. The SVG is the picture; the country list below it is the
// control. A grouped list of named buttons is a better keyboard and screen
// reader affordance than 58 tab stops on unlabelled shapes, and both drive
// the same readout.
(() => {
  const map = document.querySelector('.rangemap');
  if (!map) return;

  const readout = map.querySelector('.rangemap__readout');
  const idle = readout ? readout.innerHTML : '';
  const LABEL = {
    resident: 'Resident',
    possible: 'Possibly resident',
    gone: 'No longer present'
  };

  // One country can be several paths (islands, exclaves).
  const byName = new Map();
  map.querySelectorAll('.rg[data-hit]').forEach(p => {
    const n = p.dataset.name;
    if (!byName.has(n)) byName.set(n, []);
    byName.get(n).push(p);
  });

  const clear = () => map.querySelectorAll('.rg.is-on').forEach(p => p.classList.remove('is-on'));

  const show = (name) => {
    clear();
    const paths = byName.get(name);
    if (!paths) { readout.innerHTML = idle; return; }
    paths.forEach(p => p.classList.add('is-on'));
    const state = LABEL[paths[0].dataset.state] || '';
    readout.innerHTML = '<b></b> <span class="rangemap__status"></span>';
    readout.querySelector('b').textContent = name;
    readout.querySelector('.rangemap__status').textContent = '— ' + state;
  };

  const reset = () => { clear(); readout.innerHTML = idle; };

  // Pointing at the map itself.
  map.addEventListener('pointerover', (e) => {
    const t = e.target.closest('.rg[data-hit]');
    if (t) show(t.dataset.name);
  });
  map.addEventListener('pointerleave', reset);

  // The list: hover, focus and click all do the same thing, so the map
  // responds identically to a mouse, a keyboard and a screen reader.
  map.addEventListener('pointerover', (e) => {
    const b = e.target.closest('.rc__btn');
    if (b) show(b.dataset.country);
  });
  map.addEventListener('focusin', (e) => {
    const b = e.target.closest('.rc__btn');
    if (b) show(b.dataset.country);
  });
  map.addEventListener('click', (e) => {
    const b = e.target.closest('.rc__btn');
    if (b) show(b.dataset.country);
  });
  const list = map.querySelector('.rc');
  if (list) list.addEventListener('pointerleave', reset);
})();
