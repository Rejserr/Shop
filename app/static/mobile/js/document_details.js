class DocumentDetails {
    constructor() {
        this.modal = document.getElementById('edit-modal');
        this.quantityInput = document.getElementById('edit-quantity');
        this.currentItemId = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeModal();
        });
    }

    editQuantity(itemId) {
        this.currentItemId = itemId;
        this.modal.style.display = 'block';
        this.quantityInput.focus();
    }

    async saveQuantity() {
        const newQuantity = this.quantityInput.value;
        
        try {
            const response = await fetch('/mobile/api/update-item-quantity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    item_id: this.currentItemId,
                    quantity: newQuantity
                })
            });
            
            if (response.ok) {
                location.reload();
            }
        } catch (error) {
            console.error('Update error:', error);
        }
    }

    closeModal() {
        this.modal.style.display = 'none';
        this.currentItemId = null;
        this.quantityInput.value = '';
    }
}

const documentDetails = new DocumentDetails();

function editQuantity(itemId) {
    documentDetails.editQuantity(itemId);
}

function closeModal() {
    documentDetails.closeModal();
}

async function closeDocument(deliveryNote) {
    if (!confirm('Are you sure you want to close this document?')) return;

    try {
        const response = await fetch(`/mobile/api/close-document/${deliveryNote}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            window.location.href = '/mobile/documents';
        }
    } catch (error) {
        console.error('Close document error:', error);
    }
}