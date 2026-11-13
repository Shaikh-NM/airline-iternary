import logging
from typing import Tuple

from apps.tickets import services as ticket_services

from .algorithm.exceptions import InvalidItineraryError
from .algorithm.graph_builder import build_adjacency_list
from .algorithm.itinerary_builder import build_itinerary
from .algorithm.validators import validate_itinerary
from .models import Itinerary
from .repositories import ItineraryRepository

logger = logging.getLogger(__name__)


def reconstruct_itinerary(batch_id) -> Tuple[Itinerary, bool]:
    """Reconstruct the itinerary for a ticket batch.

    Returns ``(itinerary, created)``. Tickets in a batch are immutable, so the
    result is deterministic: an already COMPLETED itinerary is reused.

    Raises ``TicketBatch.DoesNotExist`` if the batch does not exist.
    """
    batch = ticket_services.get_batch(batch_id)

    existing = ItineraryRepository.find_completed_for_batch(batch.id)
    if existing:
        return existing, False

    itinerary = ItineraryRepository.create_pending(batch)
    tickets = ticket_services.get_ticket_pairs(batch)

    try:
        graph = build_adjacency_list(tickets)
        route = build_itinerary(graph)
        validate_itinerary(tickets, route)
    except InvalidItineraryError as exc:
        ItineraryRepository.mark_failed(itinerary, str(exc))
        return itinerary, True
    except Exception as exc:  # unexpected: record it, then surface it
        logger.exception("Unexpected error reconstructing batch %s", batch.id)
        ItineraryRepository.mark_failed(itinerary, f"Internal error: {exc}")
        raise

    ItineraryRepository.mark_completed(itinerary, route)
    return itinerary, True


def get_itinerary(itinerary_id):
    return ItineraryRepository.get(itinerary_id)
