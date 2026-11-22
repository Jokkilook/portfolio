// 밝은 모드 / 어두운 모드 전환 (처음 값은 <head>의 스크립트가 정한다)
(function () {
  var root = document.documentElement;
  document.querySelectorAll('.theme-toggle').forEach(function (button) {
    button.addEventListener('click', function () {
      var next = root.dataset.theme === 'light' ? 'dark' : 'light';
      root.dataset.theme = next;
      try {
        localStorage.setItem('theme', next);
      } catch (error) {
        // 저장이 막힌 환경에서는 이번 방문에만 적용된다
      }
    });
  });
})();

// 프로젝트 필터: 전체 / AI 활용 / 직접 구현
// 왼쪽 메뉴와 라이브러리 제목 옆, 두 곳의 버튼이 같은 상태를 공유한다
(function () {
  var buttons = document.querySelectorAll('[data-filter]');
  var cards = document.querySelectorAll('#projects .card');
  var library = document.getElementById('projects');
  if (!buttons.length || !cards.length) return;

  function apply(filter) {
    cards.forEach(function (card) {
      card.hidden = filter !== 'all' && card.dataset.kind !== filter;
    });
    buttons.forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.filter === filter));
    });
  }

  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      apply(button.dataset.filter);
      // 왼쪽 메뉴에서 눌렀으면 걸러진 목록이 보이도록 라이브러리로 이동
      if (button.closest('.rail') && library) library.scrollIntoView();
    });
  });
})();

// 왼쪽 메뉴: 지금 보고 있는 섹션을 표시
(function () {
  var links = document.querySelectorAll('.rail__nav a[href^="#"]');
  if (!links.length || !('IntersectionObserver' in window)) return;

  var byId = {};
  links.forEach(function (link) {
    byId[link.getAttribute('href').slice(1)] = link;
  });

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (link) {
          link.classList.toggle('is-active', link === byId[entry.target.id]);
        });
      });
    },
    // 화면 위쪽 1/3 지점을 지나는 섹션을 현재 섹션으로 본다
    { rootMargin: '-30% 0px -65% 0px' }
  );

  Object.keys(byId).forEach(function (id) {
    var section = document.getElementById(id);
    if (section) observer.observe(section);
  });
})();

// 카드 커서 반응: 커서 지점의 빛 반사와 살짝 기울임
(function () {
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!finePointer) return;

  var tilted = null;
  var MAX_TILT = 3; // 도

  function resetTilt() {
    if (!tilted) return;
    tilted.style.removeProperty('--rx');
    tilted.style.removeProperty('--ry');
    tilted = null;
  }

  document.addEventListener('pointermove', function (event) {
    var card = event.target.closest ? event.target.closest('.card') : null;
    if (card !== tilted) resetTilt();
    if (!card) return;

    var rect = card.getBoundingClientRect();
    var x = event.clientX - rect.left;
    var y = event.clientY - rect.top;
    card.style.setProperty('--gx', x.toFixed(1) + 'px');
    card.style.setProperty('--gy', y.toFixed(1) + 'px');

    if (!reduceMotion) {
      tilted = card;
      card.style.setProperty('--ry', ((x / rect.width - 0.5) * 2 * MAX_TILT).toFixed(2) + 'deg');
      card.style.setProperty('--rx', ((0.5 - y / rect.height) * 2 * MAX_TILT).toFixed(2) + 'deg');
    }
  });

  document.addEventListener('pointerleave', resetTilt);
})();
