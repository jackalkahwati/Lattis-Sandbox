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
        .then(response => response.json())
        .then(data => {
            document.getElementById('response').textContent = JSON.stringify(data, null, 2);
        })
        .catch(error => {
            document.getElementById('response').textContent = 'Error: ' + error;
        });
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('getVehicles').addEventListener('click', () => {
        sendRequest('/fleet/vehicles', 'GET');
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

    document.getElementById('getStations').addEventListener('click', () => {
        sendRequest('/rebalancing/stations', 'GET');
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
});
