// <site-nav> — the shared navigation and mobile menu.
// Markup and behaviour travel together; styles live in components.css.
class SiteNav extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `<nav class="nav" id="nav" role="navigation" aria-label="Main navigation">
    <div class="nav__inner">

      <!-- Logo, and a separate control for the prototype's theme picker -->
      <div class="nav__logo-wrap">
        <a href="index.html" class="nav__logo" aria-label="Felidae Conservation Fund — home">
          <img src="assets/logo/logo_felidae_neg-01.png" alt="Felidae Conservation Fund" class="nav__logo-img" />
        </a>
        <!-- Theme picker parked at Irene's request. The two themes and
             their tokens still exist; put the trigger and the picker back
             to switch between them. -->


      <!-- Desktop Links -->
      <ul class="nav__links" role="list">
        <!-- Projects -->
        <li class="nav__item" role="listitem">
          <a href="#" class="nav__link">
            Projects
            <svg class="nav__chevron" viewBox="0 0 12 12" aria-hidden="true"><polyline points="2,4 6,8 10,4"/></svg>
          </a>
          <div class="nav__dropdown nav__dropdown--mega" role="menu" aria-label="Projects submenu">
            <div class="nav__col">
              <div class="nav__col-head">Research Projects</div>
              <a href="project-bhutan.html" role="menuitem">Bhutan Wild Cat Health Project</a>
              <a href="project-patagonia.html" role="menuitem">Patagonia Wild Cats Project</a>
              <a href="project-pumalink.html" role="menuitem">Diablo PumaLink Project</a>
              <a href="project-bobcat.html" role="menuitem">Bay Area Bobcat Project</a>
              <a href="project-tsavo.html" role="menuitem">Tsavo Cheetah Project</a>
              <a href="project-bapp.html" role="menuitem">Bay Area Puma Project</a>
              <a href="project-wildcat-health.html" role="menuitem">Wild Cat Health Project</a>
              <a href="projects.html" role="menuitem" style="color: var(--gold-300);">View all projects →</a>
            </div>
            <div class="nav__col">
              <div class="nav__col-head">Community Programs</div>
              <a href="project-living-with-lions.html" role="menuitem">Living with Lions</a>
              <a href="project-cat-aware.html" role="menuitem">CAT Aware</a>
              <a href="project-wilde-pod.html" role="menuitem">Wilde Pod</a>
              <a href="project-wilde-backyard.html" role="menuitem">Wilde Backyard</a>
            </div>
          </div>
        </li>
        <!-- Learn -->
        <li class="nav__item" role="listitem">
          <a href="#" class="nav__link">
            Learn
            <svg class="nav__chevron" viewBox="0 0 12 12" aria-hidden="true"><polyline points="2,4 6,8 10,4"/></svg>
          </a>
          <div class="nav__dropdown" role="menu" aria-label="Learn submenu">
            <a href="mission.html" role="menuitem">Our Mission</a>
            <a href="science.html" role="menuitem">Science &amp; Research</a>
            <a href="news.html" role="menuitem">News</a>
            <a href="about.html" role="menuitem">About Us</a>
            <a href="learn-cats.html" role="menuitem">Wild Cat Species of the World</a>
            <a href="learn-ecosystems.html" role="menuitem">Protecting Healthy Ecosystems</a>
            <a href="learn-living-alongside.html" role="menuitem">Living Alongside Wild Cats</a>
            <a href="learn-safety.html" role="menuitem">Safety Essentials</a>
            <a href="learn-media.html" role="menuitem">Photos &amp; Videos</a>
            <a href="kids.html" role="menuitem">Kids Area</a>
          </div>
        </li>
        <!-- Get Involved -->
        <li class="nav__item" role="listitem">
          <a href="#" class="nav__link">
            Get Involved
            <svg class="nav__chevron" viewBox="0 0 12 12" aria-hidden="true"><polyline points="2,4 6,8 10,4"/></svg>
          </a>
          <div class="nav__dropdown" role="menu" aria-label="Get Involved submenu">
            <a href="volunteer.html" role="menuitem">Volunteer</a>
            <a href="spread-awareness.html" role="menuitem">Spread Awareness</a>
            <a href="community-science.html" role="menuitem">Community Scientist</a>
            <a href="project-wilde-pod.html" role="menuitem">Trail Cam Data (Wilde Pod)</a>
            <a href="events.html" role="menuitem">Events</a>
            <a href="ways-to-donate.html" role="menuitem">Ways to Donate</a>
            <a href="store.html" role="menuitem">Store</a>
            <a href="take-action.html" role="menuitem">Take Action</a>
          </div>
        </li>
      </ul>

      <!-- Right -->
      <div class="nav__right">
        <button class="nav__search" aria-label="Search">
          <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <circle cx="8.5" cy="8.5" r="5.5"/>
            <line x1="13" y1="13" x2="18" y2="18"/>
          </svg>
        </button>
        <div class="nav__badges">
          <a href="https://app.candid.org/profile/7041082/felidae-conservation-fund-20-5089093" target="_blank" rel="noopener">
            <img src="assets/badges/candid-platinum-2026.png" alt="Candid Platinum Seal of Transparency 2026" />
          </a>
          <a href="https://greatnonprofits.org/org/felidae-conservation-fund" target="_blank" rel="noopener">
            <img src="assets/badges/greatnonprofits-top-rated-2025.png" alt="GreatNonprofits 2025 Top-Rated Nonprofit" />
          </a>
          <a href="https://www.charitynavigator.org/ein/205089093" target="_blank" rel="noopener">
            <img src="assets/badges/charity-navigator-four-star-2026.png" alt="Charity Navigator Four-Star Rating 2026" />
          </a>
        </div>
        <a href="#" class="nav__donate" onclick="openDonate(event)">Donate</a>
      </div>

      <!-- Mobile hamburger -->
      <button class="nav__hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>

    <!-- Mobile menu -->
    <div class="nav__mobile" id="mobileMenu" aria-hidden="true">
      <div class="mob-panels" id="mobPanels">
        <!-- L1: top-level items -->
        <div class="mob-panel" id="mobL1">
          <button class="mob-top-item" data-menu="Projects">Projects <svg viewBox="0 0 16 16" aria-hidden="true"><polyline points="6,3 11,8 6,13"/></svg></button>
          <button class="mob-top-item" data-menu="Learn">Learn <svg viewBox="0 0 16 16" aria-hidden="true"><polyline points="6,3 11,8 6,13"/></svg></button>
          <button class="mob-top-item" data-menu="Get Involved">Get Involved <svg viewBox="0 0 16 16" aria-hidden="true"><polyline points="6,3 11,8 6,13"/></svg></button>
          <a href="#" class="mob-donate" onclick="openDonate(event)">Donate Now</a>
          <div class="mob-badges">
            <a href="https://app.candid.org/profile/7041082/felidae-conservation-fund-20-5089093" target="_blank" rel="noopener">
              <img src="assets/badges/candid-platinum-2026.png" alt="Candid Platinum Seal of Transparency 2026" />
            </a>
            <a href="https://greatnonprofits.org/org/felidae-conservation-fund" target="_blank" rel="noopener">
              <img src="assets/badges/greatnonprofits-top-rated-2025.png" alt="GreatNonprofits 2025 Top-Rated Nonprofit" />
            </a>
            <a href="https://www.charitynavigator.org/ein/205089093" target="_blank" rel="noopener">
              <img src="assets/badges/charity-navigator-four-star-2026.png" alt="Charity Navigator Four-Star Rating 2026" />
            </a>
          </div>
          <div class="mob-search">
            <svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.5" stroke="currentColor" stroke-width="1.8" fill="none"/><path d="M13 13l4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
            <input type="search" class="mob-search__input" placeholder="Search…" aria-label="Search site">
          </div>
        </div>
        <!-- L2: submenu -->
        <div class="mob-panel" id="mobL2">
          <button class="mob-back" id="mobBack">
            <svg viewBox="0 0 16 16" aria-hidden="true"><polyline points="10,3 5,8 10,13"/></svg>
            Menu
          </button>
          <div class="mob-panel-title" id="mobPanelTitle"></div>
          <div id="mobSubLinks"></div>
        </div>
      </div>
    </div>
  </nav>`;
    initNav();
  }
}

function initNav() {
    // ── Nav scroll state ──────────────────────────────────────────────
    const nav = document.getElementById('nav');
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });

    // ── Mobile hamburger ──────────────────────────────────────────────
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobPanels = document.getElementById('mobPanels');
    const mobPanelTitle = document.getElementById('mobPanelTitle');
    const mobSubLinks = document.getElementById('mobSubLinks');
    const mobBack = document.getElementById('mobBack');

    const menuData = {
      'Projects': [
        'Bhutan Wild Cat Health Project','Patagonia Wild Cats Project',
        'Diablo PumaLink Project','Bay Area Bobcat Project',
        'Tsavo Cheetah Project','Bay Area Puma Project','Wild Cat Health Project',
        '## Community Programs',
        'Living with Lions','CAT Aware','Wilde Pod','Wilde Backyard'
      ],
      'Learn': [
        'Our Mission','Science & Research','News','About Us',
        'Wild Cat Species of the World','Protecting Healthy Ecosystems',
        'Living Alongside Wild Cats','Safety Essentials',
        'Photos & Videos','Kids Area'
      ],
      'Get Involved': [
        'Volunteer','Spread Awareness','Community Scientist','Trail Cam Data (Wilde Pod)','Events',
        'Ways to Donate','Store','Take Action'
      ]
    };

    // Interim mapping of menu items to existing felidaefund.org pages (clear 1:1 matches only).
    // Items not listed here remain '#' placeholders pending the full site rework.
    const navLinks = {
      'Bhutan Wild Cat Health Project': 'project-bhutan.html',
      'Patagonia Wild Cats Project':    'project-patagonia.html',
      'Diablo PumaLink Project':        'project-pumalink.html',
      'Bay Area Bobcat Project':        'project-bobcat.html',
      'Tsavo Cheetah Project':          'project-tsavo.html',
      'Bay Area Puma Project':          'project-bapp.html',
      'Wild Cat Health Project':        'project-wildcat-health.html',
      'Our Mission':                    'mission.html',
      'About Us':                       'about.html',
      'Science & Research':             'science.html',
      'Wild Cat Species of the World':  'learn-cats.html',
      'Protecting Healthy Ecosystems':  'learn-ecosystems.html',
      'Living Alongside Wild Cats':     'learn-living-alongside.html',
      'Living with Lions':              'project-living-with-lions.html',
      'CAT Aware':                      'project-cat-aware.html',
      'Wilde Pod':                      'project-wilde-pod.html',
      'Wilde Backyard':                 'project-wilde-backyard.html',
      'Safety Essentials':              'learn-safety.html',
      'Photos & Videos':               'learn-media.html',
      'Kids Area':                      'kids.html',
      'News':                           'news.html',
      'Volunteer':                      'volunteer.html',
      'Spread Awareness':               'spread-awareness.html',
      'Community Scientist':            'community-science.html',
      'Trail Cam Data (Wilde Pod)':     'project-wilde-pod.html',
      'Events':                         'events.html',
      'Ways to Donate':                 'ways-to-donate.html',
      'Store':                          'store.html',
      'Take Action':                    'take-action.html'
    };

    function openMobileMenu(isOpen) {
      hamburger.classList.toggle('open', isOpen);
      mobileMenu.classList.toggle('open', isOpen);
      hamburger.setAttribute('aria-expanded', String(isOpen));
      mobileMenu.setAttribute('aria-hidden', String(!isOpen));
      if (!isOpen) mobPanels.classList.remove('show-sub');
    }

    hamburger.addEventListener('click', () => {
      openMobileMenu(!hamburger.classList.contains('open'));
    });

    document.querySelectorAll('.mob-top-item').forEach(btn => {
      btn.addEventListener('click', () => {
        const key = btn.dataset.menu;
        mobPanelTitle.textContent = key;
        mobSubLinks.innerHTML = menuData[key].map(item => {
          if (item === '---') return '<div class="mob-sub-divider"></div>';
          if (item.startsWith('## ')) return `<div class="mob-sub-heading">${item.slice(3)}</div>`;
          const url = navLinks[item];
          return url
            ? `<a href="${url}" class="mob-sub-link">${item}</a>`
            : `<a href="#" class="mob-sub-link">${item}</a>`;
        }).join('');
        mobPanels.classList.add('show-sub');
        document.getElementById('mobL2').scrollTop = 0;
      });
    });

    mobBack.addEventListener('click', () => {
      mobPanels.classList.remove('show-sub');
    });

  // ── Theme picker (parked) ─────────────────────────────────────────
  // The trigger and the picker are out of the markup for now. The two
  // themes and their tokens are untouched, and a theme saved earlier is
  // still honoured, so putting the control back is a markup change only.
  const themeTrigger = document.getElementById('logoThemeTrigger');
  const themePicker  = document.getElementById('themePicker');
  const themeButtons = themePicker ? themePicker.querySelectorAll('.theme-option') : [];

  function applyTheme(id) {
    if (id === '1') document.documentElement.removeAttribute('data-theme');
    else document.documentElement.setAttribute('data-theme', id);
    themeButtons.forEach(b => b.classList.toggle('active', b.dataset.themeId === id));
    localStorage.setItem('felidae-theme', id);
  }

  if (themeTrigger && themePicker) {
    themeTrigger.addEventListener('click', (e) => {
      e.preventDefault();
      themePicker.classList.toggle('open');
    });
    themeButtons.forEach(btn => btn.addEventListener('click', () => {
      applyTheme(btn.dataset.themeId);
      themePicker.classList.remove('open');
    }));
    document.addEventListener('click', (e) => {
      if (!themeTrigger.contains(e.target) && !themePicker.contains(e.target))
        themePicker.classList.remove('open');
    });
  }

  // Restore saved theme on load
  const saved = localStorage.getItem('felidae-theme');
  if (saved && saved !== '1') applyTheme(saved);
}

customElements.define('site-nav', SiteNav);
