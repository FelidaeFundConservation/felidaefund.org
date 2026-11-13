// Range map. The polygons are real shapes, so they can be pointed at,
// measured and switched off. The frame pans by dragging and zooms with
// its own buttons, the way a map is expected to behave; nothing here
// touches the page's own scrolling.
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

  map.addEventListener('pointerleave', reset);

  map.querySelectorAll('.rmtoggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const on = btn.getAttribute('aria-pressed') === 'true';
      btn.setAttribute('aria-pressed', String(!on));
      map.classList.toggle('hide-' + btn.dataset.band, on);
      reset();
    });
  });

  // ── Pan and zoom ──────────────────────────────────────────────────
  const stage = map.querySelector('.rangemap__stage');
  const svg = map.querySelector('.rangemap__svg');
  if (!stage || !svg) return;

  const frame = map.querySelector('.rangemap__frame');

  // The map stays desaturated and inert until the reader takes hold of
  // it, so it reads as one object in the middle of an article rather
  // than a live control competing for the pointer.
  const wake = () => frame && frame.classList.add('is-live');
  stage.addEventListener('pointerdown', wake);
  stage.addEventListener('focus', wake);
  map.querySelectorAll('.rmzoom').forEach(b => b.addEventListener('focus', wake));

  const base = (svg.dataset.base || '0 0 1000 1000').split(/\s+/).map(Number);
  const MIN = 1, MAX = 8;
  let zoom = 1, cx = base[0] + base[2] / 2, cy = base[1] + base[3] / 2;

  // preserveAspectRatio="slice" covers the frame, so the visible window is
  // narrower than the viewBox on one axis. Panning has to respect that,
  // otherwise the map can be dragged past its own edge.
  const visible = () => {
    const w = base[2] / zoom, h = base[3] / zoom;
    const fr = stage.clientWidth / stage.clientHeight;
    const vr = w / h;
    return fr > vr ? [w, w / fr] : [h * fr, h];
  };

  // Scale bar. Its length is recomputed every time the zoom changes, and
  // the distance it stands for is rounded to something a reader can use.
  const scaleEl = map.querySelector('.rangemap__scale');
  const kmPerUnit = scaleEl ? parseFloat(scaleEl.dataset.kmpu) : 0;
  const NICE = [1, 2, 5, 10, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000];

  const drawScale = (vw) => {
    if (!scaleEl || !kmPerUnit) return;
    const pxPerUnit = stage.clientWidth / vw;
    const targetKm = (stage.clientWidth * 0.22) / pxPerUnit * kmPerUnit;
    let km = NICE[0];
    for (const n of NICE) if (n <= targetKm) km = n;
    scaleEl.querySelector('.rangemap__scale-bar').style.width =
      Math.round((km / kmPerUnit) * pxPerUnit) + 'px';
    scaleEl.querySelector('.rangemap__scale-label').textContent =
      km.toLocaleString() + ' km';
  };

  const apply = () => {
    const w = base[2] / zoom, h = base[3] / zoom;
    const [vw, vh] = visible();
    cx = Math.min(base[0] + base[2] - vw / 2, Math.max(base[0] + vw / 2, cx));
    cy = Math.min(base[1] + base[3] - vh / 2, Math.max(base[1] + vh / 2, cy));
    svg.setAttribute('viewBox', `${cx - w / 2} ${cy - h / 2} ${w} ${h}`);
    map.style.setProperty('--rm-zoom', zoom);
    drawScale(vw);
    // Reset only has a job once the view has actually moved.
    if (frame) {
      const moved = Math.abs(zoom - 1) > 1e-6
        || Math.abs(cx - (base[0] + base[2] / 2)) > 0.5
        || Math.abs(cy - (base[1] + base[3] / 2)) > 0.5;
      frame.classList.toggle('is-moved', moved);
    }
    map.querySelector('[data-zoom="in"]').disabled = zoom >= MAX - 1e-6;
    map.querySelector('[data-zoom="out"]').disabled = zoom <= MIN + 1e-6;
  };

  const setZoom = (next) => { zoom = Math.min(MAX, Math.max(MIN, next)); apply(); };

  map.querySelectorAll('.rmzoom').forEach(b => {
    b.addEventListener('click', (e) => {
      e.stopPropagation();
      const k = b.dataset.zoom;
      if (k === 'in') setZoom(zoom * 1.5);
      else if (k === 'out') setZoom(zoom / 1.5);
      else { zoom = 1; cx = base[0] + base[2] / 2; cy = base[1] + base[3] / 2; apply(); }
    });
  });

  // Drag to move. Pointer capture keeps the gesture alive if the cursor
  // leaves the frame mid-drag.
  let drag = null;
  stage.addEventListener('pointerdown', (e) => {
    if (e.button !== 0) return;
    e.preventDefault();          // no drag-select, no image ghost drag
    const [vw, vh] = visible();
    drag = { x: e.clientX, y: e.clientY, cx, cy,
             ux: vw / stage.clientWidth, uy: vh / stage.clientHeight, moved: false };
    stage.setPointerCapture(e.pointerId);
    stage.classList.add('is-dragging');
  });
  stage.addEventListener('pointermove', (e) => {
    if (drag) {
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      if (Math.abs(dx) + Math.abs(dy) > 3) drag.moved = true;
      cx = drag.cx - dx * drag.ux;
      cy = drag.cy - dy * drag.uy;
      apply();
      return;
    }
    const t = e.target.closest('.rp');
    if (t) show(t);
  });
  const endDrag = (e) => {
    if (!drag) return;
    stage.classList.remove('is-dragging');
    try { stage.releasePointerCapture(e.pointerId); } catch (_) {}
    drag = null;
  };
  stage.addEventListener('pointerup', endDrag);
  stage.addEventListener('pointercancel', endDrag);

  // Tapping a shape still reports it, as long as it was a tap not a drag.
  stage.addEventListener('click', (e) => {
    const t = e.target.closest('.rp');
    if (t) show(t);
  });

  // Keyboard: arrows pan, +/- zoom, 0 resets.
  stage.addEventListener('keydown', (e) => {
    const [vw, vh] = visible();
    const step = 0.12;
    const moves = { ArrowLeft: [-vw * step, 0], ArrowRight: [vw * step, 0],
                    ArrowUp: [0, -vh * step], ArrowDown: [0, vh * step] };
    if (moves[e.key]) { e.preventDefault(); cx += moves[e.key][0]; cy += moves[e.key][1]; apply(); }
    else if (e.key === '+' || e.key === '=') { e.preventDefault(); setZoom(zoom * 1.5); }
    else if (e.key === '-' || e.key === '_') { e.preventDefault(); setZoom(zoom / 1.5); }
    else if (e.key === '0') { e.preventDefault(); zoom = 1; cx = base[0] + base[2] / 2; cy = base[1] + base[3] / 2; apply(); }
  });

  window.addEventListener('resize', apply);
  apply();
})();
