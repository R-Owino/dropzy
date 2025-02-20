// Initialize Lucide Icons
lucide.createIcons();

// API Base URL
const API_BASE_URL = '/api/v1';

// Sidebar toggle functionality
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const emailContainer = document.querySelector('.user-email-container');
    const logoutSection = document.querySelector('.logout-section');
    const dropdownArrow = document.querySelector('.dropdown-arrow');

    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('expanded');
    });

    emailContainer.addEventListener('click', () => {
        if (sidebar.classList.contains('expanded')) {
            logoutSection.classList.toggle('expanded');
            dropdownArrow.classList.toggle('active');
        }
    });

    // close dropdown when clicking outside
    document.addEventListener('click', (event) => {
        if (!emailContainer.contains(event.target) && !logoutSection.contains(event.target)) {
            logoutSection.classList.remove('expanded');
            dropdownArrow.classList.remove('active');
        }
    });
});

// File upload handler
document.addEventListener('DOMContentLoaded', async function () {
    const fileInput = document.getElementById('file-upload');
    const fileInfo = document.querySelector('.file-info');
    const selectedFilename = document.getElementById('selected-filename');
    const uploadButton = document.getElementById('upload-button');
    const progressContainer = document.querySelector('.progress-container');
    const progressBar = document.getElementById('upload-progress');
    const uploadStatus = document.getElementById('upload-status');
    const fetchRecentFiles = await initializeSearchAndDisplayFunctionality();

    const MAX_FILE_SIZE = 2.5 * 1024 * 1024 * 1024;
    const CHUNK_SIZE = 5 * 1024 * 1024;

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        resetUploadState();

        if (!file) {
            fileInfo.style.display = 'none';
            return;
        }

        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
            showError(`File "${file_name}" exceeds the maximum size of 2.5GB`);
            return;
        }

        // Show file info and upload button
        selectedFilename.textContent = file.name;
        fileInfo.style.display = 'block';
    });

    uploadButton.addEventListener('click', async () => {
        const file = fileInput.files[0];
        if (!file) return;

        try {
            // check if the file exists
            const checkResponse = await fetch(`${API_BASE_URL}/upload/check-file-exists`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fileName: file.name })
            });

            if (!checkResponse.ok) throw new Error('Failed to check file existence');
            const { exists } = await checkResponse.json();

            // ask for upload confirmation if file exists
            if (exists) {
                const shouldContinue = await shouldOverwriteDialog(file.name);
                if (!shouldContinue) {
                    resetForm();
                    return;
                }
            }

            // initialize upload
            progressContainer.style.display = 'block';
            uploadButton.disabled = true;
            uploadStatus.textContent = 'Initializing upload...';

            // initialize multipart upload
            const initResponse = await fetch(`${API_BASE_URL}/upload/initialize`, {
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

            if (!initResponse.ok) throw new Error('Failed to initialize upload');
            const { uploadId, key } = await initResponse.json();

            // create upload chunks
            const chunks = []
            let start = 0;
            while (start < file.size) {
                chunks.push(file.slice(start, Math.min(start + CHUNK_SIZE, file.size)));
                start += CHUNK_SIZE;
            }

            // upload chunks
            const parts = []
            let uploadedSize = 0;

            for (let i = 0; i < chunks.length; i++) {
                // get pre-signed URL for a chunk
                const urlResponse = await fetch(`${API_BASE_URL}/upload/chunk-url`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        fileName: file.name,
                        uploadId: uploadId,
                        partNumber: i + 1
                    })
                });

                if (!urlResponse.ok) throw new Error('Failed to get chunk upload URL');
                const { url } = await urlResponse.json();

                // upload chunk
                const uploadResponse = await fetch(url, {
                    method: 'PUT',
                    body: chunks[i]
                });

                if (!uploadResponse.ok) throw new Error(`Failed to upload part ${i + 1}`);

                uploadedSize += chunks[i].size;
                const progress = (uploadedSize / file.size) * 100;
                updateProgress(progress);

                parts.push({
                    PartNumber: i + 1,
                    ETag: uploadResponse.headers.get('Etag')
                });
            }
            // complete multipart upload
            const completeResponse = await fetch(`${API_BASE_URL}/upload/complete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    key: key,
                    uploadId: uploadId,
                    parts: parts
                })
            });

            if (!completeResponse.ok) throw new Error('Failed to complete upload');

            await showTemporarySuccess(`File "${file.name}" uploaded successfully.`);
            await fetchRecentFiles();

        } catch (error) {
            console.error('Upload error:', error);
            showError(`Error uploading "${file.name}": ${error.message}`);
        } finally {
            uploadButton.disabled = false;
        }
    });

    function shouldOverwriteDialog(fileName) {
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

    async function showTemporarySuccess(message, duration = 3000) {
        showSuccess(message);
        setTimeout(() => {
            resetForm();
            resetUploadState();
        }, duration);
    }

    function updateProgress(percentage) {
        progressBar.style.width = `${percentage}%`;
        uploadStatus.textContent = `Uploading: ${Math.round(percentage)}%`;
    }

    function resetUploadState() {
        uploadStatus.textContent = '';
        uploadStatus.className = 'upload-status';
        progressBar.style.width = '0%';
        progressContainer.style.display = 'none';
    }

    function resetForm() {
        fileInput.value = '';
        fileInfo.style.display = 'none';
        resetUploadState();
    }

    function showError(message) {
        uploadStatus.textContent = message;
        uploadStatus.className = 'upload-status error';
        fileInfo.style.display = 'none';
        fileInput.value = '';
    }

    function showSuccess(message) {
        uploadStatus.textContent = message;
        uploadStatus.className = 'upload-status success';
    }
});

// handle fetching, displaying and searching files
async function initializeSearchAndDisplayFunctionality() {
    const searchInput = document.querySelector('.search-input');
    const searchContainer = document.querySelector('.search-container');
    const filesContainer = document.getElementById('files-container');

    // Keep track of whether we're in search mode
    let isSearching = false;

    // display a message when no files are present
    function showNoFilesMessage(message) {
        filesContainer.innerHTML = `
            <div class="message-container">
                <i data-lucide="inbox" class="message-icon"></i>
                <p class="message-text">${message}</p>
            </div>
        `;
        lucide.createIcons();
    }

    // fetch and display recent files
    async function fetchRecentFiles() {
        try {
            const response = await fetch(`${API_BASE_URL}/file-metadata`);
            if (!response.ok) {
                throw new Error('Failed to fetch files');
            }
            const data = await response.json();

            // Only proceed with display logic if not in search mode
            if (!isSearching) {
                if (data.files && data.files.length > 0) {
                    displayFiles(data.files);
                } else {
                    showNoFilesMessage(
                        "No files have been uploaded yet. Upload your first file to get started!"
                    );
                }
            }
        } catch (error) {
            console.error('Error fetching files:', error);
            if (!isSearching) {
                showNoFilesMessage(
                    "Unable to load files. Please try again later."
                );
            }
        }
    }

    // display files in the three-column layout
    function displayFiles(files) {
        filesContainer.innerHTML = '';

        const columns = [
            document.createElement('div'),
            document.createElement('div'),
            document.createElement('div')
        ];
        columns.forEach(col => {
            col.className = 'files-column';
            filesContainer.appendChild(col);
        });

        files.forEach((file, index) => {
            const columnIndex = Math.floor(index / Math.ceil(files.length / 3));
            const fileItem = createFileElement(file);
            columns[columnIndex].appendChild(fileItem);
        });

        lucide.createIcons();
    }

    // handle search functionality
    async function handleSearch(searchTerm) {
        if (searchTerm.trim() === '') {
            isSearching = false;
            fetchRecentFiles(); // Return to normal file display
            return;
        }

        isSearching = true;
        try {
            const response = await fetch(`${API_BASE_URL}/search-files?search=${encodeURIComponent(searchTerm)}`);
            if (!response.ok) {
                throw new Error('Search failed');
            }
            const data = await response.json();

            if (data.files && data.files.length > 0) {
                displayFiles(data.files);
            } else {
                showNoFilesMessage(
                    `No files found matching "${searchTerm}". Try a different search term.`
                );
            }
        } catch (error) {
            console.error('Error during search:', error);
            showNoFilesMessage(
                "An error occurred while searching. Please try again."
            );
        }
    }

    // Debounce function to limit API calls
    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // search input placeholder management
    searchInput.addEventListener('focus', () => {
        searchInput.placeholder = "Type to search...";
    });

    searchInput.addEventListener('blur', () => {
        searchInput.placeholder = "Search files...";

        if (searchInput.value.trim() === '') {
            fetchRecentFiles();
        }
    });

    // Set up search event listeners
    const debouncedSearch = debounce(handleSearch, 300);
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.trim();
        debouncedSearch(searchTerm);
    });

    // Handle clicking outside search
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            searchInput.classList.remove('active'); // Hide input
            searchInput.value = '';
            fetchRecentFiles();
        }
    });

    // Initial file fetch
    await fetchRecentFiles();

    // Return fetchRecentFiles so it can be used outside
    return fetchRecentFiles;
}

// Create file element with download and delete options
function createFileElement(file) {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';

    // Determine icon based on file type
    const iconMap = {
        'pdf': 'file-text',
        'doc': 'file-text',
        'docx': 'file-text',
        'txt': 'file-text',
        'md': 'file-text',
        'epub': 'file-text',
        'odt': 'file-text',
        'jpg': 'image',
        'jpeg': 'image',
        'png': 'image',
        'gif': 'image',
        'gifv': 'image',
        'bmp': 'image',
        'svg': 'image',
        'ico': 'image',
        'xlsx': 'file-spreadsheet',
        'csv': 'file-spreadsheet',
        'mp4': 'file-video',
        'mov': 'file-video',
        'avi': 'file-video',
        'mkv': 'file-video',
        'webm': 'file-video',
        'mp3': 'file-audio',
        'wav': 'file-audio',
        'aac': 'file-audio',
        'zip': 'file-archive',
        'rar': 'file-archive',
        '7z': 'file-archive',
        'tar': 'file-archive',
        'gz': 'file-archive',
        'sh': 'file-code',
        'js': 'file-code',
        'py': 'file-code',
        'html': 'file-code',
        'css': 'file-code',
        'json': 'file-code',
        'xml': 'file-code',
        'ppt': 'file-presentation',
        'pptx': 'file-presentation',
        'apk': 'file-app',
        'exe': 'file-app',
        'dll': 'file-app',
        'iso': 'file-disc',
        'log': 'file-log',
        'conf': 'file-config',
        'ini': 'file-config',
        'yaml': 'file-config',
        'yml': 'file-config'
    };

    const fileExt = file.file_name.split('.').pop().toLowerCase();
    const icon = iconMap[fileExt] || 'file';

    fileItem.innerHTML = `
        <i class="file-icon" data-lucide="${icon}"></i>
        <div class="file-details">
            <div class="file-name">${file.file_name}</div>
            <div class="file-size">${(file.size_bytes / 1024 / 1024).toFixed(1)} MB</div>
        </div>
        <div class="file-actions">
            <i class="action-icon download-file" data-file-key="${file.file_key}" data-lucide="download"></i>
            <i class="action-icon delete-file" data-file-key="${file.file_key}" data-lucide="trash-2"></i>
        </div>
    `;

    return fileItem;
}

// Function to display a toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
}

// Event listener for download and delete confirmation
document.addEventListener('DOMContentLoaded', async () => {
    const fetchRecentFiles = await initializeSearchAndDisplayFunctionality();

    const filesContainer = document.getElementById('files-container');

    filesContainer.addEventListener('click', async (event) => {
        const downloadIcon = event.target.closest('.download-file');
        if (!downloadIcon) return;

        try {
            const fileKey = downloadIcon.dataset.fileKey;
            const response = await fetch(`${API_BASE_URL}/download?file_key=${encodeURIComponent(fileKey)}`);

            if (!response.ok) {
                throw new Error('Failed to generate download URL');
            }

            const data = await response.json();
            const downloadUrl = data.presigned_url;

            window.location.href = downloadUrl;
            showToast('Download started!');

        } catch (error) {
            console.error('Download error:', error);
            showToast('Failed to download file', 'error');
        }
    });

    filesContainer.addEventListener('click', async (event) => {
        const deleteIcon = event.target.closest('.delete-file');
        if (!deleteIcon) return;

        try {
            const fileKey = deleteIcon.dataset.fileKey;
            if (!fileKey) {
                throw new Error('File key missing');
            }

            const shouldDelete = await new Promise((resolve) => {
                const dialog = document.createElement('div');
                dialog.className = 'confirmation-dialog';
                dialog.innerHTML = `
                    <div class="dialog-content">
                        <p>Are you sure you want to delete this file? This action cannot be undone.</p>
                        <div class="dialog-buttons">
                            <button class="confirm-btn">Delete</button>
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

            if (!shouldDelete) {
                console.log('File deletion canceled');
                showToast('File deletion canceled.', 'error');
                return;
            }

            const response = await fetch(`${API_BASE_URL}/delete?file_key=${encodeURIComponent(fileKey)}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                showToast('File deleted successfully!');
                await fetchRecentFiles();
            } else {
                const errorData = await response.json();
                console.error('Delete error:', errorData.error);
                showToast(`Failed to delete file: ${errorData.error}`, 'error');
            }
        } catch (error) {
            console.error('Delete request error:', error);
            showToast(`An error occurred: ${error.message}`, 'error');
        }
    });
});
