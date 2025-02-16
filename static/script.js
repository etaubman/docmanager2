// API endpoints
const API_BASE = '/api';
const ENDPOINTS = {
    documents: `${API_BASE}/documents`,
    metadataFields: `${API_BASE}/metadata-fields`,
    documentTypes: `${API_BASE}/document-types`
};

// DOM Elements and Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const documentForm = document.getElementById('documentForm');
    const documentsList = document.getElementById('documentsList');
    const titleInput = document.getElementById('title');
    const contentInput = document.getElementById('content');
    const documentIdInput = document.getElementById('documentId');
    const submitBtn = document.getElementById('submitBtn');
    const clearBtn = document.getElementById('clearBtn');

    // Initialize tabs
    initializeTabs();
    
    // Load initial data
    loadDocuments();
    
    // Set up form event listeners
    if (documentForm) {
        documentForm.addEventListener('submit', handleSubmit);
    }
    if (clearBtn) {
        clearBtn.addEventListener('click', clearForm);
    }
    
    // Set up metadata form listener
    const metadataForm = document.getElementById('metadataForm');
    if (metadataForm) {
        metadataForm.addEventListener('submit', handleMetadataSubmit);
    }
    
    // Set up doctype form listener
    const doctypeForm = document.getElementById('doctypeForm');
    if (doctypeForm) {
        doctypeForm.addEventListener('submit', handleDoctypeSubmit);
    }
    
    // Set up document type change listener
    const documentTypeSelect = document.getElementById('documentType');
    if (documentTypeSelect) {
        documentTypeSelect.addEventListener('change', handleDocumentTypeChange);
    }
    
    // Set up upload form listener
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUploadSubmit);
    }
});

// Tab initialization function
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // First, ensure only the first tab is active initially
    tabContents.forEach((content, index) => {
        if (index === 0) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
    
    tabButtons.forEach((button, index) => {
        if (index === 0) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
        
        button.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            const tabContent = document.getElementById(tabId);
            if (tabContent) {
                tabContent.classList.add('active');
            }
            
            // Load data for the selected tab
            if (tabId === 'metadata') {
                loadMetadataFields();
            } else if (tabId === 'doctypes') {
                loadDocumentTypes();
            } else if (tabId === 'documents') {
                loadDocuments();
                loadDocumentTypesForSelect();
            }
        });
    });
}

// Load all documents
async function loadDocuments() {
    try {
        const response = await fetch(ENDPOINTS.documents);
        const documents = await response.json();
        displayDocuments(documents);
    } catch (error) {
        console.error('Error loading documents:', error);
        alert('Failed to load documents');
    }
}

// Display documents in the list
function displayDocuments(documents) {
    documentsList.innerHTML = documents.map(doc => `
        <div class="document-item">
            <div class="document-title">${escapeHtml(doc.title)}</div>
            <div class="document-content">${escapeHtml(doc.content.substring(0, 150))}${doc.content.length > 150 ? '...' : ''}</div>
            <div class="timestamp">
                Created: ${new Date(doc.created_at).toLocaleString()}
                ${doc.updated_at ? `<br>Updated: ${new Date(doc.updated_at).toLocaleString()}` : ''}
            </div>
            ${doc.file_path ? `
            <div class="document-file">
                <a href="${ENDPOINTS.documents}/download/${doc.id}" class="download-btn">
                    Download ${escapeHtml(doc.file_name)} (${formatFileSize(doc.file_size)})
                </a>
            </div>
            ` : ''}
            <div class="document-actions">
                <button onclick="editDocument(${doc.id})" class="edit-btn">Edit</button>
                <button onclick="deleteDocument(${doc.id})" class="delete-btn">Delete</button>
            </div>
        </div>
    `).join('');
}

// Handle form submission (create/update)
async function handleSubmit(event) {
    event.preventDefault();
    
    const isEditing = documentIdInput.value;
    if (isEditing) {
        // Currently don't support file upload during edit
        const documentData = {
            title: titleInput.value,
            content: contentInput.value
        };

        try {
            const response = await fetch(`${ENDPOINTS.documents}/${documentIdInput.value}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(documentData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            clearForm();
            loadDocuments();
            showNotification('Document saved successfully.');
        } catch (error) {
            console.error('Error saving document:', error);
            alert('Failed to save document');
        }
    } else {
        // Handle create with potential file upload
        const fileInput = document.getElementById('file');
        const file = fileInput.files[0];
        
        try {
            let response;
            
            if (file) {
                // Create FormData for file upload
                const formData = new FormData();
                formData.append('file', file);
                formData.append('document', JSON.stringify({
                    title: titleInput.value,
                    content: contentInput.value
                }));
                
                response = await fetch(`${ENDPOINTS.documents}/upload`, {
                    method: 'POST',
                    body: formData
                });
            } else {
                // Regular document creation without file
                response = await fetch(ENDPOINTS.documents, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        title: titleInput.value,
                        content: contentInput.value
                    })
                });
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            clearForm();
            loadDocuments();
            showNotification('Document saved successfully.');
        } catch (error) {
            console.error('Error saving document:', error);
            alert('Failed to save document');
        }
    }
}

// Edit document
async function editDocument(id) {
    try {
        const response = await fetch(`${ENDPOINTS.documents}/${id}`);
        const document = await response.json();
        
        titleInput.value = document.title;
        contentInput.value = document.content;
        documentIdInput.value = document.id;
        submitBtn.textContent = 'Update Document';
    } catch (error) {
        console.error('Error loading document for edit:', error);
        alert('Failed to load document for editing');
    }
}

// Delete document
async function deleteDocument(id) {
    if (!confirm('Are you sure you want to delete this document?')) {
        return;
    }

    try {
        const response = await fetch(`${ENDPOINTS.documents}/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        loadDocuments();
    } catch (error) {
        console.error('Error deleting document:', error);
        alert('Failed to delete document');
    }
}

// Clear form
function clearForm() {
    documentForm.reset();
    documentIdInput.value = '';
    submitBtn.textContent = 'Create Document';
}

// Helper function to escape HTML and prevent XSS
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Format file size in bytes to human-readable format
function formatFileSize(bytes) {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
}

// Metadata Fields Management
async function loadMetadataFields() {
    try {
        const response = await fetch(ENDPOINTS.metadataFields);
        const fields = await response.json();
        const fieldsList = document.getElementById('metadataFieldsList');
        fieldsList.innerHTML = fields.map(field => `
            <div class="metadata-field">
                <h4>${field.display_name || field.name}</h4>
                <p>Type: ${field.field_type}</p>
                <p>${field.description || ''}</p>
                ${field.enum_values ? `<p>Values: ${field.enum_values}</p>` : ''}
                <p>Multi-valued: ${field.is_multi_valued ? 'Yes' : 'No'}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading metadata fields:', error);
    }
}

async function handleMetadataSubmit(e) {
    e.preventDefault();
    const formData = {
        name: document.getElementById('fieldName').value,
        display_name: document.getElementById('fieldDisplayName').value || document.getElementById('fieldName').value,
        description: document.getElementById('fieldDescription').value,
        field_type: document.getElementById('fieldType').value,
        is_multi_valued: document.getElementById('isMultiValued').checked,
        enum_values: document.getElementById('enumValues').value || null
    };

    try {
        const response = await fetch(ENDPOINTS.metadataFields, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        if (response.ok) {
            document.getElementById('metadataForm').reset();
            loadMetadataFields();
            showNotification('Metadata field created.');
        }
    } catch (error) {
        console.error('Error creating metadata field:', error);
        showNotification('Failed to create metadata field.', 'error');
    }
}

// Document Types Management
async function loadDocumentTypes() {
    try {
        const [typesResponse, fieldsResponse] = await Promise.all([
            fetch(ENDPOINTS.documentTypes),
            fetch(ENDPOINTS.metadataFields)
        ]);
        const types = await typesResponse.json();
        const fields = await fieldsResponse.json();
        
        const typesList = document.getElementById('doctypesList');
        typesList.innerHTML = types.map(type => `
            <div class="document-type">
                <h4>${type.name}</h4>
                <p>${type.description || ''}</p>
                <h5>Required Metadata:</h5>
                <ul>
                    ${type.metadata_fields.map(field => `
                        <li>${field.name} (${field.field_type})</li>
                    `).join('')}
                </ul>
                <button onclick="editDocumentTypeFields(${type.id}, ${JSON.stringify(fields)})" class="edit-btn">
                    Edit Fields
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading document types:', error);
    }
}

async function loadDocumentTypesForSelect() {
    try {
        const response = await fetch(ENDPOINTS.documentTypes);
        const types = await response.json();
        const select = document.getElementById('documentType');
        select.innerHTML = '<option value="">Select Document Type</option>' +
            types.map(type => `
                <option value="${type.id}">${type.name}</option>
            `).join('');
    } catch (error) {
        console.error('Error loading document types for select:', error);
    }
}

async function handleDoctypeSubmit(e) {
    e.preventDefault();
    const formData = {
        name: document.getElementById('typeName').value,
        description: document.getElementById('typeDescription').value,
        metadata_fields: Array.from(document.querySelectorAll('#fieldSelection input:checked'))
            .map(input => ({
                metadata_field_id: parseInt(input.value),
                is_required: input.dataset.required === 'true'
            }))
    };

    try {
        const response = await fetch(ENDPOINTS.documentTypes, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        if (response.ok) {
            document.getElementById('doctypeForm').reset();
            loadDocumentTypes();
            showNotification('Document type created.');
        }
    } catch (error) {
        console.error('Error creating document type:', error);
        showNotification('Failed to create document type.', 'error');
    }
}

async function editDocumentTypeFields(typeId, allFields) {
    const type = await (await fetch(`${ENDPOINTS.documentTypes}/${typeId}`)).json();
    const currentFields = type.metadata_fields.map(f => f.id);
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Edit Metadata Fields</h3>
            <form id="editFieldsForm">
                ${allFields.map(field => `
                    <div class="field-selection">
                        <label>
                            <input type="checkbox" 
                                name="field_${field.id}" 
                                value="${field.id}"
                                ${currentFields.includes(field.id) ? 'checked' : ''}>
                            ${field.name} (${field.field_type})
                        </label>
                        <label class="required-checkbox">
                            <input type="checkbox" 
                                name="required_${field.id}"
                                ${type.metadata_fields.find(f => f.id === field.id)?.is_required ? 'checked' : ''}>
                            Required
                        </label>
                    </div>
                `).join('')}
                <div class="modal-actions">
                    <button type="submit">Save</button>
                    <button type="button" onclick="this.closest('.modal').remove()">Cancel</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const form = modal.querySelector('form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fieldAssociations = allFields
            .filter(field => form.querySelector(`[name="field_${field.id}"]`).checked)
            .map(field => ({
                metadata_field_id: field.id,
                is_required: form.querySelector(`[name="required_${field.id}"]`).checked
            }));
            
        try {
            await fetch(`${ENDPOINTS.documentTypes}/${typeId}/fields`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ field_associations: fieldAssociations })
            });
            
            modal.remove();
            loadDocumentTypes();
        } catch (error) {
            console.error('Error updating fields:', error);
        }
    });
}

// Document Upload with Metadata
async function handleDocumentTypeChange() {
    const typeId = this.value;
    const metadataFields = document.getElementById('metadataFields');
    
    if (!typeId) {
        metadataFields.innerHTML = '';
        return;
    }

    try {
        const response = await fetch(`${ENDPOINTS.documentTypes}/${typeId}`);
        const docType = await response.json();
        
        metadataFields.innerHTML = docType.metadata_fields.map(field => `
            <div class="metadata-input">
                <label>${field.display_name || field.name}${field.is_required ? ' *' : ''}</label>
                ${getMetadataInputHtml(field)}
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading document type metadata:', error);
    }
}

function getMetadataInputHtml(field) {
    switch (field.field_type) {
        case 'text':
            return `<input type="text" name="metadata_${field.name}" ${field.is_required ? 'required' : ''}>`;
        case 'integer':
            return `<input type="number" name="metadata_${field.name}" ${field.is_required ? 'required' : ''}>`;
        case 'date':
            return `<input type="date" name="metadata_${field.name}" ${field.is_required ? 'required' : ''}>`;
        case 'boolean':
            return `<input type="checkbox" name="metadata_${field.name}">`;
        case 'enum':
            const options = field.enum_values.split(',').map(v => v.trim());
            return `
                <select name="metadata_${field.name}" ${field.is_required ? 'required' : ''}>
                    <option value="">Select...</option>
                    ${options.map(opt => `<option value="${opt}">${opt}</option>`).join('')}
                </select>
            `;
        default:
            return `<input type="text" name="metadata_${field.name}" ${field.is_required ? 'required' : ''}>`;
    }
}

// Handle document upload with metadata
async function handleUploadSubmit(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', document.getElementById('file').files[0]);
    formData.append('title', document.getElementById('title').value);
    
    const docTypeId = document.getElementById('documentType').value;
    if (docTypeId) {
        formData.append('document_type_id', docTypeId);
        
        // Collect metadata values
        const metadataValues = {};
        document.querySelectorAll('#metadataFields input, #metadataFields select').forEach(input => {
            const fieldName = input.name.replace('metadata_', '');
            if (input.type === 'checkbox') {
                metadataValues[fieldName] = input.checked;
            } else {
                metadataValues[fieldName] = input.value;
            }
        });
        formData.append('metadata_values', JSON.stringify(metadataValues));
    }

    try {
        const response = await fetch(ENDPOINTS.documents, {
            method: 'POST',
            body: formData
        });
        if (response.ok) {
            document.getElementById('uploadForm').reset();
            document.getElementById('metadataFields').innerHTML = '';
            loadDocuments();
            showNotification('Document uploaded successfully.');
        }
    } catch (error) {
        console.error('Error uploading document:', error);
        showNotification('Failed to upload document.', 'error');
    }
}

// New: Show Notification function
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    // Optionally adjust color for error type
    if (type === 'error') {
        notification.style.backgroundColor = 'var(--danger-color)';
    }
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.opacity = 0;
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

// Initial load
loadDocuments();