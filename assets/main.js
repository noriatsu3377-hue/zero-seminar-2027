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
})();
