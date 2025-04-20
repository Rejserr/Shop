document.addEventListener('DOMContentLoaded', function() {
    const ssccInput = document.getElementById('sscc-input');
    
    if (ssccInput) {
        ssccInput.addEventListener('input', async function(e) {
            if (e.target.value.length >= 18) { // Standard SSCC length
                try {
                    const response = await fetch(`/mobile/api/scan-sscc?sscc=${e.target.value}`);
                    const data = await response.json();
                    handleScanResult(data);
                } catch (error) {
                    showError('Scanning error');
                }
            }
        });
    }
});

function handleScanResult(data) {
    // Handle scan results
}
