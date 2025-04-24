document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
      document.querySelectorAll('.flash').forEach(el => el.remove());
    }, 3000);
    // Vahvistuspoisto
    const delForm = document.getElementById('deleteForm');
    if (delForm) {
      delForm.addEventListener('submit', function(e) {
        if (!confirm('Haluatko varmasti poistaa valitun käyttäjän?')) {
          e.preventDefault();
        }
      });
    }
  });
  