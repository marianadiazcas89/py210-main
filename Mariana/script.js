const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

document.addEventListener('DOMContentLoaded', () => {
  // Text & button entrance (light and quick)
  if (!prefersReduced && window.gsap){
    gsap.from(['.lede', '.amount', '.sub'], {
      y: 14, opacity: 0, duration: 0.6, ease: 'power2.out', stagger: 0.08
    });

    gsap.from('.btn', {
      y: 10, opacity: 0, duration: 0.45, ease: 'power1.out', stagger: 0.08, delay: 0.15
    });

    // Subtle animated gradient: drift the focus point using CSS variables
    // (matches the "gradient-orange" vibe from the CodePen)
    const tl = gsap.timeline({ repeat: -1, yoyo: true, defaults: { duration: 10, ease: 'sine.inOut' }});
    tl.to(document.documentElement, { '--x': '75%', '--y': '25%' })
      .to(document.documentElement, { '--x': '60%', '--y': '70%' })
      .to(document.documentElement, { '--x': '20%', '--y': '60%' });
  }
});
