// API Base URL
const API_BASE_URL = '/api/v1';

document.addEventListener('DOMContentLoaded', function () {
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const validationFeedback = document.querySelector('.email-validation-feedback');
    const requirementsDiv = document.getElementById('password-requirements');
    const form = document.querySelector('form');

    // handle email validation display
    emailInput.addEventListener('focus', () => {
        validationFeedback.style.display = 'block';
        setTimeout(() => validationFeedback.classList.add('visible'), 10);
    });

    emailInput.addEventListener('blur', (e) => {
        if (!e.relatedTarget?.closest('.email-validation-feedback')) {
            validationFeedback.classList.remove('visible');
            setTimeout(() => {
                if (!validationFeedback.classList.contains('visible')) {
                    validationFeedback.style.display = 'none';
                }
            }, 300);
        }
    });

    // handle password requirements display
    passwordInput.addEventListener('focus', () => {
        requirementsDiv.style.display = 'block';
        passwordInput.closest('.input-group').classList.add('active');
    });

    passwordInput.addEventListener('blur', (e) => {
        if (!e.relatedTarget?.closest('.password-requirements')) {
            requirementsDiv.style.display = 'none';
            passwordInput.closest('.input-group').classList.remove('active');
        }
    });
    // form submission and validation
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(e.target);

        try {
            const response = await fetch(`${API_BASE_URL}/register`, {
                method: 'POST',
                body: formData
            });

            if (response.redirected) {
                window.location.href = response.url;
            } else {
                const data = await response.json();
            
                if (response.status === 409) {
                    showToast(data.message);
                } else {
                    showToast(data.message);
                }
            }

        } catch (error) {
            console.error('Registration error:', error);
            showToast('An error occurred. Please try again.');
        }
    });

    function showToast(message) {
        const toast = document.getElementById('errorToast');
        toast.textContent = message;
        toast.style.display = 'block';
        toast.style.animation = 'none';
        void toast.offsetWidth;
        toast.style.animation = 'slideIn 0.5s, fadeOut 0.5s 2.5s';

        toast.addEventListener('animationend', (e) => {
            if (e.animationName === 'fadeOut') {
                toast.style.display = 'none';
            }
        });
    }

    // email validation patterns
    const emailPatterns = {
        format: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        domain: /\.(com|net|org|edu|gov|mil|info|io|co|[a-z]{2})$/i,
        length: (email) => email.length >= 5 && email.length <= 50,
        special: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    };

    function validateEmail(email) {
        const results = {
            format: emailPatterns.format.test(email),
            domain: emailPatterns.domain.test(email),
            length: emailPatterns.length(email),
            special: emailPatterns.special.test(email)
        };

        return {
            isValid: Object.values(results).every(Boolean),
            results
        };
    }

    function updateValidationUI(validationResults) {
        Object.entries(validationResults.results).forEach(([check, isValid]) => {
            const element = document.querySelector(`[data-check="${check}"]`);
            element.classList.remove('valid', 'invalid');
            element.classList.add(isValid ? 'valid' : 'invalid');
        });

        emailInput.classList.remove('valid-email', 'invalid-email');
        if (validationResults.isValid) {
            emailInput.classList.add('valid-email');
        } else if (emailInput.value) {
            emailInput.classList.add('invalid-email');
        }
    }

    // Event listeners
    emailInput.addEventListener('focus', () => {
        validationFeedback.classList.add('visible');
    });

    emailInput.addEventListener('input', (e) => {
        const validationResults = validateEmail(e.target.value);
        updateValidationUI(validationResults);
    });

    // Form submission validation
    document.querySelector('form').addEventListener('submit', (e) => {
        const validationResults = validateEmail(emailInput.value);
        if (!validationResults.isValid) {
            e.preventDefault();
            validationFeedback.classList.add('visible');
            emailInput.focus();
        }
    });
});

const passwordInput = document.getElementById('password');
const requirementsDiv = document.getElementById('password-requirements');

passwordInput.addEventListener('focus', () => {
    requirementsDiv.style.display = 'block';
});

// check password requirements as the user types
passwordInput.addEventListener('input', () => {
    const password = passwordInput.value;

    const requirements = {
        'length-check': password.length >= 8,
        'uppercase-check': /[A-Z]/.test(password),
        'lowercase-check': /[a-z]/.test(password),
        'number-check': /\d/.test(password),
        'special-check': /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    for (const [id, passes] of Object.entries(requirements)) {
        const element = document.getElementById(id);
        if (passes) {
            element.innerHTML = '✓ ' + element.innerHTML.slice(2);
            element.classList.add('requirement-met');
        } else {
            element.innerHTML = '✗ ' + element.innerHTML.slice(2);
            element.classList.remove('requirement-met');
        }
    }
});

// validate all requirements before form submission
document.querySelector('form').addEventListener('submit', (e) => {
    const password = passwordInput.value;
    const allRequirementsMet =
        password.length >= 8 &&
        /[A-Z]/.test(password) &&
        /[a-z]/.test(password) &&
        /\d/.test(password) &&
        /[!@#$%^&*(),.?":{}|<>]/.test(password);

    if (!allRequirementsMet) {
        e.preventDefault();
        requirementsDiv.style.display = 'block';
        alert('Please ensure all password requirements are met.');
    }
});
