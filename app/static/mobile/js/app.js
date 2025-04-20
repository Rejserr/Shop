document.addEventListener('DOMContentLoaded', function() {
    // Auto-focus on scan input if present
    const scanInput = document.getElementById('sscc-input');
    if (scanInput) {
        scanInput.focus();
    }
});
