// static/script.js — WanderAI Frontend Logic

// ─────────────────────────────────────────────
// 1. INTEREST CHIP SELECTION
// ─────────────────────────────────────────────
const chips = document.querySelectorAll('.chip');
const interestsInput = document.getElementById('interests-input');

if (chips.length) {
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('selected');
      // Collect all selected values
      const selected = [...document.querySelectorAll('.chip.selected')]
        .map(c => c.dataset.value);
      interestsInput.value = selected.join(',');
    });
  });
}

// ─────────────────────────────────────────────
// 2. FORM VALIDATION
// ─────────────────────────────────────────────
const form = document.getElementById('travel-form');

if (form) {
  form.addEventListener('submit', e => {
    let valid = true;

    // Validate interests chips
    const selectedChips = document.querySelectorAll('.chip.selected');
    const interestsErr = document.getElementById('interests-error');
    if (selectedChips.length === 0) {
      interestsErr.classList.add('visible');
      valid = false;
    } else {
      interestsErr.classList.remove('visible');
    }

    // Validate required selects
    const selects = [
      { id: 'duration',   errId: 'duration-error' },
      { id: 'budget',     errId: 'budget-error' },
      { id: 'season',     errId: 'season-error' },
      { id: 'group_type', errId: 'group-error' },
    ];
    selects.forEach(({ id, errId }) => {
      const el  = document.getElementById(id);
      const err = document.getElementById(errId);
      if (el && err) {
        if (!el.value) { err.classList.add('visible'); valid = false; }
        else            { err.classList.remove('visible'); }
      }
    });

    if (!valid) { e.preventDefault(); return; }

    // Show loading state on button
    const btn     = document.getElementById('submit-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoad = btn.querySelector('.btn-loader');
    if (btn) {
      btnText.style.display = 'none';
      btnLoad.style.display = 'inline';
      btn.disabled = true;
    }
  });
}

// ─────────────────────────────────────────────
// 3. SCROLL-TRIGGERED ANIMATIONS (Intersection Observer)
// ─────────────────────────────────────────────
const animTargets = document.querySelectorAll('.step-card, .card, .form-container');

if ('IntersectionObserver' in window) {
  const obs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  animTargets.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(28px)';
    el.style.transition = 'opacity .6s ease, transform .6s ease';
    obs.observe(el);
  });
}

// ─────────────────────────────────────────────
// 4. SIMILARITY BAR ANIMATION ON RESULT PAGE
// ─────────────────────────────────────────────
// Bars start at 0 width via CSS; we just let the CSS transition handle it,
// but we trigger it after a tiny delay to make the animation play visibly.
window.addEventListener('load', () => {
  const bars = document.querySelectorAll('.sim-bar-fill');
  bars.forEach((bar, i) => {
    const target = bar.style.width;   // already set inline by Jinja
    bar.style.width = '0%';
    setTimeout(() => { bar.style.width = target; }, 300 + i * 80);
  });
});

// ─────────────────────────────────────────────
// 5. SMOOTH SCROLL FOR NAV LINKS
// ─────────────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});