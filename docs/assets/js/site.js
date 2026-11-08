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

  // ٢) الفصول ذات الهاتف الثابت: يعرض لقطة الخطوة الظاهرة
  if ('IntersectionObserver' in window) {
    document.querySelectorAll('.scrolly').forEach((box) => {
      const shots = [...box.querySelectorAll('.stage img[data-step]')];
      const show = (id) => shots.forEach((img) => img.classList.toggle('on', img.dataset.step === id));
      const io = new IntersectionObserver(
        (entries) => {
          for (const e of entries) if (e.isIntersecting) show(e.target.dataset.step);
        },
        { rootMargin: '-45% 0px -45% 0px' },
      );
      box.querySelectorAll('.step[data-step]').forEach((s) => io.observe(s));
    });
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
            // نحرّك شريط الفصول وحده أفقيًا (scrollIntoView ممكن يحرّك الصفحة كلها)
            const bar = a.parentElement;
            const br = bar.getBoundingClientRect();
            const ar = a.getBoundingClientRect();
            if (ar.left < br.left || ar.right > br.right) {
              const delta = ar.left + ar.width / 2 - (br.left + br.width / 2);
              bar.scrollBy({ left: delta, behavior: reduce ? 'auto' : 'smooth' });
            }
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

  // ٤) تكبير اللقطة عند الضغط عليها، بالنسخة الأكبر (1080 بكسل). يعمل بلوحة المفاتيح، ويُغلق بـ Esc
  const box = document.querySelector('.lightbox');
  if (box && typeof box.showModal === 'function') {
    const big = box.querySelector('img');
    const cap = box.querySelector('.lb-caption');
    let opener = null;
    const open = (img) => {
      opener = img;
      const hi = (img.getAttribute('srcset') || '').split(',').map((s) => s.trim().split(' ')[0]).pop() || img.src;
      big.src = hi;
      big.alt = img.alt;
      cap.textContent = img.alt;
      box.classList.toggle('wide', !!img.closest('.zoom'));
      box.showModal();
    };
    document.querySelectorAll('.phone img, .zoom img, .feature .thumb img').forEach((img) => {
      if (!img.alt || img.closest('[aria-hidden="true"]')) return;
      img.classList.add('zoomable');
      img.tabIndex = 0;
      img.setAttribute('role', 'button');
      img.setAttribute('aria-label', `تكبير: ${img.alt}`);
      img.addEventListener('click', () => open(img));
      img.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          open(img);
        }
      });
    });
    box.querySelector('.lb-close').addEventListener('click', () => box.close());
    box.addEventListener('click', (e) => {
      if (e.target === box) box.close();
    });
    box.addEventListener('close', () => opener && opener.focus());
  }
})();
