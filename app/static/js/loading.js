// Simple loading overlay functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get the form and overlay elements
    const searchForm = document.getElementById('search-form');
    const loadingOverlay = document.getElementById('loading-overlay');
    const searchBtn = document.getElementById('search-btn');
    
    // Function to show the loading overlay
    window.showLoading = function() {
        if (loadingOverlay) {
            loadingOverlay.style.display = 'block';
            console.log('Loading overlay shown');
        } else {
            console.error('Loading overlay element not found');
        }
    };
    
    // Add event listener to the form
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            showLoading();
            console.log('Form submitted, showing overlay');
        });
    }
    
    // Add event listener to the button
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            showLoading();
            console.log('Search button clicked, showing overlay');
        });
    }
    
    // Hide loading overlay when page is fully loaded
    window.addEventListener('load', function() {
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
            console.log('Page loaded, hiding overlay');
        }
    });
    
    // Fallback to hide the overlay after a timeout
    setTimeout(function() {
        if (loadingOverlay && loadingOverlay.style.display === 'block') {
            loadingOverlay.style.display = 'none';
            console.log('Timeout reached, hiding overlay');
        }
    }, 5000);
});