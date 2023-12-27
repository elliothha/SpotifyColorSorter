document.addEventListener('DOMContentLoaded', function() {
    // Add click event listener to each sorting button, on click, calls the sortPlaylist function below with the ID
    document.querySelectorAll('.sort-btn').forEach(function(button) {
        button.onclick = function() {
            const playlistId = this.getAttribute('data-playlist-id');
            sortPlaylist(playlistId);
        };
    });
});

function showOverlay() {
    document.getElementById('overlay').style.display = 'block';
}

function hideOverlay() {
    document.getElementById('overlay').style.display = 'none';
}

function sortPlaylist(playlistId) {
    showOverlay();

    // Send an AJAX request to your Flask route
    fetch('/sort_playlist/' + playlistId)
        .then(response => response.json())
        .then(data => {
            hideOverlay();
            if (data.status === 'success') {
                alert(data.message); // Show a success message
            } else {
                alert('Sorting failed. Sorry!')
            }
        })
        .catch(error => {
            hideOverlay();
            console.error('Error:', error)
        });
}

