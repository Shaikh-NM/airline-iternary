from django.urls import path

from .views import ItineraryDetailView, ReconstructView

urlpatterns = [
    path("reconstruct/", ReconstructView.as_view(), name="itinerary-reconstruct"),
    path("<uuid:pk>/", ItineraryDetailView.as_view(), name="itinerary-detail"),
]
