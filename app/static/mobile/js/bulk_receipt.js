class BulkReceiptHandler {
    constructor() {
        this.barcodeInput = document.getElementById('barcode-input');
        this.quantityInput = document.getElementById('quantity-input');
        this.confirmBtn = document.getElementById('confirm-qty');
        this.quantitySection = document.querySelector('.quantity-section');
        this.currentDeliveryNote = document.querySelector('[name="delivery_note"]').value;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.barcodeInput.addEventListener('input', async (e) => {
            if (e.target.value.length >= 5) {
                await this.handleBarcodeScan(e.target.value);
                e.target.value = '';
            }
        });

        this.confirmBtn.addEventListener('click', () => {
            this.confirmQuantity();
        });
    }

    async handleBarcodeScan(barcode) {
        try {
            const response = await fetch(`/mobile/api/bulk-lookup-item?barcode=${barcode}&delivery_note=${this.currentDeliveryNote}`);
            const data = await response.json();
            
            if (data.found) {
                this.highlightItem(data.item_code);
                this.showQuantityInput();
            }
        } catch (error) {
            console.error('Scanning error:', error);
        }
    }

    highlightItem(itemCode) {
        document.querySelectorAll('.item-card').forEach(card => {
            card.classList.remove('highlighted');
        });
        
        const itemCard = document.querySelector(`[data-item-code="${itemCode}"]`);
        if (itemCard) {
            itemCard.classList.add('highlighted');
            itemCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    showQuantityInput() {
        this.quantitySection.style.display = 'block';
        this.quantityInput.focus();
    }

    async confirmQuantity() {
        const quantity = this.quantityInput.value;
        
        try {
            const response = await fetch('/mobile/api/bulk-update-quantity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    delivery_note: this.currentDeliveryNote,
                    barcode: this.barcodeInput.value,
                    quantity: quantity
                })
            });
            
            if (response.ok) {
                location.reload();
            }
        } catch (error) {
            console.error('Update error:', error);
        }
    }
}
console.log('Bulk receipt script starting');

document.addEventListener('DOMContentLoaded', function() {
    const barcodeInput = document.getElementById('barcode');
    const artiklInput = document.getElementById('artikl');
    const scanForm = document.getElementById('scanForm');
    const deliveryNote = document.querySelector('[name="delivery_note"]')?.value;

    function handleLookup(searchTerm) {
        fetch(`/mobile/api/bulk-lookup-item?barcode=${searchTerm}&delivery_note=${deliveryNote}`)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.found) {
                    if (data.multiple) {
                        showItemSelector(data.items);
                    } else {
                        document.getElementById('item_id').value = data.items[0].id;
                        fillItemDetails(data.items[0]);
                    }
                }
            });
    }

    function showItemSelector(items) {
        const modal = document.createElement('div');
        modal.className = 'item-selector-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Izaberi stavku</h3>
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
                                <span>MSI: ${item.document_msi}</span>
                                <span>Nalog: ${item.sales_order}</span>
                                <span>Kupac: ${item.customer}</span>
                                <span class="received-qty">Zaprimljeno: ${item.received_qty} ${item.uom}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Add close button functionality
        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.remove();
        });

        modal.querySelectorAll('.selector-item').forEach(item => {
            item.addEventListener('click', function() {
                const itemData = JSON.parse(this.dataset.item);
                fillItemDetails(itemData);
                modal.remove();
            });
        });
    }

    function fillItemDetails(item) {
        if (!item) return;
        
        document.getElementById('item_id').value = item.id;
        document.getElementById('artikl').value = item.item_code;
        document.getElementById('naziv').value = item.description;
        document.getElementById('najavljena').value = item.quantity;
        document.getElementById('jm').value = item.uom;
        document.getElementById('zaprimljeno').value = item.received_qty || '0';
        document.getElementById('kolicina').focus();

        const scannedItemHtml = `
            <div class="item-card scanned">
                <div class="item-row">
                    <span class="item-code">${item.item_code}</span>
                </div>
                <div class="item-row quantity-row">
                    <span class="expected">Najavljeno: ${item.quantity}</span>
                    <span class="received">Zaprimljeno: ${item.received_qty || 0} ${item.uom}</span>
                </div>
                <div class="item-row">
                    <div class="item-description">${item.description}</div>
                    <div class="item-details">
                        <span class="receiver">Kupac: ${item.customer}</span>
                        <span class="document-msi">MSI: ${item.document_msi}</span>
                         ${item.order_type === 'WEB' ? `<span class="document-msi" style="background-color: #e6f3ff">Vrsta naloga:<strong> ${item.order_type}</strong></span>` : ''}
                    </div>
                </div>
            </div>
        `;
        document.getElementById('scanned-item').innerHTML = scannedItemHtml;
    }

    // Event listeners
    [barcodeInput, artiklInput].forEach(input => {
        if (input) {
            input.addEventListener('input', (e) => {
                if (e.target.value.length >= 3) {
                    handleLookup(e.target.value);
                }
            });
        }
    });

    // Item card clicks
    document.querySelectorAll('.item-card').forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            const itemCode = this.querySelector('.item-code').textContent.trim();
            barcodeInput.value = itemCode;
            handleLookup(itemCode);
        });
    });

    // Form submission
    if (scanForm) {
        scanForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const currentDeliveryNote = document.querySelector('[name="delivery_note"]').value;
            
            try {
                const response = await fetch('/mobile/bulk-receipt', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                if (result.success) {
                    // Clear form fields but maintain delivery note
                    document.getElementById('barcode').value = '';
                    document.getElementById('artikl').value = '';
                    document.getElementById('naziv').value = '';
                    document.getElementById('najavljena').value = '';
                    document.getElementById('jm').value = '';
                    document.getElementById('zaprimljeno').value = '';
                    document.getElementById('kolicina').value = '';
                    document.getElementById('scanned-item').innerHTML = '';
                    
                    // Reload with delivery note preserved
                    window.location.href = `/mobile/bulk-receipt?delivery_note=${currentDeliveryNote}`;
                }
            } catch (error) {
                console.error('Submit error:', error);
            }
        });
    }
});
