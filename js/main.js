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
(function () {
  var buttons = document.querySelectorAll('.filter__btn');
  var cards = document.querySelectorAll('#projects .card');
  if (!buttons.length) return;

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
    });
  });
})();

// 커서 반응: 배경 빛이 커서를 따라오고, 유리 카드에 빛 반사와 기울임이 생긴다
(function () {
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!finePointer) return;

  var aurora = document.querySelector('.aurora');
  var target = { x: window.innerWidth * 0.7, y: window.innerHeight * 0.2 };
  var current = { x: target.x, y: target.y };
  var running = false;
  var tilted = null;
  var MAX_TILT = 3; // 도
  var DRIFT = 0.18; // 커서 이동량 중 배경 빛이 따라가는 비율
  var EASE = 0.04; // 한 프레임에 목표까지 좁히는 비율 (작을수록 느긋함)

  // 배경 빛은 제자리(화면 오른쪽 위)에서 커서 쪽으로 조금만, 천천히 끌려간다
  function follow() {
    current.x += (target.x - current.x) * EASE;
    current.y += (target.y - current.y) * EASE;
    aurora.style.setProperty('--mx', current.x.toFixed(1) + 'px');
    aurora.style.setProperty('--my', current.y.toFixed(1) + 'px');
    if (Math.abs(target.x - current.x) + Math.abs(target.y - current.y) > 0.5) {
      requestAnimationFrame(follow);
    } else {
      running = false;
    }
  }

  function resetTilt() {
    if (!tilted) return;
    tilted.style.removeProperty('--rx');
    tilted.style.removeProperty('--ry');
    tilted = null;
  }

  document.addEventListener('pointermove', function (event) {
    if (aurora) {
      target.x = window.innerWidth * 0.7 + (event.clientX - window.innerWidth / 2) * DRIFT;
      target.y = window.innerHeight * 0.2 + (event.clientY - window.innerHeight / 2) * DRIFT;
      if (reduceMotion) {
        current.x = target.x;
        current.y = target.y;
      }
      if (!running) {
        running = true;
        requestAnimationFrame(follow);
      }
    }

    var glass = event.target.closest ? event.target.closest('.glass') : null;
    if (!glass) {
      resetTilt();
      return;
    }
    var rect = glass.getBoundingClientRect();
    var x = event.clientX - rect.left;
    var y = event.clientY - rect.top;
    glass.style.setProperty('--gx', x.toFixed(1) + 'px');
    glass.style.setProperty('--gy', y.toFixed(1) + 'px');

    if (glass !== tilted) resetTilt();
    if (!reduceMotion && glass.classList.contains('card')) {
      tilted = glass;
      glass.style.setProperty('--ry', ((x / rect.width - 0.5) * 2 * MAX_TILT).toFixed(2) + 'deg');
      glass.style.setProperty('--rx', ((0.5 - y / rect.height) * 2 * MAX_TILT).toFixed(2) + 'deg');
    }
  });

  document.addEventListener('pointerleave', resetTilt);
})();
