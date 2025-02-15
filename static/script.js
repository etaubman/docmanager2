// API endpoints
const API = {
    CREATE: '/api/documents/',
    UPLOAD: '/api/documents/upload',
    GET_ALL: '/api/documents/',
    UPDATE: (id) => `/api/documents/${id}`,
    DELETE: (id) => `/api/documents/${id}`,
    GET_ONE: (id) => `/api/documents/${id}`,
    DOWNLOAD: (id) => `/api/documents/download/${id}`
};

// DOM Elements
const documentForm = document.getElementById('documentForm');
const documentsList = document.getElementById('documentsList');
const titleInput = document.getElementById('title');
const contentInput = document.getElementById('content');
const documentIdInput = document.getElementById('documentId');
const submitBtn = document.getElementById('submitBtn');
const clearBtn = document.getElementById('clearBtn');

// Event Listeners
documentForm.addEventListener('submit', handleSubmit);
clearBtn.addEventListener('click', clearForm);
document.addEventListener('DOMContentLoaded', loadDocuments);

// Load all documents
async function loadDocuments() {
    try {
        const response = await fetch(API.GET_ALL);
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
                <a href="${API.DOWNLOAD(doc.id)}" class="download-btn">
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
            const response = await fetch(API.UPDATE(documentIdInput.value), {
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
                
                response = await fetch(API.UPLOAD, {
                    method: 'POST',
                    body: formData
                });
            } else {
                // Regular document creation without file
                response = await fetch(API.CREATE, {
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
        } catch (error) {
            console.error('Error saving document:', error);
            alert('Failed to save document');
        }
    }
}

// Edit document
async function editDocument(id) {
    try {
        const response = await fetch(API.GET_ONE(id));
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
        const response = await fetch(API.DELETE(id), {
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