document.addEventListener('DOMContentLoaded', function() {
    // Add click event listener to each sorting button, on click, calls the sortPlaylist function below with the ID
    document.querySelectorAll('.sort-btn').forEach(function(button) {
        button.onclick = function() {
            const playlistId = this.getAttribute('data-playlist-id');
            alert(playlistId)
            sortPlaylist(playlistId);
        };
    });
});

function sortPlaylist(playlistId) {
    // Send an AJAX request to your Flask route
    fetch('/sort_playlist/' + playlistId)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message); // Show a success message
            }
        })
        .catch(error => console.error('Error:', error));
}