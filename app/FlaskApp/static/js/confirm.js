const form = document.getElementById('verification-form');
const confirmButton = document.getElementById('confirm-button');
const verificationInput = document.getElementById('verification-code');

form.addEventListener('submit', function (e) {
    e.preventDefault();

    // Disable the form while processing
    confirmButton.disabled = true;

    // Create FormData from the form
    const formData = new FormData(form);

    // Send the request
    fetch(form.action, {
        method: 'POST',
        body: formData,
        // Add headers to ensure proper JSON handling
        headers: {
            'Accept': 'application/json'
        }
    })
        .then(response => {
            // First check if the response is ok
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            // Then parse the JSON
            return response.json();
        })
        .then(data => {

            if (data.success) {
                // Show success message first
                alert('Email verified successfully!');

                // redirect with a slight delay to ensure the alert is shown
                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 10);
            } else {
                // Handle error case
                alert(data.message || 'Verification failed. Please try again.');
                confirmButton.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error during verification:', error);
            alert('An error occurred during verification. Please try again.');
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
    fetch("{{ url_for('resend.resend_verification') }}", {
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
                alert('A new verification code has been sent to your email.');
            } else {
                alert(data.message || 'Failed to resend verification code.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to resend verification code. Please try again.');
        });
}
