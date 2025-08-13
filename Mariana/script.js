/* === script.js === */

// Speed of the animation
const ANIM = {
  ease: 'power1.out',
  seqTimeScale: 0.6,      // <- make 0.6 your default
  row: { dur: 0.28, stagger: 0.06 },
  infoDur: 0.25,
  btnDur: 0.25,
  bg: { segment: 10, timeScale: 1 }
};


/* Respect reduced motion */
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

document.addEventListener('DOMContentLoaded', () => {
  const providerSelect = document.getElementById('provider');

  // Elements to toggle
  const payBtn        = document.getElementById('payBtn');                 // Pay button in POST form
  const payForm       = document.getElementById('payForm');                // POST form
  const hiddenProv    = payForm ? payForm.querySelector('input[name="provider_id"]') : null;
  const sessionTable  = document.querySelector('.payment-form table');     // First table in the payment form
  const container     = document.querySelector('.payment-form');           // Used for styling state
  const providerInfo  = document.querySelector('.provider-info');          // Info box under table

  // Helpers
  const isSelected = () => providerSelect && providerSelect.value && providerSelect.value.trim() !== '';

  const conceal = (el) => { if (el) el.style.display = 'none'; };

  // Add/remove state class for dropdown styling
  const updateContainerState = () => {
    if (!container) return;
    if (isSelected()) container.classList.add('has-selection');
    else container.classList.remove('has-selection');
  };

  // Subtle sequence: rows -> provider info -> Pay button
  const showAllSequenced = () => {
    if (!sessionTable) return;

    // Ensure they are visible with correct display types
    sessionTable.style.display = 'table';
    if (providerInfo) providerInfo.style.display = 'block';
    if (payBtn) payBtn.style.display = 'inline-flex';

    if (prefersReduced || !window.gsap) return; // skip animation if reduced motion

    const rows = sessionTable.querySelectorAll('tbody tr');

    const tl = gsap.timeline({ defaults: { ease: 'power1.out' } });

    // Prepare: hide rows and below elements
    if (rows.length) tl.set(rows, { autoAlpha: 0, y: 6 });
    if (providerInfo) tl.set(providerInfo, { autoAlpha: 0, y: 8 });
    if (payBtn) tl.set(payBtn, { autoAlpha: 0, y: 8 });

    // Animate rows in a stagger
    if (rows.length) {
      tl.to(rows, {
        autoAlpha: 1,
        y: 0,
        duration: 0.28,
        stagger: 0.06
      });
    }

    // Then provider info
    if (providerInfo) {
      tl.to(providerInfo, {
        autoAlpha: 1,
        y: 0,
        duration: 0.25
      }, '>-0.05'); // slight overlap for smoothness
    }

    // Then Pay button
    if (payBtn) {
      tl.to(payBtn, {
        autoAlpha: 1,
        y: 0,
        duration: 0.25
      }, '>-0.03');
    }
  };

  // Background drift animation (kept from your original)
  if (!prefersReduced && window.gsap) {
    const tlBg = gsap.timeline({ repeat: -1, yoyo: true, defaults: { duration: 10, ease: 'sine.inOut' } });
    tlBg.to(document.documentElement, { '--x': '75%', '--y': '25%' })
        .to(document.documentElement, { '--x': '60%', '--y': '70%' })
        .to(document.documentElement, { '--x': '20%', '--y': '60%' });
  }

  // Initial state on load (server may pre-select a provider)
  if (providerSelect) {
    if (isSelected()) {
      if (hiddenProv) hiddenProv.value = providerSelect.value;
      showAllSequenced();
    } else {
      if (hiddenProv) hiddenProv.value = '';
      conceal(sessionTable);
      conceal(providerInfo);
      conceal(payBtn);
    }
    updateContainerState();

    // On change: toggle UI + sync hidden input + animate sequence
    providerSelect.addEventListener('change', () => {
      if (isSelected()) {
        if (hiddenProv) hiddenProv.value = providerSelect.value;
        showAllSequenced();
      } else {
        if (hiddenProv) hiddenProv.value = '';
        conceal(sessionTable);
        conceal(providerInfo);
        conceal(payBtn);
      }
      updateContainerState();
    });
  }
});
