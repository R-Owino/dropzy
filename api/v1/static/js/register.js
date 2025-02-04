document.addEventListener('DOMContentLoaded', function () {
    const emailInput = document.getElementById('email');
    const validationFeedback = document.querySelector('.email-validation-feedback');

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
