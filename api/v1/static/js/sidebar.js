// sidebar functionality

const SELECTORS = {
    SIDEBAR: '.sidebar',
    TOGGLE: '.sidebar-toggle',
    EMAIL_CONTAINER: '.user-email-container',
    LOGOUT_SECTION: '.logout-section',
    DROPDOWN_ARROW: '.down-arrow',
    MODAL_OVERLAY: '.modal-overlay',
    DELETE_ACCOUNT_BTN: '.delete-account-btn',
    MODAL_CANCEL_BTN: '.modal-cancel',
    MODAL_DELETE_BTN: '.modal-delete',
    LOGOUT_BTN: '.logout-btn'
};

const API_ENDPOINTS = {
    register: '/api/v1/register',
    delete_account: '/api/v1/delete-account',
    logout: '/api/v1/logout'
};

class SidebarManager {
    constructor() {
        this.sidebar = document.querySelector(SELECTORS.SIDEBAR);
        this.toggle = document.querySelector(SELECTORS.TOGGLE);
        this.emailContainer = document.querySelector(SELECTORS.EMAIL_CONTAINER);
        this.logoutSection = document.querySelector(SELECTORS.LOGOUT_SECTION);
        this.dropdownArrow = document.querySelector(SELECTORS.DROPDOWN_ARROW);
        this.modalOverlay = document.querySelector(SELECTORS.MODAL_OVERLAY);
        this.deleteAccountBtn = document.querySelector(SELECTORS.DELETE_ACCOUNT_BTN);
        this.modalCancelBtn = document.querySelector(SELECTORS.MODAL_CANCEL_BTN);
        this.modalDeleteBtn = document.querySelector(SELECTORS.MODAL_DELETE_BTN);
        this.logoutBtn = document.querySelector(SELECTORS.LOGOUT_BTN);

        this.initializeEventListeners();
        this.initializeDeleteAccount();
        this.initializeLogout();
    }

    initializeEventListeners() {
        this.toggle.addEventListener('click', () => {
            this.toggleSidebar();
        });

        this.emailContainer.addEventListener('click', () => {
            this.handleEmailContainerClick();
        });

        const userIcon = document.querySelector('.user-icon');
        userIcon.addEventListener('click', () => {
            this.toggleSidebar();
        });

        document.addEventListener('click', (event) => {
            this.handleOutsideClick(event);
        });
    }

    toggleSidebar() {
        this.sidebar.classList.toggle('expanded');
        if (!this.sidebar.classList.contains('expanded')) {
            this.logoutSection.classList.remove('expanded');
            this.dropdownArrow.classList.remove('active');
        }
    }

    handleEmailContainerClick() {
        if (this.sidebar.classList.contains('expanded')) {
            this.logoutSection.classList.toggle('expanded');
            this.dropdownArrow.classList.toggle('active');
        }
    }

    handleOutsideClick(event) {
        const isClickOutside = !this.emailContainer.contains(event.target) &&
            !this.logoutSection.contains(event.target);

        if (isClickOutside) {
            this.logoutSection.classList.remove('expanded');
            this.dropdownArrow.classList.remove('active');
        }
    }

    initializeDeleteAccount() {
        this.deleteAccountBtn.addEventListener('click', () => {
            this.modalOverlay.classList.add('visible');
        });

        this.modalCancelBtn.addEventListener('click', () => {
            this.modalOverlay.classList.remove('visible');
        });

        this.modalDeleteBtn.addEventListener('click', async () => {
            try {
                this.showToast('Deleting account...');

                const response = await fetch(API_ENDPOINTS.delete_account, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                });

                const data = await response.json();

                if (response.ok) {
                    this.showToast(data.message);

                    setTimeout(() => {
                        window.location.href = API_ENDPOINTS.register;
                    }, 1500);

                } else {
                    this.showToast(data.message || 'Failed to delete account');
                    this.modalOverlay.classList.remove('visible');
                }
            } catch (error) {
                console.error('Error:', error);
                this.showToast('An unexpected error occurred');
                this.modalOverlay.classList.remove('visible');
            }
        });

        this.modalOverlay.addEventListener('click', (event) => {
            if (event.target === this.modalOverlay) {
                this.modalOverlay.classList.remove('visible');
            }
        });
    }

    initializeLogout() {
        this.logoutBtn.addEventListener('click', async (event) => {
            event.preventDefault();

            this.showToast('Logging out...');

            try {
                const response = await fetch(API_ENDPOINTS.logout, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                });

                if (response.ok) {
                    this.showToast('Logged out successfully');
                    setTimeout(() => {
                        window.location.href = response.url;
                    }, 1500);
                } else {
                    this.showToast('Failed to log out');
                }
            } catch (error) {
                console.error('Error:', error);
                this.showToast('An unexpected error occurred');
            }
        });
    }

    showToast(message) {
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            document.body.appendChild(toastContainer);
        }

        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.textContent = message;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 400);
        }, 5000);
    }
}

export function initializeSidebar() {
    return new SidebarManager();
}
