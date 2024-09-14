console.log('main.js is loaded and executing');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded');
    initializeMap();
    setupDarkModeToggle();
    setupAPIInteraction();
});

function initializeMap() {
    console.log('Initializing map...');
    const mapElement = document.getElementById('fleet-map');
    if (!mapElement) {
        console.error('Map element not found');
        return;
    }
    // ... rest of the map initialization code
}

function setupDarkModeToggle() {
    console.log('Setting up dark mode toggle...');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const body = document.body;

    if (!darkModeToggle) {
        console.error('Dark mode toggle checkbox not found');
        return;
    }

    // Set initial state based on localStorage
    if (localStorage.getItem('darkMode') === 'true') {
        body.classList.add('dark-mode');
        darkModeToggle.checked = true;
    }

    darkModeToggle.addEventListener('change', () => {
        if (darkModeToggle.checked) {
            body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'true');
        } else {
            body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'false');
        }
        updateDarkModeUI();
    });

    updateDarkModeUI();
}

function updateDarkModeUI() {
    const isDarkMode = document.body.classList.contains('dark-mode');

    if (window.map) {
        window.map.setStyle(isDarkMode ? 'mapbox://styles/mapbox/dark-v10' : 'mapbox://styles/mapbox/streets-v11');
    }
}

function setupAPIInteraction() {
    console.log('Setting up API interaction...');
    const apiDropdownsContainer = document.getElementById('api-dropdowns');
    const requestUrl = document.getElementById('request-url');
    const requestBody = document.getElementById('request-body');
    const sendRequestBtn = document.getElementById('send-request-btn');
    const responseBody = document.getElementById('response-body');

    if (!apiDropdownsContainer) {
        console.error('API dropdowns container not found');
        return;
    }

    if (!requestUrl || !requestBody || !sendRequestBtn || !responseBody) {
        console.error('One or more required elements not found');
        return;
    }

    fetch('/api/config')
        .then(response => {
            console.log('API config response received');
            return response.json();
        })
        .then(data => {
            console.log('API config data:', data);
            createApiDropdowns(data.endpoints);
        })
        .catch(error => {
            console.error('Error fetching API config:', error);
            showNotification('Failed to load API endpoints.', 'error');
        });

    function createApiDropdowns(endpoints) {
        console.log('Creating API dropdowns...');
        apiDropdownsContainer.innerHTML = ''; // Clear existing dropdowns

        for (const [category, endpointList] of Object.entries(endpoints)) {
            console.log(`Creating dropdown for category: ${category}`);
            const dropdownContainer = document.createElement('div');
            dropdownContainer.className = 'api-dropdown-container';

            const label = document.createElement('label');
            label.textContent = category;
            label.htmlFor = `api-dropdown-${category.toLowerCase().replace(/\s+/g, '-')}`;

            const select = document.createElement('select');
            select.id = `api-dropdown-${category.toLowerCase().replace(/\s+/g, '-')}`;
            select.className = 'api-dropdown';

            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = `Select ${category} Endpoint`;
            select.appendChild(defaultOption);

            endpointList.forEach(endpoint => {
                const option = document.createElement('option');
                option.value = JSON.stringify(endpoint);
                option.textContent = `${endpoint.method} ${endpoint.path}`;
                select.appendChild(option);
            });

            select.addEventListener('change', (e) => {
                if (e.target.value) {
                    const endpoint = JSON.parse(e.target.value);
                    selectEndpoint(endpoint);
                }
            });

            dropdownContainer.appendChild(label);
            dropdownContainer.appendChild(select);
            apiDropdownsContainer.appendChild(dropdownContainer);
        }
        console.log('API dropdowns created');
    }

    function selectEndpoint(endpoint) {
        console.log('Selected endpoint:', endpoint);
        requestUrl.textContent = `${endpoint.method} ${endpoint.path}`;
        requestBody.textContent = endpoint.method !== 'GET' ? '{\n  \n}' : '{}';
        highlightCode();
    }

    function highlightCode() {
        if (window.hljs) {
            hljs.highlightElement(requestBody);
            hljs.highlightElement(responseBody);
        }
    }

    sendRequestBtn.addEventListener('click', sendRequest);

    function sendRequest() {
        console.log('Sending request...');
        const selectedDropdown = document.querySelector('.api-dropdown:not(:invalid)');
        if (!selectedDropdown) {
            showNotification('Please select an endpoint before sending a request.', 'error');
            return;
        }

        const selectedEndpoint = JSON.parse(selectedDropdown.value);
        const url = selectedEndpoint.path;
        const method = selectedEndpoint.method;
        let body;

        try {
            body = JSON.parse(requestBody.textContent);
        } catch (error) {
            showNotification('Invalid JSON in request body.', 'error');
            return;
        }

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: method !== 'GET' ? JSON.stringify(body) : undefined
        })
        .then(response => response.json())
        .then(data => {
            console.log('Response received:', data);
            responseBody.textContent = JSON.stringify(data, null, 2);
            highlightCode();
            showNotification('Request completed successfully.', 'success');
        })
        .catch(error => {
            console.error('Error sending request:', error);
            responseBody.textContent = `Error: ${error.message}`;
            showNotification('An error occurred while sending the request.', 'error');
        });
    }
}

function showNotification(message, type = 'info') {
    console.log(`Showing notification: ${message} (${type})`);
    const notificationArea = document.getElementById('notification-area');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notificationArea.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notificationArea.removeChild(notification);
        }, 300);
    }, 3000);
}
