from collections import Counter
from typing import List, Sequence, Tuple

from .exceptions import InvalidItineraryError
from .itinerary_builder import START_AIRPORT


def validate_itinerary(
    tickets: Sequence[Tuple[str, str]],
    route: List[str],
    start: str = START_AIRPORT,
) -> None:
    """Ensure the route starts at ``start`` and uses every ticket exactly once."""
    if not route or route[0] != start:
        raise InvalidItineraryError(f"Itinerary must start from {start}.")

    if len(route) != len(tickets) + 1:
        used = max(len(route) - 1, 0)
        raise InvalidItineraryError(
            f"Tickets do not form a valid itinerary from {start}: "
            f"only {used} of {len(tickets)} tickets could be used."
        )

    legs_used = Counter(zip(route, route[1:]))
    legs_expected = Counter(tuple(t) for t in tickets)
    if legs_used != legs_expected:
        raise InvalidItineraryError("Itinerary does not use every ticket exactly once.")
