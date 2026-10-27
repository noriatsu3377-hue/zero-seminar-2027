// 演出のみ。JavaScriptが無効でも本文・日程・リンクはすべて使える。
(function () {
  var root = document.documentElement;
  root.classList.remove('no-js');
  root.classList.add('js');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var targets = document.querySelectorAll('.fade, .mk');
  if (reduce || !('IntersectionObserver' in window)) {
    targets.forEach(function (el) { el.classList.add('on'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('on'); io.unobserve(e.target); }
      });
    }, { threshold: 0 });
    targets.forEach(function (el) { io.observe(el); });
  }

  var hero = document.querySelector('.hero');
  var btn = document.querySelector('.motion-toggle');
  if (hero && btn) {
    btn.addEventListener('click', function () {
      var paused = hero.classList.toggle('paused');
      btn.textContent = paused ? '背景の動きを再生' : '背景の動きを停止';
      btn.setAttribute('aria-pressed', paused ? 'true' : 'false');
    });
  }

  var menu = document.querySelector('.mobile-menu');
  if (menu) {
    menu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () { menu.open = false; });
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && menu.open) {
        menu.open = false;
        menu.querySelector('summary').focus();
      }
    });
  }

  // セミナー一覧の絞り込み（JavaScript無効時はフォームを出さず全件表示）
  var form = document.querySelector('.filter');
  if (form) {
    var cards = Array.prototype.slice.call(document.querySelectorAll('#seminars .card'));
    var month = form.querySelector('#f-month');
    var topics = Array.prototype.slice.call(form.querySelectorAll('.topic'));
    var count = form.querySelector('.count');
    var empty = document.querySelector('#seminars .empty');
    var apply = function () {
      var m = month.value;
      var on = topics.filter(function (b) { return b.getAttribute('aria-pressed') === 'true'; }).map(function (b) { return b.dataset.topic; });
      var shown = 0;
      cards.forEach(function (c) {
        var ts = (c.dataset.topics || '').split('|');
        var ok = (!m || c.dataset.month === m) && (!on.length || on.some(function (t) { return ts.indexOf(t) !== -1; }));
        c.hidden = !ok;
        if (ok) { shown++; c.classList.add('on'); }
      });
      count.textContent = (m || on.length) ? shown + '件 / 全' + cards.length + '講座を表示中' : '全' + cards.length + '講座を表示中';
      empty.hidden = shown !== 0;
    };
    month.addEventListener('change', apply);
    topics.forEach(function (b) {
      b.addEventListener('click', function () {
        b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
        apply();
      });
    });
    form.querySelector('.reset').addEventListener('click', function () {
      month.value = '';
      topics.forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
      apply();
    });
    form.addEventListener('submit', function (e) { e.preventDefault(); });
    form.hidden = false;
  }
})();
