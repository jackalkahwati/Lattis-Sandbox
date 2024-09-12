function sendRequest(endpoint, method, body = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    fetch(endpoint, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('response').textContent = JSON.stringify(data, null, 2);
            document.getElementById('error').textContent = '';
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('error').textContent = `Error: ${error.message}`;
            document.getElementById('response').textContent = '';
        });
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('getVehicles').addEventListener('click', () => {
        sendRequest('/fleet/vehicles', 'GET');
    });

    document.getElementById('getFleetStatus').addEventListener('click', () => {
        sendRequest('/fleet/status', 'GET');
    });

    document.getElementById('assignTask').addEventListener('click', () => {
        const body = {
            vehicle_id: 1,
            task_type: 'maintenance',
            description: 'Regular maintenance check'
        };
        sendRequest('/fleet/task', 'POST', body);
    });

    document.getElementById('getMaintenanceSchedule').addEventListener('click', () => {
        sendRequest('/maintenance/schedule', 'GET');
    });

    document.getElementById('createMaintenanceTask').addEventListener('click', () => {
        const body = {
            vehicle_id: 1,
            description: 'Regular maintenance check'
        };
        sendRequest('/maintenance/task', 'POST', body);
    });

    document.getElementById('getPredictiveMaintenance').addEventListener('click', () => {
        sendRequest('/maintenance/predictive-maintenance', 'GET');
    });

    document.getElementById('getStations').addEventListener('click', () => {
        sendRequest('/rebalancing/stations', 'GET');
    });

    document.getElementById('scheduleRebalancing').addEventListener('click', () => {
        const body = {
            from_station_id: 1,
            to_station_id: 2,
            num_bikes: 5
        };
        sendRequest('/rebalancing/task', 'POST', body);
    });

    document.getElementById('getOptimizationSuggestions').addEventListener('click', () => {
        const body = {
            time_range: 'morning'
        };
        sendRequest('/rebalancing/optimization/suggestions', 'POST', body);
    });

    document.getElementById('manageAccess').addEventListener('click', () => {
        const body = {
            username: 'john_doe',
            role: 'technician',
            action: 'grant'
        };
        sendRequest('/user/access', 'POST', body);
    });

    document.getElementById('getUserActivity').addEventListener('click', () => {
        sendRequest('/user/activity', 'GET');
    });

    document.getElementById('getUsageReport').addEventListener('click', () => {
        sendRequest('/reports/usage', 'GET');
    });

    document.getElementById('getMaintenanceReport').addEventListener('click', () => {
        sendRequest('/reports/maintenance', 'GET');
    });

    document.getElementById('ingestGBFSData').addEventListener('click', () => {
        const body = {
            gbfs_data: {
                last_updated: 1627884661,
                ttl: 0,
                data: {
                    bikes: [
                        {
                            bike_id: "bike_1",
                            lat: 37.7749,
                            lon: -122.4194,
                            is_reserved: 0,
                            is_disabled: 0
                        }
                    ]
                }
            }
        };
        sendRequest('/integration/gbfs', 'POST', body);
    });

    document.getElementById('connectRepairTicket').addEventListener('click', () => {
        const body = {
            ticket_id: 'T12345',
            customer_id: 'C6789',
            issue_description: 'Flat tire'
        };
        sendRequest('/integration/crm', 'POST', body);
    });

    document.getElementById('setDynamicPricing').addEventListener('click', () => {
        const body = {
            base_price: 2.5,
            surge_multiplier: 1.5,
            time_based_rules: {
                'peak_hours': {
                    'start': '17:00',
                    'end': '19:00',
                    'multiplier': 1.2
                }
            }
        };
        sendRequest('/future/dynamic-pricing', 'POST', body);
    });

    document.getElementById('defineGeofence').addEventListener('click', () => {
        const body = {
            zone_name: 'Downtown',
            coordinates: [
                { lat: 37.7749, lon: -122.4194 },
                { lat: 37.7750, lon: -122.4195 },
                { lat: 37.7751, lon: -122.4196 }
            ],
            rules: {
                'max_speed': 15,
                'parking_allowed': false
            }
        };
        sendRequest('/future/geofencing', 'POST', body);
    });
});
