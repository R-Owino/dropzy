// handle toast and dialog notifications

export class NotificationManager {
    static showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }

    static async showConfirmationDialog(message, confirmText = 'Confirm', cancelText = 'Cancel') {
        return new Promise((resolve) => {
            const dialog = document.createElement('div');
            dialog.className = 'confirmation-dialog';
            dialog.innerHTML = `
                <div class="dialog-content">
                    <p>${message}</p>
                    <div class="dialog-buttons">
                        <button class="confirm-btn">${confirmText}</button>
                        <button class="cancel-btn">${cancelText}</button>
                    </div>
                </div>
            `;

            const cleanup = () => document.body.removeChild(dialog);
            dialog.querySelector('.confirm-btn').onclick = () => {
                cleanup();
                resolve(true);
            };
            dialog.querySelector('.cancel-btn').onclick = () => {
                cleanup();
                resolve(false);
            };

            document.body.appendChild(dialog);
        });
    }

    static showError(message) {
        this.showToast(message, 'error');
    }

    static showSuccess(message) {
        this.showToast(message, 'success');
    }
}
