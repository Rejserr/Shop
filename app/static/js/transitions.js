document.addEventListener('DOMContentLoaded', () => {
    // Add page transition class to body
    document.body.classList.add('page-transition');

    // Handle loading states
    const showLoading = () => {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(overlay);
    };

    const hideLoading = () => {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => overlay.remove(), 300);
        }
    };

    // Add loading state to all links
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (e) => {
            if (!link.hasAttribute('data-no-loading')) {
                showLoading();
            }
        });
    });

    // Add loading state to all forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            showLoading();
        });
    });

    // Hide loading on page load
    window.addEventListener('load', hideLoading);

    const toggleBtn = document.querySelector('.toggle-sidebar');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            const sidebar = document.getElementById('sidebar');
            const content = document.getElementById('content');
            const icon = this.querySelector('i');
            
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('sidebar-collapsed');
            icon.classList.toggle('fa-chevron-left');
            icon.classList.toggle('fa-chevron-right');
        });
    }
});
