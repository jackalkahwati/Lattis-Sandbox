import json
from datetime import datetime

class DataStore:
    def __init__(self, use_in_memory=True):
        self.use_in_memory = use_in_memory
        if use_in_memory:
            self.vehicles = []
            self.fleets = []
            self.trips = []
            self.users = []
            self.maintenance_tasks = []
            self.reports = []
        else:
            # In the future, this could be replaced with API calls to your existing system
            pass

    # User Authentication & Authorization
    def register_user(self, user_data):
        if self.use_in_memory:
            user_data['id'] = len(self.users) + 1
            self.users.append(user_data)
            return user_data
        else:
            return self._mock_api_call('POST', '/api/v1/auth/register', user_data)

    def login_user(self, credentials):
        if self.use_in_memory:
            # For demo purposes, just return success
            return {"message": "Login successful"}
        else:
            return self._mock_api_call('POST', '/api/v1/auth/login', credentials)

    def logout_user(self):
        if self.use_in_memory:
            return {"message": "Logout successful"}
        else:
            return self._mock_api_call('POST', '/api/v1/auth/logout')

    def get_current_user(self):
        if self.use_in_memory:
            # For demo purposes, return a mock user
            return {"id": 1, "username": "demo_user"}
        else:
            return self._mock_api_call('GET', '/api/v1/auth/me')

    # Vehicle Management
    def get_vehicles(self):
        if self.use_in_memory:
            return self.vehicles
        else:
            return self._mock_api_call('GET', '/api/v1/vehicles')

    def add_vehicle(self, vehicle):
        if self.use_in_memory:
            vehicle['id'] = len(self.vehicles) + 1
            self.vehicles.append(vehicle)
            return vehicle
        else:
            return self._mock_api_call('POST', '/api/v1/vehicles', vehicle)

    def get_vehicle(self, id):
        if self.use_in_memory:
            return next((v for v in self.vehicles if v['id'] == id), None)
        else:
            return self._mock_api_call('GET', f'/api/v1/vehicles/{id}')

    def update_vehicle(self, id, vehicle_data):
        if self.use_in_memory:
            vehicle = next((v for v in self.vehicles if v['id'] == id), None)
            if vehicle:
                vehicle.update(vehicle_data)
                return vehicle
            return None
        else:
            return self._mock_api_call('PUT', f'/api/v1/vehicles/{id}', vehicle_data)

    def delete_vehicle(self, id):
        if self.use_in_memory:
            self.vehicles = [v for v in self.vehicles if v['id'] != id]
            return {"message": "Vehicle deleted"}
        else:
            return self._mock_api_call('DELETE', f'/api/v1/vehicles/{id}')

    # Fleet Management
    def get_fleets(self):
        if self.use_in_memory:
            return self.fleets
        else:
            return self._mock_api_call('GET', '/api/v1/fleets')

    def add_fleet(self, fleet):
        if self.use_in_memory:
            fleet['id'] = len(self.fleets) + 1
            self.fleets.append(fleet)
            return fleet
        else:
            return self._mock_api_call('POST', '/api/v1/fleets', fleet)

    def get_fleet(self, id):
        if self.use_in_memory:
            return next((f for f in self.fleets if f['id'] == id), None)
        else:
            return self._mock_api_call('GET', f'/api/v1/fleets/{id}')

    def update_fleet(self, id, fleet_data):
        if self.use_in_memory:
            fleet = next((f for f in self.fleets if f['id'] == id), None)
            if fleet:
                fleet.update(fleet_data)
                return fleet
            return None
        else:
            return self._mock_api_call('PUT', f'/api/v1/fleets/{id}', fleet_data)

    def delete_fleet(self, id):
        if self.use_in_memory:
            self.fleets = [f for f in self.fleets if f['id'] != id]
            return {"message": "Fleet deleted"}
        else:
            return self._mock_api_call('DELETE', f'/api/v1/fleets/{id}')

    # Trip Management
    def get_trips(self):
        if self.use_in_memory:
            return self.trips
        else:
            return self._mock_api_call('GET', '/api/v1/trips')

    def add_trip(self, trip):
        if self.use_in_memory:
            trip['id'] = len(self.trips) + 1
            self.trips.append(trip)
            return trip
        else:
            return self._mock_api_call('POST', '/api/v1/trips', trip)

    def get_trip(self, id):
        if self.use_in_memory:
            return next((t for t in self.trips if t['id'] == id), None)
        else:
            return self._mock_api_call('GET', f'/api/v1/trips/{id}')

    def update_trip(self, id, trip_data):
        if self.use_in_memory:
            trip = next((t for t in self.trips if t['id'] == id), None)
            if trip:
                trip.update(trip_data)
                return trip
            return None
        else:
            return self._mock_api_call('PUT', f'/api/v1/trips/{id}', trip_data)

    # Maintenance
    def get_maintenance(self):
        if self.use_in_memory:
            return self.maintenance_tasks
        else:
            return self._mock_api_call('GET', '/api/v1/maintenance')

    def add_maintenance(self, task):
        if self.use_in_memory:
            task['id'] = len(self.maintenance_tasks) + 1
            self.maintenance_tasks.append(task)
            return task
        else:
            return self._mock_api_call('POST', '/api/v1/maintenance', task)

    # Reporting
    def get_reports(self):
        if self.use_in_memory:
            return self.reports
        else:
            return self._mock_api_call('GET', '/api/v1/reports')

    def add_report(self, report):
        if self.use_in_memory:
            report['id'] = len(self.reports) + 1
            self.reports.append(report)
            return report
        else:
            return self._mock_api_call('POST', '/api/v1/reports', report)

    def _mock_api_call(self, method, endpoint, data=None):
        # This method simulates an API call to your existing system
        # In the future, this would be replaced with actual API calls
        return json.dumps({"message": f"Mock API call: {method} {endpoint}"})

data_store = DataStore(use_in_memory=True)