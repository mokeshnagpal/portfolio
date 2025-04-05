// main.js
document.addEventListener("DOMContentLoaded", function() {
  // Smooth scroll for in-page links if needed.
  const links = document.querySelectorAll('a.nav-link');
  links.forEach(link => {
    link.addEventListener('click', function(e) {
      if (this.hash !== "") {
        e.preventDefault();
        const target = document.querySelector(this.hash);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth' });
        }
      }
    });
  });
});
