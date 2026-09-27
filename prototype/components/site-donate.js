// <site-donate> — the donation modal, shared by every page.
// The nav's Donate links call openDonate(), so these stay global.

let donateModal;
let currentAmount = 25;
let currentFreq = 'monthly';

class SiteDonate extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
  <div class="modal-overlay" id="donateModal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
    <div class="modal" role="document">
      <div class="modal__header">
        <h2 class="modal__header-title" id="modal-title">Support Wild Cats</h2>
        <button class="modal__close" onclick="closeDonate()" aria-label="Close donation dialog">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <line x1="2" y1="2" x2="16" y2="16"/><line x1="16" y1="2" x2="2" y2="16"/>
          </svg>
        </button>
      </div>
      <div class="modal__body">
        <p class="modal__subtitle">Your gift funds field research, community science, and habitat protection — where wild cats need it most.</p>

        <!-- Frequency -->
        <div class="donate-freq" role="group" aria-label="Donation frequency">
          <button class="donate-freq__btn active" onclick="setFreq(this, 'monthly')">Monthly</button>
          <button class="donate-freq__btn" onclick="setFreq(this, 'once')">One-time</button>
        </div>

        <!-- Amounts -->
        <div class="donate-amounts" role="group" aria-label="Donation amount">
          <button class="donate-amount selected" onclick="selectAmount(this, 25)">
            $25
            <small>Camera trap</small>
          </button>
          <button class="donate-amount" onclick="selectAmount(this, 50)">
            $50
            <small>GPS tag battery</small>
          </button>
          <button class="donate-amount" onclick="selectAmount(this, 100)">
            $100
            <small>Field day</small>
          </button>
          <button class="donate-amount" onclick="selectAmount(this, 250)">
            $250
            <small>Collar deployment</small>
          </button>
          <button class="donate-amount" onclick="selectAmount(this, 500)">
            $500
            <small>1 week in the field</small>
          </button>
          <button class="donate-amount" onclick="selectAmount(this, null)">
            Other
            <small>Your amount</small>
          </button>
        </div>

        <!-- Custom amount -->
        <div class="donate-custom" id="customAmount" style="display:none">
          <span class="donate-custom__label">$</span>
          <input type="number" class="donate-custom__input" id="customInput" placeholder="Enter amount" min="1" aria-label="Custom donation amount" />
        </div>

        <!-- Impact message -->
        <div class="donate-impact" id="donateImpact">
          "$25/month keeps a camera trap running for a full year — capturing the data we need to protect wild cats."
        </div>

        <button class="donate-submit" id="donateBtn">Give $25 / month</button>
        <p class="donate-note">🔒 Secure processing via Stripe. Felidae Conservation Fund is a 501(c)(3) nonprofit — your gift is tax-deductible.</p>
      </div>
    </div>
  </div>
`;
    initDonate();
  }
}

function initDonate() {
  // ── Donate modal ──────────────────────────────────────────────────
  donateModal = document.getElementById('donateModal');

  function openDonate(e) {
    if (e) e.preventDefault();
    donateModal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeDonate() {
    donateModal.classList.remove('open');
    document.body.style.overflow = '';
  }
  donateModal.addEventListener('click', (e) => {
    if (e.target === donateModal) closeDonate();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && donateModal.classList.contains('open')) closeDonate();
  });

  const impactMessages = {
    25:  '"$25/month keeps a camera trap running for a full year — capturing the data we need to protect wild cats."',
    50:  '"$50 powers GPS collar batteries that tell us exactly where wild cats roam and what corridors they need."',
    100: '"$100 funds a full field day — two researchers, travel, and data collection in the habitat."',
    250: '"$250 deploys a GPS collar on a wild cat, giving us months of movement data we\'d never get otherwise."',
    500: '"$500 sends a field team into the wild for a full week of monitoring, health assessments, and camera checks."',
  };

  function updateDonateBtn() {
    const btn = document.getElementById('donateBtn');
    const impact = document.getElementById('donateImpact');
    const label = currentFreq === 'monthly' ? '/ month' : '';
    btn.textContent = currentAmount ? `Give $${currentAmount.toLocaleString()} ${label}`.trim() : `Give ${label}`.trim();
    impact.textContent = impactMessages[currentAmount] || '"Every dollar funds real science — from camera traps to GPS collars to field teams in the most remote habitats."';
  }

  function setFreq(btn, freq) {
    currentFreq = freq;
    document.querySelectorAll('.donate-freq__btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    updateDonateBtn();
  }

  function selectAmount(btn, amount) {
    document.querySelectorAll('.donate-amount').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    const customDiv = document.getElementById('customAmount');
    if (amount === null) {
      currentAmount = null;
      customDiv.style.display = 'flex';
      document.getElementById('customInput').focus();
    } else {
      currentAmount = amount;
      customDiv.style.display = 'none';
    }
    updateDonateBtn();
  }

  document.getElementById('customInput').addEventListener('input', (e) => {
    currentAmount = parseInt(e.target.value, 10) || null;
    updateDonateBtn();
  });

  // The markup's onclick attributes resolve against the global scope.
  Object.assign(window, { openDonate, closeDonate, setFreq, selectAmount });
}

customElements.define('site-donate', SiteDonate);
