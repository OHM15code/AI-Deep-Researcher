document.addEventListener('DOMContentLoaded', () => {
    const topicInput = document.getElementById('topicInput');
    const generateBtn = document.getElementById('generateBtn');
    const statusSection = document.getElementById('statusSection');
    const statusMsg = document.getElementById('statusMsg');
    const resultSection = document.getElementById('resultSection');
    const searchSection = document.querySelector('.search-section');
    const resetBtn = document.getElementById('resetBtn');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.querySelector('.spinner');

    let pollInterval = null;

    const startPolling = () => {
        pollInterval = setInterval(async () => {
            try {
                const response = await fetch('/status');
                const data = await response.json();

                statusMsg.textContent = data.message;

                if (data.status === 'completed') {
                    stopPolling();
                    showResult();
                } else if (data.status === 'error') {
                    stopPolling();
                    alert(data.message);
                    resetUI();
                }
            } catch (err) {
                console.error('Polling error:', err);
            }
        }, 2000);
    };

    const stopPolling = () => {
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
    };

    const resetUI = () => {
        searchSection.classList.remove('hidden');
        statusSection.classList.add('hidden');
        resultSection.classList.add('hidden');
        generateBtn.disabled = false;
        btnText.classList.remove('hidden');
        spinner.classList.add('hidden');
        topicInput.value = '';
    };

    const showProcessing = () => {
        searchSection.classList.add('hidden');
        statusSection.classList.remove('hidden');
        resultSection.classList.add('hidden');
    };

    const showResult = () => {
        searchSection.classList.add('hidden');
        statusSection.classList.add('hidden');
        resultSection.classList.remove('hidden');
    };

    generateBtn.addEventListener('click', async () => {
        const topic = topicInput.value.trim();
        if (!topic) {
            alert('Please enter a topic.');
            return;
        }

        try {
            generateBtn.disabled = true;
            btnText.classList.add('hidden');
            spinner.classList.remove('hidden');

            const response = await fetch('/research', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ topic })
            });

            if (response.ok) {
                showProcessing();
                startPolling();
            } else {
                const data = await response.json();
                alert(data.detail || 'Failed to start research.');
                generateBtn.disabled = false;
                btnText.classList.remove('hidden');
                spinner.classList.add('hidden');
            }
        } catch (err) {
            console.error('Error:', err);
            alert('An error occurred.');
            generateBtn.disabled = false;
            btnText.classList.remove('hidden');
            spinner.classList.add('hidden');
        }
    });

    resetBtn.addEventListener('click', resetUI);
});
