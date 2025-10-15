// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const goalInput = document.getElementById('goal-input');
    const resultsContainer = document.getElementById('results-container');
    const loader = document.getElementById('loader');

    generateBtn.addEventListener('click', async () => {
        const goal = goalInput.value.trim();
        if (!goal) {
            alert('Please enter a goal.');
            return;
        }

        // Show loader and clear previous results
        loader.style.display = 'block';
        resultsContainer.innerHTML = '';

        try {
            // Call our backend API
            const response = await fetch('/create-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ goal: goal }),
            });

            if (!response.ok) {
                // Try to read error body from server for a clearer message
                let errText = '';
                let errJson = null;
                try {
                    errJson = await response.json();
                    errText = errJson.error || JSON.stringify(errJson);
                } catch (e) {
                    errText = await response.text();
                }

                // Special handling for 429 (quota/rate-limit)
                if (response.status === 429) {
                    const retryAfter = errJson && errJson.retry_after ? errJson.retry_after : response.headers.get('Retry-After');
                    showRetryMessage(errText, retryAfter);
                    return; // stop further processing
                }

                throw new Error(`Server error: ${errText || response.statusText}`);
            }

            const data = await response.json();
            
            // Hide loader
            loader.style.display = 'none';

            // Display the results
            displayResults(data);

        } catch (error) {
            loader.style.display = 'none';
            resultsContainer.innerHTML = `<p style="color: red;">An error occurred: ${error.message}</p>`;
            console.error('Error:', error);
        }
    });

    function displayResults(data) {
        if (data.error) {
            resultsContainer.innerHTML = `<p style="color: red;">Error from server: ${data.error}</p>`;
            return;
        }

        // Add a title for the project
        const projectTitle = document.createElement('h2');
        projectTitle.textContent = data.project_name || 'Generated Plan';
        resultsContainer.appendChild(projectTitle);

        // Create a card for each task
        data.tasks.forEach(task => {
            const card = document.createElement('div');
            card.className = 'task-card';

            const title = document.createElement('h3');
            title.textContent = `${task.task_id}. ${task.task_name}`;

            const description = document.createElement('p');
            description.textContent = task.description;

            const meta = document.createElement('div');
            meta.className = 'meta';
            const timeline = `<strong>Timeline:</strong> ${task.timeline_days} days`;
            const dependencies = `<strong>Dependencies:</strong> ${task.dependencies.length > 0 ? task.dependencies.join(', ') : 'None'}`;
            meta.innerHTML = `${timeline} | ${dependencies}`;

            card.appendChild(title);
            card.appendChild(description);
            card.appendChild(meta);

            resultsContainer.appendChild(card);
        });
    }

    // Show a retry UI for quota errors
    function showRetryMessage(message, retryAfterSeconds) {
        loader.style.display = 'none';
        const container = document.getElementById('results-container');
        container.innerHTML = '';

        const msg = document.createElement('div');
        msg.style.color = 'orange';
        msg.style.marginBottom = '10px';
        msg.textContent = `An error occurred: ${message}`;

        const retryBtn = document.createElement('button');
        retryBtn.textContent = 'Retry';
        retryBtn.disabled = true;

        let seconds = parseInt(retryAfterSeconds) || 30;
        const countdown = document.createElement('span');
        countdown.style.marginLeft = '10px';
        countdown.textContent = ` (retry in ${seconds}s)`;

        const interval = setInterval(() => {
            seconds -= 1;
            if (seconds <= 0) {
                clearInterval(interval);
                retryBtn.disabled = false;
                countdown.textContent = '';
            } else {
                countdown.textContent = ` (retry in ${seconds}s)`;
            }
        }, 1000);

        retryBtn.addEventListener('click', () => {
            // programmatically click the generate button to retry
            document.getElementById('generate-btn').click();
        });

        container.appendChild(msg);
        container.appendChild(retryBtn);
        container.appendChild(countdown);
    }
});