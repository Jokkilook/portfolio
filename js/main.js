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

// 프로젝트 줄의 빛 반사: 커서가 있는 지점이 밝아진다
(function () {
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;

  document.addEventListener('pointermove', function (event) {
    var row = event.target.closest ? event.target.closest('.row') : null;
    if (!row) return;
    var rect = row.getBoundingClientRect();
    row.style.setProperty('--gx', (event.clientX - rect.left).toFixed(1) + 'px');
    row.style.setProperty('--gy', (event.clientY - rect.top).toFixed(1) + 'px');
  });
})();
