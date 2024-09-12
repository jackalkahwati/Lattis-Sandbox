// Global variables
let map;
let vehicles = [
    { id: 1, x: 100, y: 150, status: 'active' },
    { id: 2, x: 300, y: 200, status: 'maintenance' },
    { id: 3, x: 200, y: 300, status: 'inactive' },
    { id: 4, x: 400, y: 100, status: 'active' },
];

let charts = {};
let zoom = 1;
let panX = 0;
let panY = 0;

function initializeMap() {
    try {
        const mapContainer = document.getElementById('fleet-map');
        if (!mapContainer) {
            throw new Error('Map container not found');
        }

        const mapSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        mapSvg.setAttribute('width', '100%');
        mapSvg.setAttribute('height', '100%');
        mapSvg.setAttribute('viewBox', '0 0 1000 800');

        // Background
        const background = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        background.setAttribute('width', '1000');
        background.setAttribute('height', '800');
        background.setAttribute('fill', '#e6e8e6');
        mapSvg.appendChild(background);

        // Water bodies
        const water = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        water.setAttribute('d', 'M0 600 Q 250 550, 500 600 T 1000 600 V 800 H 0 Z');
        water.setAttribute('fill', '#a5d5f5');
        mapSvg.appendChild(water);

        // Roads
        const roads = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        roads.setAttribute('stroke', '#ffffff');
        roads.setAttribute('stroke-width', '20');

        const roadPaths = [
            'M0 200 H1000', 'M0 400 H1000', 'M0 600 H1000',
            'M200 0 V800', 'M500 0 V800', 'M800 0 V800'
        ];

        roadPaths.forEach(path => {
            const road = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            road.setAttribute('d', path);
            roads.appendChild(road);
        });

        mapSvg.appendChild(roads);

        // Add vehicles
        const vehiclesGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        vehicles.forEach(vehicle => {
            const vehicleGroup = createVehicleElement(vehicle);
            vehiclesGroup.appendChild(vehicleGroup);
        });

        mapSvg.appendChild(vehiclesGroup);

        mapContainer.appendChild(mapSvg);
        map = mapSvg;  // Store the map for later use

        // Add zoom and pan functionality
        mapSvg.addEventListener('wheel', handleZoom);
        mapSvg.addEventListener('mousedown', startPan);
        mapSvg.addEventListener('mousemove', pan);
        mapSvg.addEventListener('mouseup', endPan);
        mapSvg.addEventListener('mouseleave', endPan);

        // Add zoom buttons
        addZoomButtons(mapContainer);

    } catch (error) {
        console.error('Error initializing map:', error);
        showNotification('Error initializing map. Please try refreshing the page.');
    }
}

function createVehicleElement(vehicle) {
    const vehicleGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    vehicleGroup.setAttribute('class', 'vehicle');
    vehicleGroup.setAttribute('data-id', vehicle.id);

    const vehicleCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    vehicleCircle.setAttribute('cx', vehicle.x);
    vehicleCircle.setAttribute('cy', vehicle.y);
    vehicleCircle.setAttribute('r', '10');
    vehicleCircle.setAttribute('fill', getVehicleColor(vehicle.status));

    const vehicleLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    vehicleLabel.setAttribute('x', vehicle.x);
    vehicleLabel.setAttribute('y', vehicle.y + 5);
    vehicleLabel.setAttribute('text-anchor', 'middle');
    vehicleLabel.setAttribute('fill', '#ffffff');
    vehicleLabel.setAttribute('font-size', '10');
    vehicleLabel.textContent = vehicle.id;

    vehicleGroup.appendChild(vehicleCircle);
    vehicleGroup.appendChild(vehicleLabel);

    // Add tooltip
    const tooltip = document.createElementNS('http://www.w3.org/2000/svg', 'title');
    tooltip.textContent = `Vehicle ${vehicle.id} - Status: ${vehicle.status}`;
    vehicleGroup.appendChild(tooltip);

    // Make vehicle draggable
    vehicleGroup.addEventListener('mousedown', startDrag);
    vehicleGroup.addEventListener('mousemove', drag);
    vehicleGroup.addEventListener('mouseup', endDrag);
    vehicleGroup.addEventListener('mouseleave', endDrag);

    return vehicleGroup;
}

function getVehicleColor(status) {
    switch (status) {
        case 'active': return '#22c55e';
        case 'maintenance': return '#eab308';
        case 'inactive': return '#ef4444';
        default: return '#3b82f6';
    }
}

function handleZoom(event) {
    event.preventDefault();
    const delta = event.deltaY;
    if (delta > 0) {
        zoom *= 0.9;
    } else {
        zoom *= 1.1;
    }
    zoom = Math.min(Math.max(0.5, zoom), 3);
    updateMapTransform();
}

function startPan(event) {
    map.setAttribute('data-panning', 'true');
    map.setAttribute('data-pan-x', event.clientX);
    map.setAttribute('data-pan-y', event.clientY);
}

function pan(event) {
    if (map.getAttribute('data-panning') !== 'true') return;
    const dx = event.clientX - parseFloat(map.getAttribute('data-pan-x'));
    const dy = event.clientY - parseFloat(map.getAttribute('data-pan-y'));
    panX += dx / zoom;
    panY += dy / zoom;
    updateMapTransform();
    map.setAttribute('data-pan-x', event.clientX);
    map.setAttribute('data-pan-y', event.clientY);
}

function endPan() {
    map.setAttribute('data-panning', 'false');
}

function updateMapTransform() {
    const viewBox = map.viewBox.baseVal;
    viewBox.x = 500 - 500 * zoom + panX;
    viewBox.y = 400 - 400 * zoom + panY;
    viewBox.width = 1000 * zoom;
    viewBox.height = 800 * zoom;
}

function addZoomButtons(container) {
    const zoomInButton = document.createElement('button');
    zoomInButton.textContent = '+';
    zoomInButton.className = 'zoom-button zoom-in';
    zoomInButton.addEventListener('click', () => {
        zoom *= 1.1;
        zoom = Math.min(zoom, 3);
        updateMapTransform();
    });

    const zoomOutButton = document.createElement('button');
    zoomOutButton.textContent = '-';
    zoomOutButton.className = 'zoom-button zoom-out';
    zoomOutButton.addEventListener('click', () => {
        zoom *= 0.9;
        zoom = Math.max(zoom, 0.5);
        updateMapTransform();
    });

    container.appendChild(zoomInButton);
    container.appendChild(zoomOutButton);
}

let isDragging = false;
let draggedVehicle = null;

function startDrag(event) {
    isDragging = true;
    draggedVehicle = event.currentTarget;
    draggedVehicle.setAttribute('data-x', event.clientX);
    draggedVehicle.setAttribute('data-y', event.clientY);
}

function drag(event) {
    if (!isDragging) return;
    event.preventDefault();
    const dx = event.clientX - parseFloat(draggedVehicle.getAttribute('data-x'));
    const dy = event.clientY - parseFloat(draggedVehicle.getAttribute('data-y'));
    const vehicleId = draggedVehicle.getAttribute('data-id');
    const vehicle = vehicles.find(v => v.id === parseInt(vehicleId));
    vehicle.x += dx / zoom;
    vehicle.y += dy / zoom;
    updateVehiclePosition(draggedVehicle, vehicle);
    draggedVehicle.setAttribute('data-x', event.clientX);
    draggedVehicle.setAttribute('data-y', event.clientY);
}

function endDrag() {
    isDragging = false;
    draggedVehicle = null;
}

function updateVehiclePosition(vehicleElement, vehicle) {
    const circle = vehicleElement.querySelector('circle');
    const text = vehicleElement.querySelector('text');
    circle.setAttribute('cx', vehicle.x);
    circle.setAttribute('cy', vehicle.y);
    text.setAttribute('x', vehicle.x);
    text.setAttribute('y', vehicle.y + 5);
}

// ... (rest of the code remains unchanged)

function setupApiTestingInterface() {
    const endpointSelect = document.getElementById('endpoint-select');
    const sendRequestBtn = document.getElementById('send-request');
    const requestBody = document.getElementById('request-body');
    const responseBody = document.getElementById('response-body');
    const saveRequestBtn = document.getElementById('save-request');
    const loadRequestBtn = document.getElementById('load-request');
    const endpointSearch = document.getElementById('endpoint-search');

    // Populate endpoint select
    const endpoints = [
        { value: 'get-vehicles', label: 'GET /api/vehicles' },
        { value: 'create-task', label: 'POST /api/tasks' },
        { value: 'update-vehicle', label: 'PUT /api/vehicles/{id}' },
        { value: 'get-stats', label: 'GET /api/stats' },
    ];

    function populateEndpoints(endpoints) {
        endpointSelect.innerHTML = '<option value="">Select an endpoint</option>';
        endpoints.forEach(endpoint => {
            const option = document.createElement('option');
            option.value = endpoint.value;
            option.textContent = endpoint.label;
            endpointSelect.appendChild(option);
        });
    }

    populateEndpoints(endpoints);

    // Endpoint search functionality
    endpointSearch.addEventListener('input', (event) => {
        const searchTerm = event.target.value.toLowerCase();
        const filteredEndpoints = endpoints.filter(endpoint => 
            endpoint.label.toLowerCase().includes(searchTerm)
        );
        populateEndpoints(filteredEndpoints);
    });

    // Handle send request
    sendRequestBtn.addEventListener('click', () => {
        const selectedEndpoint = endpointSelect.value;
        let url, method;

        switch (selectedEndpoint) {
            case 'get-vehicles':
                url = '/api/vehicles';
                method = 'GET';
                break;
            case 'create-task':
                url = '/api/tasks';
                method = 'POST';
                break;
            case 'update-vehicle':
                url = '/api/vehicles/1'; // Assuming we're updating vehicle with id 1
                method = 'PUT';
                break;
            case 'get-stats':
                url = '/api/stats';
                method = 'GET';
                break;
            default:
                showNotification('Please select an endpoint');
                return;
        }

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: method !== 'GET' ? requestBody.value : undefined,
        })
        .then(response => response.json())
        .then(data => {
            responseBody.textContent = JSON.stringify(data, null, 2);
            hljs.highlightBlock(responseBody);
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('An error occurred while sending the request');
        });
    });

    // Save request
    saveRequestBtn.addEventListener('click', () => {
        const requestData = {
            endpoint: endpointSelect.value,
            body: requestBody.value
        };
        localStorage.setItem('savedRequest', JSON.stringify(requestData));
        showNotification('Request saved successfully');
    });

    // Load request
    loadRequestBtn.addEventListener('click', () => {
        const savedRequest = JSON.parse(localStorage.getItem('savedRequest'));
        if (savedRequest) {
            endpointSelect.value = savedRequest.endpoint;
            requestBody.value = savedRequest.body;
            showNotification('Request loaded successfully');
        } else {
            showNotification('No saved request found');
        }
    });
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

document.addEventListener('DOMContentLoaded', () => {
    try {
        initializeMap();
        setupRealTimeUpdates();
        initializeCharts();
        setupApiTestingInterface();

        // Update charts periodically
        setInterval(updateCharts, 5000);

        // Set up dark mode toggle
        const darkModeToggle = document.getElementById('dark-mode-toggle');
        if (darkModeToggle) {
            darkModeToggle.addEventListener('click', toggleDarkMode);
            
            // Check for saved dark mode preference
            if (localStorage.getItem('darkMode') === 'true') {
                document.body.classList.add('dark-mode');
            }
        }

        // Initialize syntax highlighting
        hljs.highlightAll();
    } catch (error) {
        console.error('Error initializing application:', error);
        showNotification('Error initializing application. Please try refreshing the page.');
    }
});
