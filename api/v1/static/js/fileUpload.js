// file upload handling

export class FileUploader {
    constructor() {
        this.MAX_FILE_SIZE = 2.5 * 1024 * 1024 * 1024;
        this.CHUNK_SIZE = 5 * 1024 * 1024;
        this.API_BASE_URL = '/api/v1';
        
        this.elements = {
            fileInput: document.getElementById('file-upload'),
            fileInfo: document.querySelector('.file-info'),
            selectedFilename: document.getElementById('selected-filename'),
            uploadButton: document.getElementById('upload-button'),
            progressContainer: document.querySelector('.progress-container'),
            progressBar: document.getElementById('upload-progress'),
            uploadStatus: document.getElementById('upload-status')
        };

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.elements.fileInput.addEventListener('change', this.handleFileSelection.bind(this));
        this.elements.uploadButton.addEventListener('click', this.handleUpload.bind(this));
    }

    handleFileSelection(event) {
        const file = event.target.files[0];
        this.resetUploadState();

        if (!file) {
            this.elements.fileInfo.style.display = 'none';
            return;
        }

        if (file.size > this.MAX_FILE_SIZE) {
            this.showError(`File "${file.name}" exceeds the maximum size of 2.5GB`);
            return;
        }

        this.elements.selectedFilename.textContent = file.name;
        this.elements.fileInfo.style.display = 'block';
    }

    async handleUpload() {
        const file = this.elements.fileInput.files[0];
        if (!file) return;

        try {
            const exists = await this.checkFileExists(file.name);
            if (exists && !(await this.shouldOverwriteDialog(file.name))) {
                this.resetForm();
                return;
            }

            await this.performUpload(file);
        } catch (error) {
            console.error('Upload error:', error);
            this.showError(`Error uploading "${file.name}": ${error.message}`);
        } finally {
            this.elements.uploadButton.disabled = false;
        }
    }

    async checkFileExists(fileName) {
        const response = await fetch(`${this.API_BASE_URL}/upload/check-file-exists`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fileName })
        });
        if (!response.ok) throw new Error('Failed to check file existence');
        const { exists } = await response.json();
        return exists;
    }

    async performUpload(file) {
        this.elements.progressContainer.style.display = 'block';
        this.elements.uploadButton.disabled = true;
        this.elements.uploadStatus.textContent = 'Initializing upload...';

        const { uploadId, key } = await this.initializeUpload(file);
        const chunks = this.createChunks(file);
        const parts = await this.uploadChunks(chunks, file, uploadId, key);
        await this.completeUpload(key, uploadId, parts);

        await this.showTemporarySuccess(`File "${file.name}" uploaded successfully.`);
    }

    async initializeUpload(file) {
        const response = await fetch(`${this.API_BASE_URL}/upload/initialize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                fileName: file.name,
                contentType: file.type
            })
        });
        if (!response.ok) throw new Error('Failed to initialize upload');
        return response.json();
    }

    createChunks(file) {
        const chunks = [];
        let start = 0;
        while (start < file.size) {
            chunks.push(file.slice(start, Math.min(start + this.CHUNK_SIZE, file.size)));
            start += this.CHUNK_SIZE;
        }
        return chunks;
    }

    async uploadChunks(chunks, file, uploadId, key) {
        const parts = [];
        let uploadedSize = 0;

        for (let i = 0; i < chunks.length; i++) {
            const url = await this.getChunkUploadUrl(file.name, uploadId, i + 1);
            const uploadResponse = await fetch(url, {
                method: 'PUT',
                body: chunks[i]
            });

            if (!uploadResponse.ok) throw new Error(`Failed to upload part ${i + 1}`);

            uploadedSize += chunks[i].size;
            this.updateProgress((uploadedSize / file.size) * 100);

            parts.push({
                PartNumber: i + 1,
                ETag: uploadResponse.headers.get('Etag')
            });
        }

        return parts;
    }

    async getChunkUploadUrl(fileName, uploadId, partNumber) {
        const response = await fetch(`${this.API_BASE_URL}/upload/chunk-url`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fileName, uploadId, partNumber })
        });
        if (!response.ok) throw new Error('Failed to get chunk upload URL');
        const { url } = await response.json();
        return url;
    }

    async completeUpload(key, uploadId, parts) {
        const response = await fetch(`${this.API_BASE_URL}/upload/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key, uploadId, parts })
        });
        if (!response.ok) throw new Error('Failed to complete upload');
    }

    shouldOverwriteDialog(fileName) {
        return new Promise(resolve => {
            const dialog = document.createElement('div');
            dialog.className = 'confirmation-dialog';
            dialog.innerHTML = `
                <div class="dialog-content">
                    <p>A file named "${fileName}" already exists. Do you want to continue?</p>
                    <div class="dialog-buttons">
                        <button class="confirm-btn">Continue</button>
                        <button class="cancel-btn">Cancel</button>
                    </div>
                </div>
            `;

            dialog.querySelector('.confirm-btn').onclick = () => {
                document.body.removeChild(dialog);
                resolve(true);
            };
            dialog.querySelector('.cancel-btn').onclick = () => {
                document.body.removeChild(dialog);
                resolve(false);
            };

            document.body.appendChild(dialog);
        });
    }

    async showTemporarySuccess(message, duration = 3000) {
        this.showSuccess(message);
        setTimeout(() => {
            this.resetForm();
            this.resetUploadState();
        }, duration);
    }

    updateProgress(percentage) {
        this.elements.progressBar.style.width = `${percentage}%`;
        this.elements.uploadStatus.textContent = `Uploading: ${Math.round(percentage)}%`;
    }

    resetUploadState() {
        this.elements.uploadStatus.textContent = '';
        this.elements.uploadStatus.className = 'upload-status';
        this.elements.progressBar.style.width = '0%';
        this.elements.progressContainer.style.display = 'none';
    }

    resetForm() {
        this.elements.fileInput.value = '';
        this.elements.fileInfo.style.display = 'none';
        this.resetUploadState();
    }

    showError(message) {
        this.elements.uploadStatus.textContent = message;
        this.elements.uploadStatus.className = 'upload-status error';
        this.elements.fileInfo.style.display = 'none';
        this.elements.fileInput.value = '';
    }

    showSuccess(message) {
        this.elements.uploadStatus.textContent = message;
        this.elements.uploadStatus.className = 'upload-status success';
    }
}
