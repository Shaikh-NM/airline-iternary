from rest_framework import serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import TicketBatch
from .serializers import TicketBatchCreateSerializer, TicketBatchSerializer


class BatchQuerySerializer(serializers.Serializer):
    batch_id = serializers.UUIDField()


class TicketListCreateView(APIView):
    def post(self, request):
        serializer = TicketBatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        batch = services.submit_tickets(serializer.validated_data["tickets"])
        return Response(TicketBatchSerializer(batch).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        query = BatchQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        try:
            batch = services.get_batch(query.validated_data["batch_id"])
        except TicketBatch.DoesNotExist:
            raise NotFound("Ticket batch not found.")
        return Response(TicketBatchSerializer(batch).data)
