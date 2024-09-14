document.addEventListener('DOMContentLoaded', () => {
    initializeMap();
    setupDarkModeToggle();
    setupAPIInteraction();
});

let map;
let markers = [];

function initializeMap() {
    console.log('Initializing map...');
    console.log('Mapbox Access Token:', MAPBOX_ACCESS_TOKEN);

    if (!MAPBOX_ACCESS_TOKEN || MAPBOX_ACCESS_TOKEN === 'None' || MAPBOX_ACCESS_TOKEN === '{{ MAPBOX_ACCESS_TOKEN }}') {
        console.error('Mapbox access token is missing or invalid');
        document.querySelector('.map-loading').style.display = 'none';
        document.getElementById('fleet-map').innerHTML = '<p>Error: Unable to load map due to missing or invalid access token.</p>';
        return;
    }

    mapboxgl.accessToken = MAPBOX_ACCESS_TOKEN;

    try {
        map = new mapboxgl.Map({
            container: 'fleet-map',
            style: 'mapbox://styles/mapbox/streets-v11',
            center: [-122.4194, 37.7749],
            zoom: 12
        });

        map.on('load', () => {
            console.log('Map loaded successfully');
            document.querySelector('.map-loading').style.display = 'none';
            document.getElementById('fleet-map').style.visibility = 'visible';
            map.addControl(new mapboxgl.NavigationControl());
            map.addControl(new mapboxgl.FullscreenControl());
            fetchVehicles();
        });

        map.on('error', (e) => {
            console.error('Map error:', e);
            document.querySelector('.map-loading').style.display = 'none';
            document.getElementById('fleet-map').innerHTML = '<p>Error: Unable to load map. Please check your internet connection and try again.</p>';
        });
    } catch (error) {
        console.error('Error initializing map:', error);
        document.querySelector('.map-loading').style.display = 'none';
        document.getElementById('fleet-map').innerHTML = '<p>Error: Unable to initialize map. Please try refreshing the page.</p>';
    }
}

function fetchVehicles() {
    fetch('/api/map')
        .then(response => response.json())
        .then(data => {
            updateVehicleMarkers(data);
        })
        .catch(error => {
            console.error('Error fetching vehicles:', error);
        });
}

function updateVehicleMarkers(vehicles) {
    markers.forEach(marker => marker.remove());
    markers = [];

    vehicles.forEach(vehicle => {
        const el = document.createElement('div');
        el.className = 'vehicle-marker';
        el.style.backgroundColor = getVehicleColor(vehicle.status);

        const marker = new mapboxgl.Marker(el)
            .setLngLat([vehicle.lng, vehicle.lat])
            .setPopup(new mapboxgl.Popup().setHTML(`
                <h3>Vehicle ${vehicle.id}</h3>
                <p>Status: ${vehicle.status}</p>
                <p>Battery: ${vehicle.battery_level || 'N/A'}%</p>
            `))
            .addTo(map);

        markers.push(marker);
    });
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
        updateDarkModeUI();
    });

    if (localStorage.getItem('darkMode') === 'true') {
        body.classList.add('dark-mode');
    }

    updateDarkModeUI();
}

function updateDarkModeUI() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const isDarkMode = document.body.classList.contains('dark-mode');

    darkModeToggle.textContent = isDarkMode ? '🌞' : '🌓';
    darkModeToggle.setAttribute('aria-label', isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode');

    if (map) {
        map.setStyle(isDarkMode ? 'mapbox://styles/mapbox/dark-v10' : 'mapbox://styles/mapbox/streets-v11');
    }
}

function setupAPIInteraction() {
    const endpointSelect = document.getElementById('endpoint-select');
    const requestUrl = document.getElementById('request-url');
    const requestBody = document.getElementById('request-body');
    const sendRequestBtn = document.getElementById('send-request-btn');
    const responseBody = document.getElementById('response-body');

    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            populateEndpointDropdown(data.endpoints);
        })
        .catch(error => {
            console.error('Error fetching API config:', error);
            showNotification('Failed to load API endpoints.', 'error');
        });

    function populateEndpointDropdown(endpoints) {
        endpointSelect.innerHTML = '<option value="">Select an endpoint</option>';
        
        for (const [category, endpointList] of Object.entries(endpoints)) {
            const optgroup = document.createElement('optgroup');
            optgroup.label = category;
            
            endpointList.forEach(endpoint => {
                const option = document.createElement('option');
                option.value = JSON.stringify(endpoint);
                option.textContent = `${endpoint.method} ${endpoint.path}`;
                optgroup.appendChild(option);
            });
            
            endpointSelect.appendChild(optgroup);
        }
    }

    endpointSelect.addEventListener('change', (e) => {
        if (e.target.value) {
            const endpoint = JSON.parse(e.target.value);
            selectEndpoint(endpoint);
        }
    });

    sendRequestBtn.addEventListener('click', sendRequest);

    function selectEndpoint(endpoint) {
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

    function sendRequest() {
        const selectedEndpoint = JSON.parse(endpointSelect.value);
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
            responseBody.textContent = JSON.stringify(data, null, 2);
            highlightCode();
            showNotification('Request completed successfully.', 'success');
        })
        .catch(error => {
            responseBody.textContent = `Error: ${error.message}`;
            showNotification('An error occurred while sending the request.', 'error');
        });
    }
}

function showNotification(message, type = 'info') {
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
