document.addEventListener("DOMContentLoaded", function() {
  // Smooth scroll for nav links
  document.querySelectorAll('a.nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
      if (this.hash) {
        e.preventDefault();
        document.querySelector(this.hash)
                .scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Refresh AOS (if content changes)
  if (window.AOS) AOS.refresh();
});
