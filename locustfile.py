from locust import HttpUser, task, between


class VehicleTypeUser(HttpUser):

    # Wait between 1 and 3 seconds between requests
    wait_time = between(1, 3)

    @task
    def get_vehicle_types(self):

        # Test the paginated Vehicle Types API
        self.client.get(
            "/api/vehicle-types-paginated/?page=1&page_size=5"
        )