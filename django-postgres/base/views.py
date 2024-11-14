# base/views.py
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.timezone import make_aware
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
from django.db.models import Q
from .models import Event, Participant, Registration, Booking
from .serializers import EventSerializer, ParticipantSerializer, RegistrationSerializer, RSVPSerializer, BookingSerializer, EventImageUploadSerializer
from rest_framework.parsers import MultiPartParser, FormParser
import logging

logger = logging.getLogger(__name__)
class AuthenticatedAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

class EventList(AuthenticatedAPIView, generics.ListAPIView):
    """View to list all events."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = EventSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

class CreateEvent(AuthenticatedAPIView, generics.CreateAPIView):
    """View to create a new event."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    
class EventImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        serializer = EventImageUploadSerializer(data=request.data)

        if serializer.is_valid():
            image = serializer.validated_data['image']
            event.image = image
            event.save()
            return Response({"message": "Image uploaded successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventDetail(AuthenticatedAPIView, generics.RetrieveAPIView):
    """View to retrieve details of a specific event."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get(self, request, *args, **kwargs):
        event_instance = self.get_object()
        serializer = EventSerializer(event_instance, context={'request': request})
        return Response(serializer.data)

class RegisterEvent(AuthenticatedAPIView):
    """View to register a participant for an event."""
    
    @swagger_auto_schema(request_body=RegistrationSerializer)
    def post(self, request, *args, **kwargs):
        event_id = request.data.get('event_id')
        participant_data = request.data.get('participant')

        event = get_object_or_404(Event, pk=event_id)

        # Check if the event date and time have passed
        event_datetime = make_aware(
            timezone.datetime.combine(event.date, event.time)
        )
        if event_datetime < timezone.now():
            return Response({"error": "Event date or time has passed. Registration is closed."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate and handle participant data
        participant_serializer = ParticipantSerializer(data=participant_data)
        if participant_serializer.is_valid():
            participant_email = participant_data['email']
            participant, created = Participant.objects.get_or_create(
                email=participant_email,
                defaults=participant_serializer.validated_data
            )

            # Check for existing registration
            if Registration.objects.filter(event=event, participant=participant).exists():
                return Response({"error": "Participant is already registered for this event."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Create registration using RegistrationSerializer
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
        event_id = self.kwargs.get('pk')
        if event_id:
            registration_objects = Registration.objects.filter(event_id=event_id)
            participants_ids = registration_objects.values_list('participant', flat=True)
            return Participant.objects.filter(id__in=participants_ids)
        else:
            return Participant.objects.none()
        
class CreateBooking(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            # Perform any additional checks (e.g., booking availability) before saving
            booking = serializer.save()  # Save the new booking
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
class UpdateBooking(APIView):
    def put(self, request, booking_id, *args, **kwargs):
        booking = Booking.objects.get(id=booking_id)
        
        # Confirm the booking by setting the 'booked' field to True
        booking.booked = True
        booking.save()
        
        return Response({"message": "Booking confirmed", "booking_id": booking.id}, status=status.HTTP_200_OK)


class RSVPEvent(APIView):
    """API to RSVP to an event."""
    
    @swagger_auto_schema(request_body=RSVPSerializer)
    def post(self, request, *args, **kwargs):
        serializer = RSVPSerializer(data=request.data)

        if serializer.is_valid():
            # Save the registration (create or update)
            registration = serializer.save()

            # Log the successful RSVP (optional)
            logger.info(f"RSVP successful for participant {registration.participant.email} to event {registration.event.id}")

            return Response({
                "message": "RSVP successful!",
                "registration_id": registration.id
            }, status=status.HTTP_201_CREATED)  # Use 201 for successful creation

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteEvent(AuthenticatedAPIView, generics.DestroyAPIView):
    """View to delete an event."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @swagger_auto_schema(operation_summary="Delete an event")
    def delete(self, request, *args, **kwargs):
        event = self.get_object()
        event.delete()
        return Response({"message": "Event deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class DeleteParticipant(AuthenticatedAPIView, generics.DestroyAPIView):
    """View to delete a participant."""
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    @swagger_auto_schema(operation_summary="Delete a participant")
    def delete(self, request, *args, **kwargs):
        participant = self.get_object()
        participant.delete()
        return Response({"message": "Participant deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class PastEventList(AuthenticatedAPIView, generics.ListAPIView):
    """View to list all past events."""
    serializer_class = EventSerializer

    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(
            Q(date__lt=now.date()) | 
            (Q(date=now.date()) & Q(time__lt=now.time()))
        )

class FutureEventList(AuthenticatedAPIView, generics.ListAPIView):
    """View to list all future events."""
    serializer_class = EventSerializer

    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(
            Q(date__gt=now.date()) | 
            (Q(date=now.date()) & Q(time__gte=now.time()))
        )