from django.http import JsonResponse
from django.core.cache import cache
from .models import VehicleType, ApplicationConfig
from django.core.paginator import Paginator

# ============================================================
# Vehicle Types API
# ============================================================
def vehicle_types(request):

    cache_key = "vehicle_types"

    # --------------------------------------------------------
    # Check Redis cache first
    # --------------------------------------------------------
    cached_data = cache.get(cache_key)

    # If data exists in Redis, return cached data
    if cached_data is not None:
        return JsonResponse({
            "source": "redis",
            "vehicle_types": cached_data
        })

    # --------------------------------------------------------
    # Cache miss:
    # Redis does not have the data, so get fresh data
    # from the database.
    # --------------------------------------------------------
    vehicle_types = VehicleType.objects.filter(
        is_active=True
    ).values(
        "id",
        "name",
        "capacity",
        "base_fare"
    )

    data = list(vehicle_types)

    # --------------------------------------------------------
    # Store fresh database data in Redis for 10 minutes
    # --------------------------------------------------------
    cache.set(
        cache_key,
        data,
        timeout=60 * 10
    )

    # Return fresh data from database
    return JsonResponse({
        "source": "database",
        "vehicle_types": data
    })


# ============================================================
# Application Configuration API
# ============================================================
def application_config(request):

    cache_key = "application_config"

    # --------------------------------------------------------
    # Check Redis cache first
    # --------------------------------------------------------
    cached_config = cache.get(cache_key)

    # If data exists in Redis, return cached data
    if cached_config is not None:
        return JsonResponse({
            "source": "redis",
            "config": cached_config
        })

    # --------------------------------------------------------
    # Cache miss:
    # Redis does not have the configuration, so get it
    # from the database.
    # --------------------------------------------------------
    config = ApplicationConfig.objects.all().values(
        "key",
        "value"
    )

    data = {
        item["key"]: item["value"]
        for item in config
    }

    # --------------------------------------------------------
    # Store configuration in Redis for 30 minutes
    # --------------------------------------------------------
    cache.set(
        cache_key,
        data,
        timeout=60 * 30
    )

    return JsonResponse({
        "source": "database",
        "config": data
    })


# ============================================================
# Update Vehicle Type API
# ============================================================
def update_vehicle_type(request, vehicle_id):

    # Only allow POST requests for updating data
    if request.method != "POST":
        return JsonResponse({
            "error": "Only POST method is allowed"
        }, status=405)

    # --------------------------------------------------------
    # Get the vehicle from the database
    # --------------------------------------------------------
    try:
        vehicle = VehicleType.objects.get(id=vehicle_id)
    except VehicleType.DoesNotExist:
        return JsonResponse({
            "error": "Vehicle type not found"
        }, status=404)

    # --------------------------------------------------------
    # Update the database
    # --------------------------------------------------------
    vehicle.base_fare = 200
    vehicle.save()

    # ========================================================
    # CACHE INVALIDATION
    # ========================================================
    # The vehicle data in Redis is now OLD/STALE because
    # the database value has changed.
    #
    # Therefore, delete the old cached vehicle_types data.
    # The next GET request will get fresh data from the
    # database and store it in Redis again.
    # ========================================================
    cache.delete("vehicle_types")

    # --------------------------------------------------------
    # Return success response
    # --------------------------------------------------------
    return JsonResponse({
        "message": "Vehicle updated successfully",
        "cache": "invalidated"
    })
def vehicle_types_paginated(request):

    # --------------------------------------------------------
    # Maximum number of records allowed per page
    # --------------------------------------------------------
     MAX_PAGE_SIZE = 20

    # --------------------------------------------------------
    # Get page number from URL
    # Example:
    # /api/vehicle-types-paginated/?page=2
    # --------------------------------------------------------
     page_number = request.GET.get("page", 1)

    # --------------------------------------------------------
    # Get requested page size
    # Example:
    # /api/vehicle-types-paginated/?page=1&page_size=10
    # --------------------------------------------------------
     page_size = request.GET.get("page_size", 5)

    # --------------------------------------------------------
    # Validate page number
    # --------------------------------------------------------
     try:
        page_number = int(page_number)
     except ValueError:
        page_number = 1

    # --------------------------------------------------------
    # Validate page size
    # --------------------------------------------------------
     try:
        page_size = int(page_size)
     except ValueError:
        page_size = 5

    # --------------------------------------------------------
    # Maximum page size protection
    #
    # If user requests:
    # page_size=1000
    #
    # We limit it to:
    # page_size=20
    # --------------------------------------------------------
     if page_size > MAX_PAGE_SIZE:
        page_size = MAX_PAGE_SIZE

    # Prevent zero or negative page sizes
     if page_size < 1:
        page_size = 5

    # --------------------------------------------------------
    # FIELD SELECTION
    #
    # Only select fields required by the API.
    #
    # We do NOT retrieve unnecessary database fields.
    # --------------------------------------------------------
     vehicle_queryset = VehicleType.objects.filter(
        is_active=True
    ).values(
        "id",
        "name",
        "capacity",
        "base_fare"
    )

    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------
     paginator = Paginator(
        vehicle_queryset,
        page_size
    )

    # Get requested page
     page_obj = paginator.get_page(page_number)

    # --------------------------------------------------------
    # LIGHTWEIGHT RESPONSE
    #
    # Convert only the required fields into the response.
    # --------------------------------------------------------
     data = list(page_obj.object_list)

    # --------------------------------------------------------
    # Return paginated response
    # --------------------------------------------------------
     return JsonResponse({
        "page": page_obj.number,
        "page_size": page_size,
        "total": paginator.count,
        "total_pages": paginator.num_pages,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "vehicle_types": data
    })
    