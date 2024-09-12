document.addEventListener('DOMContentLoaded', () => {
    initializeMap();
    setupDarkModeToggle();
    setupAPIInteraction();
    setupHelpModal();
    updateDashboard();
});

function initializeMap() {
    mapboxgl.accessToken = MAPBOX_ACCESS_TOKEN;
    const map = new mapboxgl.Map({
        container: 'fleet-map',
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [-122.4194, 37.7749],
        zoom: 12
    });

    // Add markers for sample vehicles
    const vehicles = [
        { id: 1, coordinates: [-122.4194, 37.7749], status: 'active' },
        { id: 2, coordinates: [-122.4099, 37.7850], status: 'maintenance' },
        { id: 3, coordinates: [-122.4289, 37.7648], status: 'inactive' },
    ];

    vehicles.forEach(vehicle => {
        const el = document.createElement('div');
        el.className = 'vehicle-marker';
        el.style.backgroundColor = getVehicleColor(vehicle.status);
        el.style.width = '20px';
        el.style.height = '20px';
        el.style.borderRadius = '50%';
        el.style.border = '2px solid white';

        new mapboxgl.Marker(el)
            .setLngLat(vehicle.coordinates)
            .setPopup(new mapboxgl.Popup().setHTML(`Vehicle ${vehicle.id}<br>Status: ${vehicle.status}`))
            .addTo(map);
    });

    // Add zoom and rotation controls
    map.addControl(new mapboxgl.NavigationControl());

    // Add fullscreen control
    map.addControl(new mapboxgl.FullscreenControl());
}

function getVehicleColor(status) {
    switch (status) {
        case 'active': return '#22c55e';
        case 'maintenance': return '#eab308';
        case 'inactive': return '#ef4444';
        default: return '#3b82f6';
    }
}

function setupDarkModeToggle() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const body = document.body;

    darkModeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', body.classList.contains('dark-mode'));
        darkModeToggle.textContent = body.classList.contains('dark-mode') ? '🌞' : '🌓';
        darkModeToggle.setAttribute('aria-label', body.classList.contains('dark-mode') ? 'Switch to Light Mode' : 'Switch to Dark Mode');
    });

    if (localStorage.getItem('darkMode') === 'true') {
        body.classList.add('dark-mode');
        darkModeToggle.textContent = '🌞';
        darkModeToggle.setAttribute('aria-label', 'Switch to Light Mode');
    }
}

function setupAPIInteraction() {
    const endpointList = document.getElementById('endpoint-list');
    const endpointSearch = document.getElementById('endpoint-search');
    const accessTokenInput = document.getElementById('access-token');
    const generateTestTokenBtn = document.getElementById('generate-test-token-btn');
    const sendRequestBtn = document.getElementById('send-request-btn');
    const requestUrl = document.getElementById('request-url');
    const requestBody = document.getElementById('request-body');
    const responseBody = document.getElementById('response-body');
    const loadingSpinner = document.getElementById('loading-spinner');

    generateTestTokenBtn.addEventListener('click', generateTestToken);
    sendRequestBtn.addEventListener('click', sendRequest);
    endpointSearch.addEventListener('input', filterEndpoints);

    // Populate endpoint list
    const endpoints = getAllEndpoints();
    endpoints.forEach(endpoint => {
        const endpointItem = createEndpointItem(endpoint);
        endpointList.appendChild(endpointItem);
    });

    function createEndpointItem(endpoint) {
        const item = document.createElement('div');
        item.className = 'endpoint-item';
        item.innerHTML = `
            <h3>${endpoint.method} ${endpoint.path}</h3>
            <p>${endpoint.description}</p>
            <button class="select-endpoint-btn">Select</button>
        `;
        item.querySelector('.select-endpoint-btn').addEventListener('click', () => selectEndpoint(endpoint));
        return item;
    }

    function selectEndpoint(endpoint) {
        requestUrl.textContent = `${endpoint.method} ${endpoint.path}`;
        requestBody.textContent = JSON.stringify(endpoint.sampleBody || {}, null, 2);
        highlightCode();
    }

    function filterEndpoints() {
        const searchTerm = endpointSearch.value.toLowerCase();
        const endpointItems = endpointList.querySelectorAll('.endpoint-item');
        
        endpointItems.forEach(item => {
            const endpointText = item.textContent.toLowerCase();
            if (endpointText.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    function highlightCode() {
        hljs.highlightElement(requestBody);
        hljs.highlightElement(responseBody);
    }

    function generateTestToken() {
        fetch('/api/v1/auth/generate-test-token', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            accessTokenInput.value = data.test_token;
            showNotification('Test API Access Token generated successfully.', 'success');
        })
        .catch(error => {
            showNotification('Failed to generate Test API Access Token.', 'error');
        });
    }

    function sendRequest() {
        const accessToken = accessTokenInput.value;
        const url = requestUrl.textContent.split(' ')[1];
        const method = requestUrl.textContent.split(' ')[0];

        if (!url || !accessToken) {
            showNotification('Please select an endpoint and enter an access token.', 'error');
            return;
        }

        showNotification('Sending request...', 'info');
        loadingSpinner.style.display = 'block';
        responseBody.style.opacity = '0.5';

        let body;
        try {
            body = JSON.parse(requestBody.textContent);
        } catch (error) {
            showNotification('Invalid JSON in request body.', 'error');
            loadingSpinner.style.display = 'none';
            responseBody.style.opacity = '1';
            return;
        }

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: method !== 'GET' ? JSON.stringify(body) : undefined
        })
        .then(response => response.json())
        .then(data => {
            responseBody.textContent = JSON.stringify(data, null, 2);
            highlightCode();
            showNotification('Request completed successfully.', 'success');
        })
        .catch(error => {
            responseBody.textContent = `Error: ${error.message}`;
            showNotification('An error occurred while sending the request.', 'error');
        })
        .finally(() => {
            loadingSpinner.style.display = 'none';
            responseBody.style.opacity = '1';
        });
    }
}

function getAllEndpoints() {
    return [
        {
            method: 'GET',
            path: '/api/v1/fleet/vehicles',
            description: 'Get all vehicles',
            sampleBody: {}
        },
        {
            method: 'POST',
            path: '/api/v1/fleet/vehicles',
            description: 'Create a new vehicle',
            sampleBody: {
                "name": "Vehicle 1",
                "type": "car",
                "status": "active"
            }
        },
        {
            method: 'GET',
            path: '/api/v1/maintenance/tasks',
            description: 'Get all maintenance tasks',
            sampleBody: {}
        },
        {
            method: 'POST',
            path: '/api/v1/maintenance/tasks',
            description: 'Create a new maintenance task',
            sampleBody: {
                "vehicle_id": 1,
                "description": "Oil change",
                "due_date": "2024-10-01"
            }
        },
        {
            method: 'GET',
            path: '/api/v1/rebalancing/stations',
            description: 'Get all stations',
            sampleBody: {}
        },
        {
            method: 'POST',
            path: '/api/v1/rebalancing/task',
            description: 'Schedule a rebalancing task',
            sampleBody: {
                "from_station_id": 1,
                "to_station_id": 2,
                "num_bikes": 5
            }
        },
        {
            method: 'GET',
            path: '/api/v1/user/activity',
            description: 'Get user activity logs',
            sampleBody: {}
        },
        {
            method: 'POST',
            path: '/api/v1/user/access',
            description: 'Manage user access',
            sampleBody: {
                "username": "john_doe",
                "role": "admin",
                "action": "grant"
            }
        }
    ];
}

function setupHelpModal() {
    const modal = document.getElementById('help-modal');
    const btn = document.getElementById('help-button');
    const closeBtn = modal.querySelector('.close');

    btn.onclick = function() {
        modal.style.display = 'block';
        modal.setAttribute('aria-hidden', 'false');
    }

    closeBtn.onclick = function() {
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
        }
    }
}

function updateDashboard() {
    // This function should fetch real data from your API
    // For now, we'll use placeholder data
    document.getElementById('total-vehicles').textContent = '150';
    document.getElementById('active-trips').textContent = '42';
    document.getElementById('maintenance-tasks').textContent = '7';
    document.getElementById('revenue-today').textContent = '$3,250';
}

function showNotification(message, type = 'info') {
    const notificationArea = document.getElementById('notification-area');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.setAttribute('role', 'alert');
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
