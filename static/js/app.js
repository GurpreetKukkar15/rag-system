// RAG System Frontend JavaScript
class RAGSystem {
    constructor() {
        this.apiBaseUrl = '';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkSystemStatus();
        this.setupFileUpload();
    }

    setupEventListeners() {
        // Question submission
        const askButton = document.getElementById('askButton');
        const questionInput = document.getElementById('questionInput');
        
        askButton.addEventListener('click', () => this.askQuestion());
        questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.askQuestion();
            }
        });
    }

    setupFileUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        // Click to upload
        uploadArea.addEventListener('click', () => fileInput.click());

        // File input change
        fileInput.addEventListener('change', (e) => this.handleFileUpload(e.target.files));

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFileUpload(e.dataTransfer.files);
        });
    }

    async checkSystemStatus() {
        try {
            const response = await fetch('/');
            const data = await response.json();
            
            document.getElementById('apiStatus').textContent = 'Online';
            document.getElementById('apiStatus').className = 'status-value ready';
            
            document.getElementById('vectorStatus').textContent = data.vector_store_loaded ? 'Loaded' : 'Not Loaded';
            document.getElementById('vectorStatus').className = `status-value ${data.vector_store_loaded ? 'ready' : 'not-ready'}`;
            
            // Get document count (mock for now)
            document.getElementById('docCount').textContent = '3 documents';
            document.getElementById('docCount').className = 'status-value ready';
            
        } catch (error) {
            console.error('Status check failed:', error);
            document.getElementById('apiStatus').textContent = 'Offline';
            document.getElementById('apiStatus').className = 'status-value not-ready';
        }
    }

    async handleFileUpload(files) {
        if (files.length === 0) return;

        const uploadProgress = document.getElementById('uploadProgress');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const uploadStatus = document.getElementById('uploadStatus');

        // Show progress
        uploadProgress.style.display = 'block';
        uploadStatus.style.display = 'none';

        try {
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                const progress = ((i + 1) / files.length) * 100;
                
                progressFill.style.width = `${progress}%`;
                progressText.textContent = `Uploading ${file.name}...`;

                await this.uploadFile(file);
            }

            // Success
            uploadProgress.style.display = 'none';
            uploadStatus.innerHTML = `
                <i class="fas fa-check-circle"></i>
                Successfully uploaded ${files.length} file(s). Processing documents...
            `;
            uploadStatus.className = 'upload-status success';
            uploadStatus.style.display = 'block';

            // Refresh document count
            setTimeout(() => this.checkSystemStatus(), 2000);

        } catch (error) {
            console.error('Upload failed:', error);
            uploadProgress.style.display = 'none';
            uploadStatus.innerHTML = `
                <i class="fas fa-exclamation-circle"></i>
                Upload failed: ${error.message}
            `;
            uploadStatus.className = 'upload-status error';
            uploadStatus.style.display = 'block';
        }
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(error);
        }

        return response.json();
    }

    async askQuestion() {
        const questionInput = document.getElementById('questionInput');
        const askButton = document.getElementById('askButton');
        const loading = document.getElementById('loading');
        const response = document.getElementById('response');
        const answerContent = document.getElementById('answerContent');

        const question = questionInput.value.trim();
        if (!question) return;

        // Show loading state
        askButton.disabled = true;
        loading.style.display = 'block';
        response.style.display = 'none';

        try {
            const apiResponse = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            });

            if (!apiResponse.ok) {
                throw new Error(`API Error: ${apiResponse.status}`);
            }

            const data = await apiResponse.json();
            
            // Display response
            answerContent.textContent = data.answer;
            response.style.display = 'block';
            
            // Clear input
            questionInput.value = '';

        } catch (error) {
            console.error('Query failed:', error);
            answerContent.textContent = `Error: ${error.message}`;
            response.style.display = 'block';
        } finally {
            // Hide loading state
            askButton.disabled = false;
            loading.style.display = 'none';
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RAGSystem();
});

// Add some utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showNotification(message, type = 'info') {
    // Simple notification system
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    if (type === 'success') {
        notification.style.background = '#48bb78';
    } else if (type === 'error') {
        notification.style.background = '#f56565';
    } else {
        notification.style.background = '#4299e1';
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}
