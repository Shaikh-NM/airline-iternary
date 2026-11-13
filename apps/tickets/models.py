import uuid

from django.db import models
from django.db.models import F, Q


class TicketBatch(models.Model):
    """A set of tickets submitted together; the input to one reconstruction."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class Ticket(models.Model):
    """One flight leg. Duplicate (origin, destination) pairs are allowed."""

    batch = models.ForeignKey(
        TicketBatch, on_delete=models.CASCADE, related_name="tickets"
    )
    origin = models.CharField(max_length=3)
    destination = models.CharField(max_length=3)
    position = models.PositiveSmallIntegerField(
        help_text="Order in which the ticket was submitted."
    )

    class Meta:
        ordering = ["position"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(origin=F("destination")),
                name="ticket_origin_ne_destination",
            ),
            models.UniqueConstraint(
                fields=["batch", "position"], name="ticket_unique_position_per_batch"
            ),
        ]
        indexes = [models.Index(fields=["batch", "origin"])]

    def __str__(self):
        return f"{self.origin}->{self.destination}"
