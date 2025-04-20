class BarcodeScanner {
    constructor() {
        this.registerDataWedgeIntent();
    }

    registerDataWedgeIntent() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const activeElement = document.activeElement;
                if (activeElement && activeElement.classList.contains('scan-input')) {
                    this.handleScan(activeElement.value);
                }
            }
        });

        // Zebra DataWedge Intent
        document.addEventListener('datawedge', (e) => {
            this.handleScan(e.data);
        });
    }

    handleScan(scannedData) {
        const event = new CustomEvent('barcodescanned', {
            detail: { data: scannedData }
        });
        document.dispatchEvent(event);
    }
}
