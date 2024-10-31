from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Event, Participant, Registration
from .serializers import EventSerializer, ParticipantSerializer, RegistrationSerializer
from django.utils import timezone
from django.utils.timezone import make_aware

# Example: Base class with authentication and permission for all views in this module
class AuthenticatedAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

class EventList(AuthenticatedAPIView, generics.ListAPIView):
    """View to list all events."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class CreateEvent(AuthenticatedAPIView, generics.CreateAPIView):
    """View to create a new event."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventDetail(AuthenticatedAPIView, generics.RetrieveAPIView):
    """View to retrieve details of a specific event."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class RegisterEvent(AuthenticatedAPIView):
    """View to register a participant for an event."""

    def post(self, request, *args, **kwargs):
        # Extract event_id and participant data from request
        event_id = request.data.get('event_id')
        participant_data = request.data.get('participant')

        # Get the event or return 404 if not found
        event = get_object_or_404(Event, pk=event_id)

        # Check if the event date and time have passed
        event_datetime = make_aware(
            timezone.datetime.combine(event.event_datetime.date(), event.event_datetime.time())
        )
        if event_datetime < timezone.now():
            return Response({"error": "Event date or time has passed. Registration is closed."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and handle participant data
        participant_serializer = ParticipantSerializer(data=participant_data)
        if participant_serializer.is_valid():
            participant_email = participant_data['email']
            participant, _ = Participant.objects.get_or_create(email=participant_email, defaults=participant_data)

            # Check for existing registration
            if Registration.objects.filter(event=event, participant=participant).exists():
                return Response({"error": "Participant is already registered for this event."}, status=status.HTTP_400_BAD_REQUEST)

            # Create registration
            registration_data = {'event': event.id, 'participant': participant.id}
            registration_serializer = RegistrationSerializer(data=registration_data)
            if registration_serializer.is_valid():
                registration_serializer.save()
                return Response(registration_serializer.data, status=status.HTTP_201_CREATED)
            return Response(registration_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(participant_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListParticipants(AuthenticatedAPIView, generics.ListAPIView):
    """View to list participants of a specific event."""
    serializer_class = ParticipantSerializer

    def get_queryset(self):
        # Extract event_id from URL kwargs
        event_id = self.kwargs['event_id']
        registration_objects = Registration.objects.filter(event_id=event_id)
        participants_ids = registration_objects.values_list('participant', flat=True)
        return Participant.objects.filter(id__in=participants_ids)
