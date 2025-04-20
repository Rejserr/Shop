class DocumentManager {
    constructor() {
        this.deliveryNoteFilter = document.getElementById('delivery-note-filter');
        this.documentMsiFilter = document.getElementById('document-msi-filter');
        this.initializeFilters();
    }

    initializeFilters() {
        [this.deliveryNoteFilter, this.documentMsiFilter].forEach(filter => {
            filter.addEventListener('input', () => this.filterDocuments());
        });
    }

    async filterDocuments() {
        const deliveryNote = this.deliveryNoteFilter.value;
        const documentMsi = this.documentMsiFilter.value;

        try {
            const response = await fetch(`/mobile/api/filter-documents?delivery_note=${deliveryNote}&document_msi=${documentMsi}`);
            const documents = await response.json();
            this.updateDocumentsList(documents);
        } catch (error) {
            console.error('Filter error:', error);
        }
    }

    updateDocumentsList(documents) {
        const container = document.getElementById('documents-container');
        container.innerHTML = documents.map(doc => this.createDocumentCard(doc)).join('');
    }

    createDocumentCard(doc) {
        return `
            <div class="document-card">
                <div class="document-header">
                    <span class="delivery-note">${doc.delivery_note}</span>
                    <span class="document-status ${doc.status.toLowerCase()}">${doc.status}</span>
                </div>
                <div class="document-details">
                    <div>MSI: ${doc.document_msi}</div>
                    <div>Items: ${doc.item_count}</div>
                </div>
                <div class="document-actions">
                    <button onclick="viewDocument('${doc.delivery_note}')" class="action-btn">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button onclick="closeDocument('${doc.delivery_note}')" class="action-btn close-btn">
                        <i class="fas fa-check"></i> Close
                    </button>
                </div>
            </div>
        `;
    }
}

async function viewDocument(deliveryNote) {
    window.location.href = `/mobile/document/${deliveryNote}`;
}

async function closeDocument(deliveryNote) {
    if (!confirm('Are you sure you want to close this document?')) return;

    try {
        const response = await fetch(`/mobile/api/close-document/${deliveryNote}`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            location.reload();
        }
    } catch (error) {
        console.error('Close document error:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DocumentManager();
});
