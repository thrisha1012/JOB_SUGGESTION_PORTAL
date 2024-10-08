document.getElementById('searchForm').addEventListener('submit', function(event) {
  event.preventDefault();
  const formData = new FormData(this);
  fetch('/search', {
    method: 'POST',
    body: formData
  })
  .then(response => response.text())
  .then(data => {
    document.getElementById('searchResults').innerHTML = data;
  })
  .catch(error => {
    console.error('Error:', error);
  });
});

