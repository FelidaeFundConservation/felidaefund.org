// <site-footer> — the shared footer. Styles live in components.css.
class SiteFooter extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `<footer class="footer" role="contentinfo">
    <div class="container">
      <div class="footer__top">
        <!-- Brand row -->
        <div class="footer__brand-row">
          <div>
            <img loading="lazy" src="assets/logo/logo_felidae_neg-01.png" alt="Felidae Conservation Fund" class="footer__logo-img" />
            <div class="footer__brand-name">Felidae Conservation Fund</div>
            <p class="footer__brand-tagline">Protecting wild cats and their habitats through scientific research, education, and human-wildlife conflict reduction since 2006.</p>
            <div class="footer__social">
              <!-- Facebook -->
              <a href="https://www.facebook.com/felidaefund" target="_blank" rel="noopener" class="footer__social-link" aria-label="Facebook">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg>
              </a>
              <!-- Instagram -->
              <a href="https://www.instagram.com/felidaefund/" target="_blank" rel="noopener" class="footer__social-link" aria-label="Instagram">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="5"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>
              </a>
              <!-- TikTok -->
              <a href="https://www.tiktok.com/@felidaefund" target="_blank" rel="noopener" class="footer__social-link" aria-label="TikTok">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M16 3c.3 2.1 1.6 3.6 3.7 3.8v2.4c-1.3.1-2.5-.3-3.7-1v5.9a5.4 5.4 0 11-5.4-5.4c.3 0 .6 0 .9.1v2.5a2.9 2.9 0 102 2.8V3H16z"/></svg>
              </a>
              <!-- YouTube -->
              <a href="https://www.youtube.com/felidaefund" target="_blank" rel="noopener" class="footer__social-link" aria-label="YouTube">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="2" y="5" width="20" height="14" rx="3"/><polygon points="10,9 16,12 10,15" fill="currentColor" stroke="none"/></svg>
              </a>
              <!-- LinkedIn -->
              <a href="https://www.linkedin.com/company/felidae-conservation-fund/" target="_blank" rel="noopener" class="footer__social-link" aria-label="LinkedIn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="2" y="2" width="20" height="20" rx="3"/><path d="M7 10v7M7 7v.01M11 17v-4a2 2 0 014 0v4M11 10v7"/></svg>
              </a>
              <!-- X (Twitter) -->
              <a href="https://twitter.com/felidaefund" target="_blank" rel="noopener" class="footer__social-link" aria-label="X (Twitter)">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M18.9 3H21l-6.6 7.5L22 21h-6l-4.3-5.6L6.4 21H4.3l7-8L2 3h6.1l3.9 5.2L18.9 3zm-1 16h1.1L8.1 4.2H6.9L17.9 19z"/></svg>
              </a>
            </div>
          </div>
          <div></div>
        </div>

        <!-- Link columns -->
        <nav class="footer__links" aria-label="Footer navigation">
          <div>
            <div class="footer__col-head">Projects</div>
            <a href="project-bhutan.html" class="footer__link">Bhutan Wild Cat Health Project</a>
            <a href="project-patagonia.html" class="footer__link">Patagonia Wild Cats Project</a>
            <a href="project-pumalink.html" class="footer__link">Diablo PumaLink Project</a>
            <a href="project-bobcat.html" class="footer__link">Bay Area Bobcat Project</a>
            <a href="project-tsavo.html" class="footer__link">Tsavo Cheetah Project</a>
            <a href="project-bapp.html" class="footer__link">Bay Area Puma Project</a>
            <a href="project-wildcat-health.html" class="footer__link">Wild Cat Health Project</a>
          </div>
          <div>
            <div class="footer__col-head">Learn</div>
            <a href="mission.html" class="footer__link">Our Mission</a>
            <a href="news.html" class="footer__link">News</a>
            <a href="about.html" class="footer__link">About Us</a>
            <a href="learn-cats.html" class="footer__link">Wild Cat Species</a>
            <a href="learn-ecosystems.html" class="footer__link">Healthy Ecosystems</a>
            <a href="learn-living-alongside.html" class="footer__link">Living Alongside Wild Cats</a>
            <a href="learn-safety.html" class="footer__link">Safety Essentials</a>
          </div>
          <div>
            <div class="footer__col-head">Get Involved</div>
            <a href="volunteer.html" class="footer__link">Volunteer</a>
            <a href="volunteer.html" class="footer__link">Volunteer and Career Opportunities</a>
            <a href="community-science.html" class="footer__link">Community Scientist</a>
            <a href="project-wilde-pod.html" class="footer__link">Wilde Pod (Trail Cam)</a>
            <a href="events.html" class="footer__link">Events</a>
            <a href="ways-to-donate.html" class="footer__link">Ways to Donate</a>
            <a href="take-action.html" class="footer__link">Take Action</a>
          </div>
          <div>
            <div class="footer__col-head">Contact</div>
            <a href="mailto:info@felidaefund.org" class="footer__link">info@felidaefund.org</a>
          </div>
        </nav>
      </div>

      <div class="footer__bottom">
        <p class="footer__copy">© 2026 Felidae Conservation Fund. A 501(c)(3) nonprofit organization. Tax ID: [XX-XXXXXXX]</p>
        <nav class="footer__legal" aria-label="Legal links">
          <a href="#" class="footer__legal-link">Privacy Policy</a>
          <a href="#" class="footer__legal-link">Terms of Use</a>
          <a href="#" class="footer__legal-link">Accessibility</a>
          <a href="#" class="footer__legal-link">Annual Report</a>
        </nav>
      </div>
    </div>
  </footer>`;
  }
}

customElements.define('site-footer', SiteFooter);
