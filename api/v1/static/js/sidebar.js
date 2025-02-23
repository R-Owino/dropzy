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
    MODAL_DELETE_BTN: '.modal-delete'
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

        this.initializeEventListeners();
        this.initializeDeleteAccount();
    }

    initializeEventListeners() {
        // Sidebar toggle functionality
        this.toggle.addEventListener('click', () => {
            this.toggleSidebar();
        });

        // Email dropdown functionality
        this.emailContainer.addEventListener('click', () => {
            this.handleEmailContainerClick();
        });

        // User icon click to expand sidebar
        const userIcon = document.querySelector('.user-icon');
        userIcon.addEventListener('click', () => {
            this.toggleSidebar();
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (event) => {
            this.handleOutsideClick(event);
        });
    }

    toggleSidebar() {
        this.sidebar.classList.toggle('expanded');
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
                const response = await fetch('/api/v1/delete-account', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    window.location.href = '/signup';
                } else {
                    console.error('Failed to delete account');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });

        this.modalOverlay.addEventListener('click', (event) => {
            if (event.target === this.modalOverlay) {
                this.modalOverlay.classList.remove('visible');
            }
        });
    }

}

// Export function to initialize sidebar
export function initializeSidebar() {
    return new SidebarManager();
}
