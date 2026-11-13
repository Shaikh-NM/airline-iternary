import re
import uuid

from django.db import transaction

from .models import Ticket, TicketBatch

AIRPORT_CODE_RE = re.compile(r"^[A-Z]{3}$")
MIN_TICKETS = 1
MAX_TICKETS = 300


class TicketValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("; ".join(errors))


def validate_ticket_pairs(pairs):
    """Validate raw [[from, to], ...] input. Raises TicketValidationError
    listing every problem found."""
    errors = []
    if not isinstance(pairs, (list, tuple)):
        raise TicketValidationError(["tickets must be a list."])
    if not MIN_TICKETS <= len(pairs) <= MAX_TICKETS:
        errors.append(
            f"Number of tickets must be between {MIN_TICKETS} and {MAX_TICKETS}."
        )
    for i, pair in enumerate(pairs):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            errors.append(f"tickets[{i}] must be a [from, to] pair.")
            continue
        origin, destination = pair
        for label, code in (("from", origin), ("to", destination)):
            if not isinstance(code, str) or not AIRPORT_CODE_RE.match(code):
                errors.append(
                    f"tickets[{i}] '{label}' must be 3 uppercase letters, got {code!r}."
                )
        if origin == destination:
            errors.append(f"tickets[{i}] 'from' and 'to' must differ.")
    if errors:
        raise TicketValidationError(errors)


@transaction.atomic
def submit_tickets(pairs):
    """Validate and persist tickets as a new batch."""
    validate_ticket_pairs(pairs)
    batch = TicketBatch.objects.create()
    Ticket.objects.bulk_create(
        [
            Ticket(batch=batch, origin=o, destination=d, position=i)
            for i, (o, d) in enumerate(pairs)
        ]
    )
    return batch


def get_batch(batch_id: uuid.UUID) -> TicketBatch:
    """Raises TicketBatch.DoesNotExist if missing."""
    return TicketBatch.objects.get(pk=batch_id)


def get_ticket_pairs(batch: TicketBatch):
    return list(batch.tickets.values_list("origin", "destination"))
