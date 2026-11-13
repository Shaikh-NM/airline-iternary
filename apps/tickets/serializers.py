from rest_framework import serializers

from .services import MAX_TICKETS, MIN_TICKETS, TicketValidationError, validate_ticket_pairs


class TicketBatchCreateSerializer(serializers.Serializer):
    tickets = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField(), min_length=2, max_length=2
        ),
        min_length=MIN_TICKETS,
        max_length=MAX_TICKETS,
    )

    def validate_tickets(self, value):
        try:
            validate_ticket_pairs(value)
        except TicketValidationError as exc:
            raise serializers.ValidationError(exc.errors)
        return value


class TicketBatchSerializer(serializers.Serializer):
    batch_id = serializers.UUIDField(source="id")
    ticket_count = serializers.SerializerMethodField()
    tickets = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_ticket_count(self, obj):
        return obj.tickets.count()

    def get_tickets(self, obj):
        return [[o, d] for o, d in obj.tickets.values_list("origin", "destination")]
