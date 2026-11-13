from django.urls import include, path

urlpatterns = [
    path("api/v1/tickets/", include("apps.tickets.urls")),
    path("api/v1/itineraries/", include("apps.itineraries.urls")),
]
