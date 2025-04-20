class MobileReceiving {
    constructor() {
        this.barcodeInput = document.getElementById('barcode-input');
        this.quantityInput = document.getElementById('quantity-input');
        this.confirmBtn = document.getElementById('confirm-qty');
        this.currentItem = null;
        this.sscc = document.querySelector('.mobile-receiving').dataset.sscc;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.barcodeInput.addEventListener('input', async (e) => {
            if (e.target.value.length >= 5) {
                await this.lookupItem(e.target.value);
            }
        });

        this.confirmBtn.addEventListener('click', () => this.confirmQuantity());

        // Handle Zebra Scanner
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && document.activeElement === this.barcodeInput) {
                e.preventDefault();
                this.lookupItem(this.barcodeInput.value);
            }
        });
    }

    async lookupItem(barcode) {
        try {
            const response = await fetch(`/mobile/api/lookup-item?barcode=${barcode}&sscc=${this.sscc}`);
            const data = await response.json();
            
            if (data.found) {
                this.showItemDetails(data);
            }
        } catch (error) {
            console.error('Lookup error:', error);
        }
    }

    showItemDetails(item) {
        this.currentItem = item;
        document.getElementById('current-item').style.display = 'block';
        document.getElementById('item-code').textContent = item.item_code;
        document.getElementById('item-description').textContent = item.description;
        document.getElementById('expected-qty').textContent = `${item.quantity} ${item.uom}`;
        document.getElementById('received-qty').textContent = item.received_qty || '0';
        this.quantityInput.focus();
    }

    async confirmQuantity() {
        if (!this.currentItem) return;

        try {
            const response = await fetch('/mobile/api/update-quantity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sscc: this.sscc,
                    barcode: this.currentItem.barcode,
                    quantity: this.quantityInput.value
                })
            });
            
            if (response.ok) {
                this.resetForm();
                this.updateItemCard(this.currentItem.item_code, this.quantityInput.value);
            }
        } catch (error) {
            console.error('Update error:', error);
        }
    }

    resetForm() {
        this.barcodeInput.value = '';
        this.quantityInput.value = '';
        document.getElementById('current-item').style.display = 'none';
        this.barcodeInput.focus();
    }

    updateItemCard(itemCode, newQuantity) {
        const card = document.querySelector(`.item-card[data-item-code="${itemCode}"]`);
        if (card) {
            const statusSpan = card.querySelector('.item-status');
            const [received, total] = statusSpan.textContent.split('/');
            statusSpan.textContent = `${newQuantity}/${total}`;
            
            if (parseFloat(newQuantity) >= parseFloat(total)) {
                card.classList.add('completed');
            }
        }
    }
    
}

function completeReceiving() {
    const sscc = document.querySelector('.mobile-container').dataset.sscc;
    fetch(`/zaprimanje/complete-receiving/${sscc}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/mobile/menu';
        } else {
            alert('Error completing receiving: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error completing receiving');
    });
}


document.addEventListener('DOMContentLoaded', () => {
    new MobileReceiving();
});
