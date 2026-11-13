from typing import List, Optional

from django.utils import timezone

from .models import Itinerary


class ItineraryRepository:
    """All database access for itineraries lives here."""

    @staticmethod
    def create_pending(batch) -> Itinerary:
        return Itinerary.objects.create(batch=batch, status=Itinerary.Status.PENDING)

    @staticmethod
    def get(itinerary_id) -> Optional[Itinerary]:
        return Itinerary.objects.filter(pk=itinerary_id).first()

    @staticmethod
    def find_completed_for_batch(batch_id) -> Optional[Itinerary]:
        return Itinerary.objects.filter(
            batch_id=batch_id, status=Itinerary.Status.COMPLETED
        ).first()

    @staticmethod
    def mark_completed(itinerary: Itinerary, route: List[str]) -> Itinerary:
        itinerary.status = Itinerary.Status.COMPLETED
        itinerary.route = route
        itinerary.error_message = ""
        itinerary.completed_at = timezone.now()
        itinerary.save(update_fields=["status", "route", "error_message", "completed_at"])
        return itinerary

    @staticmethod
    def mark_failed(itinerary: Itinerary, message: str) -> Itinerary:
        itinerary.status = Itinerary.Status.FAILED
        itinerary.error_message = message
        itinerary.completed_at = timezone.now()
        itinerary.save(update_fields=["status", "error_message", "completed_at"])
        return itinerary
