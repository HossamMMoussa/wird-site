// وِرد — حركة خفيفة فوق محتوى ظاهر أصلًا. لو JavaScript مش شغّال أو الحركة مقلّلة، كل شيء يظهر عادي.
(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const root = document.documentElement;

  // ١) ظهور العناصر أثناء التمرير
  if (!reduce && 'IntersectionObserver' in window) {
    root.classList.add('js');
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            e.target.classList.add('in');
            io.unobserve(e.target);
          }
        }
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.08 },
    );
    document.querySelectorAll('.reveal').forEach((el) => io.observe(el));
    /*
     * أمان: التمرير السريع أو القفز برابط ممكن يعدّي عنصر صغير بين فحصين فما يظهرش. فمع كل تمرير
     * (مرة في الإطار) أي عنصر وصل للشاشة أو عدّاها يظهر فورًا، وأول ما كله يظهر نشيل المستمع.
     */
    let pending = [...document.querySelectorAll('.reveal')];
    let ticking = false;
    const sweep = () => {
      ticking = false;
      const limit = window.innerHeight;
      pending = pending.filter((el) => {
        if (el.getBoundingClientRect().top < limit) {
          el.classList.add('in');
          io.unobserve(el);
          return false;
        }
        return true;
      });
      if (!pending.length) window.removeEventListener('scroll', onScroll);
    };
    const onScroll = () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(sweep);
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    requestAnimationFrame(sweep);
  }

  // ٢) فصل القرآن: الهاتف الثابت يعرض لقطة الخطوة الظاهرة
  const stage = document.querySelector('.scrolly .stage');
  if (stage && 'IntersectionObserver' in window) {
    const shots = [...stage.querySelectorAll('img[data-step]')];
    const show = (id) => shots.forEach((img) => img.classList.toggle('on', img.dataset.step === id));
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) if (e.isIntersecting) show(e.target.dataset.step);
      },
      { rootMargin: '-45% 0px -45% 0px' },
    );
    document.querySelectorAll('.scrolly .step[data-step]').forEach((s) => io.observe(s));
  }

  // ٣) الفصل الحالي في شريط التنقّل
  const links = new Map(
    [...document.querySelectorAll('.chapters a[href^="#"]')].map((a) => [a.getAttribute('href').slice(1), a]),
  );
  if (links.size && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (!e.isIntersecting) continue;
          links.forEach((a) => a.removeAttribute('aria-current'));
          const a = links.get(e.target.id);
          if (a) {
            a.setAttribute('aria-current', 'true');
            a.scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: reduce ? 'auto' : 'smooth' });
          }
        }
      },
      { rootMargin: '-40% 0px -55% 0px' },
    );
    links.forEach((_, id) => {
      const el = document.getElementById(id);
      if (el) io.observe(el);
    });
  }
})();
