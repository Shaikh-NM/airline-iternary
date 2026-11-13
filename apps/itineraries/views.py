from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tickets.models import TicketBatch

from . import services
from .models import Itinerary
from .serializers import ItinerarySerializer, ReconstructRequestSerializer


class ReconstructView(APIView):
    def post(self, request):
        serializer = ReconstructRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            itinerary, created = services.reconstruct_itinerary(
                serializer.validated_data["batch_id"]
            )
        except TicketBatch.DoesNotExist:
            raise NotFound("Ticket batch not found.")

        if itinerary.status == Itinerary.Status.FAILED:
            code = status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(ItinerarySerializer(itinerary).data, status=code)


class ItineraryDetailView(APIView):
    def get(self, request, pk):
        itinerary = services.get_itinerary(pk)
        if itinerary is None:
            raise NotFound("Itinerary not found.")
        return Response(ItinerarySerializer(itinerary).data)
