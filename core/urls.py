from django.urls import path
from .views import (
    vehicle_types,
    application_config,
    update_vehicle_type,
    vehicle_types_paginated,
)

urlpatterns = [
      # Existing Vehicle Types API
    path("vehicle-types/", vehicle_types, name="vehicle-types"),
       # Existing Application Configuration API
    path(
        "config/",
        application_config,
        name="application-config",
    ),
    
  # Existing Vehicle Update API
    path(
        "vehicle-types/<int:vehicle_id>/update/",
        update_vehicle_type,
        name="update-vehicle",
    ),
    # New Paginated Vehicle Types API
    path(
        "vehicle-types-paginated/",
        vehicle_types_paginated,
        name="vehicle-types-paginated",
    ),
]