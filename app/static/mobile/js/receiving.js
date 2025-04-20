class MobileReceiving {
    constructor() {
        this.barcodeInput = document.getElementById('barcode-input');
        this.quantityInput = document.getElementById('quantity-input');
        this.confirmBtn = document.getElementById('confirm-qty');
        this.scanner = new BarcodeScanner();
        this.currentItem = null;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.addEventListener('barcodescanned', (e) => {
            this.handleBarcodeScan(e.detail.data);
        });

        this.confirmBtn.addEventListener('click', () => {
            this.confirmQuantity();
        });
    }

    async handleBarcodeScan(barcode) {
        try {
            const response = await fetch(`/mobile/api/lookup-item?barcode=${barcode}&sscc=${this.sscc}`);
            const data = await response.json();
            
            if (data.found) {
                this.currentItem = data;
                this.showQuantityInput();
            } else {
                this.showError('Item not found');
            }
        } catch (error) {
            this.showError('Scanning error');
        }
    }

    async confirmQuantity() {
        const quantity = this.quantityInput.value;
        
        try {
            const response = await fetch('/mobile/api/update-quantity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sscc: this.sscc,
                    barcode: this.currentItem.barcode,
                    quantity: quantity
                })
            });
            
            const result = await response.json();
            if (result.success) {
                this.updateUI();
                this.resetScanForm();
            }
        } catch (error) {
            this.showError('Update failed');
        }
    }
}
