from rest_framework import serializers


class ReconstructRequestSerializer(serializers.Serializer):
    batch_id = serializers.UUIDField()


class ItinerarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    batch_id = serializers.UUIDField()
    status = serializers.CharField()
    route = serializers.ListField(child=serializers.CharField())
    error_message = serializers.CharField()
    created_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(allow_null=True)
