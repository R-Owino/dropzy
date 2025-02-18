const API_BASE_URL = '/api/v1';

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'test/html'
            }
        });

        if (response.redirected) {
            window.location.href = response.url;
        } else {
            const toast = document.getElementById('errorToast');
            toast.style.display = 'block';

            setTimeout(() => {
                toast.style.display = 'none';
            }, 3000);
        }
    } catch (error) {
        console.error('Login error:', error);
    }
});
