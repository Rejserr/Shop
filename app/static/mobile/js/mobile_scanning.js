class MobileScanner {
    constructor() {
        this.form = document.getElementById('scanForm');
        this.modal = document.getElementById('itemSelectorModal');
        this.itemList = document.getElementById('itemList');
        this.initializeScanner();
    }

    initializeScanner() {
        const barcodeInput = document.getElementById('barcode');
        if (barcodeInput) {
            barcodeInput.addEventListener('input', async (e) => {
                if (e.target.value.length >= 3) {
                    await this.handleLookup(e.target.value);
                }
            });
        }

        document.querySelectorAll('.item-card').forEach(card => {
            card.addEventListener('click', () => {
                const itemCode = card.dataset.itemCode;
                this.handleLookup(itemCode);
            });
        });

        if (this.form) {
            this.form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.submitForm();
            });
        }
    }

    async handleLookup(searchTerm) {
        const sscc = document.querySelector('.mobile-container').dataset.sscc;
        try {
            const response = await fetch(`/mobile/api/lookup-barcode?barcode=${searchTerm}&sscc=${sscc}`);
            const data = await response.json();
            
            if (data.found) {
                if (data.items.length > 1) {
                    this.showItemSelector(data.items);
                } else {
                    this.fillItemDetails(data.items[0]);
                }
            }
        } catch (error) {
            console.error('Lookup error:', error);
        }
    }

    showItemSelector(items) {
        const modal = document.createElement('div');
        modal.className = 'item-selector-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3> Izaberi stavku </h3>
                    <span class="close-modal">×</span>
                </div>
                <div class="item-list">
                    ${items.map(item => `
                        <div class="selector-item" data-item='${JSON.stringify(item)}'>
                            <div class="item-header">
                                <span class="item-code">${item.item_code}</span>
                                <span class="quantity">Najavljeno: ${item.quantity} ${item.uom}</span>
                            </div>
                            <div class="item-details">
                                <span>SSCC: ${item.sscc}</span>
                                <span class="received-qty">Zaprimljeno: ${item.received_qty} ${item.uom}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.remove();
        });

        modal.querySelectorAll('.selector-item').forEach(item => {
            item.addEventListener('click', () => {
                const itemData = JSON.parse(item.dataset.item);
                this.fillItemDetails(itemData);
                modal.remove();
            });
        });
    }
    fillItemDetails(item) {
        // Update form fields
        document.getElementById('selected_item_id').value = item.id;
        document.getElementById('artikl').value = item.item_code;
        document.getElementById('naziv').value = item.description;
        document.getElementById('najavljena').value = item.quantity;
        document.getElementById('jm').value = item.uom;
        document.getElementById('zaprimljeno').value = item.received_qty || '0';
        document.getElementById('kolicina').focus();

        // Update scanned item display
        document.getElementById('scanned-item-container').style.display = 'block';
        document.getElementById('scanned-item-code').textContent = item.item_code;
        document.getElementById('scanned-item-desc').textContent = item.description;
        document.getElementById('scanned-item-qty').textContent = `${item.quantity} ${item.uom}`;
        document.getElementById('scanned-item-sscc').textContent = `SSCC: ${item.sscc}`;
        document.getElementById('scanned-item-received').textContent = `Zaprimljeno: ${item.received_qty || 0} ${item.uom}`;
    }

    async submitForm() {
        const formData = new FormData(this.form);
        const sscc = document.querySelector('.mobile-container').dataset.sscc;
        
        try {
            const response = await fetch(`/mobile/scan-items/${sscc}`, {
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
    }
}

// Initialize scanner
document.addEventListener('DOMContentLoaded', () => {
    new MobileScanner();
});

async function completeReceiving() {
    const sscc = document.querySelector('.mobile-container').dataset.sscc;
    try {
        console.log('Starting complete receiving for SSCC:', sscc);
        const response = await fetch(`/mobile/complete-receiving/${sscc}`, {
            method: 'POST'
        });
        const data = await response.json();
        console.log('Received response:', data);
        
        if (data.success) {
            alert('Receiving completed successfully!');
            window.location.href = '/mobile/scan-sscc';
        } else {
            alert('Error completing receiving: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error completing receiving');
    }
}