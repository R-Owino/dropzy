// main entry point

import { initializeSidebar } from './sidebar.js';
import { FileUploader } from './fileUpload.js';
import { FileDisplayManager } from './fileDisplay.js';
import { FileActionHandler } from './fileActions.js';

document.addEventListener('DOMContentLoaded', async () => {
    // Initialize Lucide icons
    lucide.createIcons();
    
    // Initialize all modules
    const sidebar = initializeSidebar();
    const fileDisplayManager = new FileDisplayManager();
    const fileUploader = new FileUploader();
    const fileActionHandler = new FileActionHandler(fileDisplayManager);
});
