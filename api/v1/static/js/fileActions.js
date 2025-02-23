// handle download and delete operations

import { NotificationManager } from './notifications.js';

export class FileActionHandler {
    constructor(fileDisplayManager) {
        this.API_BASE_URL = '/api/v1';
        this.fileDisplayManager = fileDisplayManager;
        this.filesContainer = document.getElementById('files-container');
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.filesContainer.addEventListener('click', async (event) => {
            const downloadIcon = event.target.closest('.download-file');
            const deleteIcon = event.target.closest('.delete-file');
            
            if (downloadIcon) await this.handleDownload(downloadIcon);
            if (deleteIcon) await this.handleDelete(deleteIcon);
        });
    }

    async handleDownload(element) {
        try {
            const fileKey = element.dataset.fileKey;
            const response = await fetch(`${this.API_BASE_URL}/download?file_key=${encodeURIComponent(fileKey)}`);
            
            if (!response.ok) throw new Error('Failed to generate download URL');
            
            const { presigned_url } = await response.json();
            window.location.href = presigned_url;
            NotificationManager.showSuccess('Download started!');
        } catch (error) {
            console.error('Download error:', error);
            NotificationManager.showError('Failed to download file');
        }
    }

    async handleDelete(element) {
        const fileKey = element.dataset.fileKey;
        if (!fileKey) {
            NotificationManager.showError('File key missing');
            return;
        }

        try {
            const shouldDelete = await NotificationManager.showConfirmationDialog(
                'Are you sure you want to delete this file? This action cannot be undone.',
                'Delete',
                'Cancel'
            );

            if (!shouldDelete) {
                NotificationManager.showToast('File deletion canceled.', 'error');
                return;
            }

            const response = await fetch(
                `${this.API_BASE_URL}/delete?file_key=${encodeURIComponent(fileKey)}`,
                { method: 'DELETE' }
            );

            if (response.ok) {
                NotificationManager.showSuccess('File deleted successfully!');
                await this.fileDisplayManager.fetchRecentFiles();
            } else {
                const errorData = await response.json();
                NotificationManager.showError(`Failed to delete file: ${errorData.error}`);
            }
        } catch (error) {
            console.error('Delete request error:', error);
            NotificationManager.showError(`An error occurred: ${error.message}`);
        }
    }
}
