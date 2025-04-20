console.log('Zaprimanje.js loaded');

document.addEventListener('DOMContentLoaded', function() {
    const barcodeInput = document.getElementById('barcode');
    const artiklInput = document.getElementById('artikl');
    const scanForm = document.getElementById('scanForm');
    const sscc = document.querySelector('[data-sscc]')?.dataset.sscc;

    [barcodeInput, artiklInput].forEach(input => {
        if (input) {
            input.addEventListener('input', async function(e) {
                if (e.target.value.length >= 3) {
                    try {
                        const response = await fetch(`/api/lookup-barcode?barcode=${e.target.value}&sscc=${sscc}`);
                        const data = await response.json();
                        
                        if (data.found) {
                            document.getElementById('artikl').value = data.item_code;
                            document.getElementById('naziv').value = data.description;
                            document.getElementById('najavljena').value = data.quantity;
                            document.getElementById('jm').value = data.uom;
                            document.getElementById('zaprimljeno').value = data.received_qty || '0';
                            document.getElementById('kolicina').focus();
                        }
                    } catch (error) {
                        console.error('Lookup error:', error);
                    }
                }
            });
        }
    });

    if (scanForm) {
        scanForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const searchTerm = formData.get('barcode') || formData.get('artikl');
            formData.set('barcode', searchTerm);
            
            try {
                const response = await fetch(`/zaprimanje/scan-items/${sscc}`, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                if (result.success) {
                    window.location.reload();
                } else {
                    alert(result.message || 'Error updating record');
                }
            } catch (error) {
                console.error('Submit error:', error);
                alert('Error updating record');
            }
        });
    }
});
async function completeReceiving() {
    const sscc = document.querySelector('[data-sscc]').dataset.sscc;
    
    try {
        const response = await fetch(`/zaprimanje/complete-receiving/${sscc}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            alert('Receiving completed successfully!');
            window.location.href = '/zaprimanje/scan_sscc'; 
        } else {
            alert('Error completing receiving: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error completing receiving');
    }
}
document.querySelectorAll('.table tbody tr').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', function() {
        const itemCode = this.querySelector('td:first-child').textContent;
        const barcode = this.querySelector('td:nth-child(2)').textContent;
        const description = this.querySelector('td:nth-child(3)').textContent;
        const quantity = this.querySelector('td:nth-child(4)').textContent;
        const receivedQty = this.querySelector('td:nth-child(5)').textContent;
        const uom = this.querySelector('td:nth-child(6)').textContent;
        
        document.getElementById('barcode').value = itemCode;
        document.getElementById('artikl').value = itemCode;
        document.getElementById('naziv').value = description;
        document.getElementById('najavljena').value = quantity;
        document.getElementById('zaprimljeno').value = receivedQty;
        document.getElementById('jm').value = uom;
        document.getElementById('kolicina').focus();
    });
});async function completeReceiving() {
    const sscc = document.querySelector('[data-sscc]').dataset.sscc;
    
    try {
        const response = await fetch(`/zaprimanje/complete-receiving/${sscc}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            alert('Receiving completed successfully!');
            window.location.href = '/zaprimanje/scan-sscc';  // Changed underscore to hyphen
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error completing receiving');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const ssccInput = document.getElementById('sscc');
    
    if (ssccInput) {
        ssccInput.focus();
        ssccInput.addEventListener('input', function(e) {
            if (e.target.value.length >= 5) {
                e.target.form.submit();
            }
        });
    }
});

