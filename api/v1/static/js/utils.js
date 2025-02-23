// utility functions

export const utils = {
    debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    },

    getFileIcon(fileName) {
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
        const fileExt = fileName.split('.').pop().toLowerCase();
        return iconMap[fileExt] || 'file';
    },

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / 1048576).toFixed(1) + ' MB';
    }
};
