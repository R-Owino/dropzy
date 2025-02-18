const form = document.getElementById('verification-form');
const confirmButton = document.getElementById('confirm-button');
const verificationInput = document.getElementById('verification-code');
const timeoutWarning = document.querySelector('.timeout-warning');
const timeoutCounter = document.getElementById('timeout-counter');

const API_ENDPOINTS = {
    confirm: '/api/v1/confirm',
    resend: '/api/v1/resend-verification',
    register: '/api/v1/register'
  };

// Toast notification
function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    toast.offsetHeight;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

let timeoutDuration = 5 * 60;
let timeoutTimer;

function startTimeout() {
    timeoutWarning.style.display = 'block';

    timeoutTimer = setInterval(() => {
        timeoutDuration--;
        const minutes = Math.floor(timeoutDuration / 60);
        const seconds = timeoutDuration % 60;
        timeoutCounter.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        if (timeoutDuration <= 60) {
            timeoutWarning.style.color = '#f44336';
        }

        if (timeoutDuration <= 0) {
            clearInterval(timeoutTimer);
            showToast('Session expired. Redirecting to registration page...', 'error');
            setTimeout(() => {
                window.location.href = API_ENDPOINTS.register;
            }, 2000)
        }
    }, 1000);
}

startTimeout();

form.addEventListener('submit', function (e) {
    e.preventDefault();
    confirmButton.disabled = true;

    const formData = new FormData(form);

    // Send the request
    fetch(API_ENDPOINTS.confirm, {
        method: 'POST',
        body: formData,
        headers: {
            'Accept': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showToast('Email verified successfully!', 'success');
                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 2000);
            } else {
                showToast(data.message || 'Verification failed. Please try again.', 'error');
                confirmButton.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error during verification:', error);
            showToast('An error occurred during verification. Please try again.', 'error');
            confirmButton.disabled = false;
        });
});

// handle input events
verificationInput.addEventListener('input', function (e) {
    let value = e.target.value.replace(/\D/g, '');
    value = value.slice(0, 6);
    e.target.value = value;
});

// handle pasting 
verificationInput.addEventListener('paste', function (e) {
    e.preventDefault();
    let pasteData = (e.clipboardData || window.clipboardData).getData('text');
    pasteData = pasteData.replace(/\D/g, '').slice(0, 6);
    this.value = pasteData;
});

// resendCode function
function resendCode() {
    fetch(API_ENDPOINTS.resend, {
        method: 'POST'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showToast('A new verification code has been sent to your email.', 'success');
                clearInterval(timeoutTimer);
                timeoutDuration = 5 * 60;
                startTimeout();
            } else {
                showToast(data.message || 'Failed to resend verification code.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Failed to resend verification code. Please try again.', 'error');
        });
}
