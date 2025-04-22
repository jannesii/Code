document.addEventListener('DOMContentLoaded', function() {
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
  