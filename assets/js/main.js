/* =========================================================
   Maison Mirenza — V2 runtime (vanilla JS)
   Public pages stay light. Confidential R&D data is filtered
   at build time and never reaches the DOM.
   ========================================================= */
(function () {
  'use strict';
  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Analytics hooks (semantic, privacy-safe) ---------- */
  function track(event, detail) {
    (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: event }, detail || {}));
  }
  window.mmTrack = track;

  /* ---------- Lazy video: hydrate near viewport, pause offscreen ---------- */
  var lazyVideos = document.querySelectorAll('video[data-lazy-video]');
  function hydrateVideo(video) {
    if (video.dataset.hydrated === 'true') return;
    video.querySelectorAll('source[data-src]').forEach(function (s) {
      s.src = s.dataset.src; s.removeAttribute('data-src');
    });
    video.load();
    video.dataset.hydrated = 'true';
  }
  if (!reducedMotion && 'IntersectionObserver' in window && lazyVideos.length) {
    var vObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) { hydrateVideo(v); if (v.muted) v.play().catch(function () {}); }
        else { v.pause(); }
      });
    }, { rootMargin: '240px 0px', threshold: 0.15 });
    lazyVideos.forEach(function (v) { vObs.observe(v); });
  } else {
    lazyVideos.forEach(function (v) { v.pause(); v.removeAttribute('autoplay'); });
  }

  /* ---------- Mobile fullscreen menu ---------- */
  var toggle = document.querySelector('[data-menu-toggle]');
  var menu = document.querySelector('[data-mobile-menu]');
  var closeBtn = document.querySelector('[data-menu-close]');
  function openMenu() {
    if (!menu) return;
    menu.classList.add('is-open');
    document.body.classList.add('menu-open');
    if (toggle) toggle.setAttribute('aria-expanded', 'true');
    var first = menu.querySelector('a, button'); if (first) first.focus();
  }
  function closeMenu() {
    if (!menu) return;
    menu.classList.remove('is-open');
    document.body.classList.remove('menu-open');
    if (toggle) { toggle.setAttribute('aria-expanded', 'false'); toggle.focus(); }
  }
  if (toggle) toggle.addEventListener('click', openMenu);
  if (closeBtn) closeBtn.addEventListener('click', closeMenu);
  if (menu) menu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', closeMenu); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && menu && menu.classList.contains('is-open')) closeMenu();
  });

  /* ---------- Accordions ---------- */
  document.querySelectorAll('[data-accordion] > [data-accordion-trigger]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var panel = btn.nextElementSibling;
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!open));
      if (panel) panel.hidden = open;
    });
  });

  /* ---------- Journal filtering ---------- */
  var filters = document.querySelectorAll('[data-filter]');
  var cards = document.querySelectorAll('[data-journal-card]');
  if (filters.length && cards.length) {
    filters.forEach(function (f) {
      f.addEventListener('click', function () {
        var cat = f.dataset.filter;
        filters.forEach(function (x) { x.classList.toggle('active', x === f); });
        cards.forEach(function (c) {
          var show = cat === 'all' || c.dataset.category === cat;
          c.style.display = show ? '' : 'none';
        });
        track('journal_filter', { category: cat });
      });
    });
  }

  /* ---------- Product selector: Trouver ma protection ---------- */
  var root = document.querySelector('[data-selector-root]');
  if (root && window.__MM_SELECTOR__) {
    initSelector(root, window.__MM_SELECTOR__);
  }

  function initSelector(root, cfg) {
    var steps = cfg.steps, logic = cfg.logic, answers = {}, current = 0;
    var stepsWrap = root.querySelector('[data-selector-steps]');
    var progress = root.querySelector('[data-selector-progress]');
    var resultWrap = root.querySelector('[data-selector-result]');

    // progress bars
    steps.forEach(function () { var s = document.createElement('span'); progress.appendChild(s); });

    steps.forEach(function (step, i) {
      var el = document.createElement('div');
      el.className = 'selector-step' + (i === 0 ? ' active' : '');
      el.dataset.step = step.id;
      var cols = step.options.length >= 4 ? ' cols-4' : '';
      el.innerHTML =
        '<span class="eyebrow">Question ' + (i + 1) + ' / ' + steps.length + '</span>' +
        '<h2>' + step.question + '</h2>' +
        (step.help ? '<p class="selector-help">' + step.help + '</p>' : '') +
        '<div class="option-grid' + cols + '" role="group" aria-label="' + step.question + '"></div>' +
        '<div class="selector-actions">' +
          '<button class="cta-plain" data-back' + (i === 0 ? ' hidden' : '') + '>Retour</button>' +
          '<span class="muted" data-hint>Sélectionnez pour continuer</span>' +
        '</div>';
      var grid = el.querySelector('.option-grid');
      step.options.forEach(function (opt) {
        var b = document.createElement('button');
        b.className = 'option';
        b.type = 'button';
        b.innerHTML = '<span class="opt-label">' + opt.label + '</span>' +
          (opt.note ? '<span class="opt-note">' + opt.note + '</span>' : '');
        b.addEventListener('click', function () {
          grid.querySelectorAll('.option').forEach(function (o) { o.classList.remove('selected'); });
          b.classList.add('selected');
          answers[step.id] = opt.value;
          if (i === 0) track('selector_start', {});
          setTimeout(function () { goTo(i + 1); }, 220);
        });
        grid.appendChild(b);
      });
      el.querySelector('[data-back]').addEventListener('click', function () { goTo(i - 1); });
      stepsWrap.appendChild(el);
    });

    function updateProgress() {
      progress.querySelectorAll('span').forEach(function (s, idx) {
        s.className = idx < current ? 'done' : (idx === current ? 'active' : '');
      });
    }
    function goTo(i) {
      if (i >= steps.length) { showResult(); return; }
      if (i < 0) i = 0;
      current = i;
      stepsWrap.querySelectorAll('.selector-step').forEach(function (s, idx) {
        s.classList.toggle('active', idx === i);
      });
      updateProgress();
      resultWrap.hidden = true;
      stepsWrap.hidden = false;
      root.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' });
    }
    updateProgress();

    function computeLevel() {
      var base = logic.level_from_flow[answers.flow] || 'regular';
      var order = logic.level_order;
      var idx = order.indexOf(base);
      var bump = (logic.night_upgrade[answers.moment] || 0);
      idx = Math.max(0, Math.min(order.length - 1, idx + bump));
      return order[idx];
    }
    function altLevel(level) {
      var order = logic.level_order, i = order.indexOf(level);
      return i < order.length - 1 ? order[i + 1] : order[Math.max(0, i - 1)];
    }
    function cutLabel() {
      if (answers.cut === 'hipster') return 'Hipster';
      if (answers.cut === 'classic-brief') return 'Classic Brief';
      return 'Classic Brief';
    }
    function cutSlug() {
      if (answers.cut === 'hipster') return 'hipster';
      return 'classic-brief';
    }

    function showResult() {
      var level = computeLevel();
      var alt = altLevel(level);
      var sizes = (cfg.size_map[answers.size] || []).join(' · ');
      var label = logic.level_labels[level];
      var descriptor = logic.level_descriptor[level];
      var reason = cfg.reasons[level];
      var productHref = root.dataset.productBase + cutSlug() + '/';

      resultWrap.innerHTML =
        '<div class="result-head">' +
          '<span class="eyebrow">Notre recommandation</span>' +
          '<h2>' + cutLabel() + ' — ' + label + '</h2>' +
          '<p>' + descriptor + '</p>' +
        '</div>' +
        '<div class="result-body">' +
          '<p>' + reason + '</p>' +
          '<dl class="result-spec">' +
            '<div><dt>Coupe</dt><dd>' + cutLabel() + '</dd></div>' +
            '<div><dt>Niveau</dt><dd>' + label + ' · ' + descriptor + '</dd></div>' +
            '<div><dt>Tailles conseillées</dt><dd>' + (sizes || 'Toutes tailles') + '</dd></div>' +
            '<div><dt>Alternative</dt><dd>' + logic.level_labels[alt] + ' selon les jours</dd></div>' +
          '</dl>' +
          '<p class="result-alt">Les capacités chiffrées seront publiées après validation. En attendant, le choix se fait par niveau et par usage.</p>' +
          '<div class="cta-row">' +
            '<a class="btn btn--primary" href="' + productHref + '">Voir le ' + cutLabel() + '</a>' +
            '<a class="cta" href="' + (root.dataset.pharmacyHref || '/pharmacie/') + '">Trouver en pharmacie</a>' +
            '<button class="cta-plain" data-restart>Recommencer</button>' +
          '</div>' +
        '</div>';

      stepsWrap.hidden = true;
      resultWrap.hidden = false;
      progress.querySelectorAll('span').forEach(function (s) { s.className = 'done'; });
      resultWrap.querySelector('[data-restart]').addEventListener('click', function () {
        answers = {}; current = 0;
        stepsWrap.querySelectorAll('.option.selected').forEach(function (o) { o.classList.remove('selected'); });
        goTo(0);
      });
      track('selector_complete', { level: level, cut: cutSlug() });
      resultWrap.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' });
    }
  }

  /* ---------- Scroll reveal (subtle, opt-in via data-reveal) ---------- */
  if (!reducedMotion && 'IntersectionObserver' in window) {
    var reveals = document.querySelectorAll('[data-reveal]');
    if (reveals.length) {
      var rObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add('is-visible'); rObs.unobserve(e.target); }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
      reveals.forEach(function (el) { rObs.observe(el); });
    }
  } else {
    document.querySelectorAll('[data-reveal]').forEach(function (el) { el.classList.add('is-visible'); });
  }
})();
