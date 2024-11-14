from rest_framework import serializers
from .models import Event, Participant, Registration
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from datetime import datetime
from rest_framework.fields import ImageField

class EventSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    # Explicitly define the image field as an ImageField
    image = ImageField(required=False, allow_null=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'image', 'date', 'time', 'venue', 'charge', 'image_url']

    def get_image_url(self, obj):
        """Returns the full URL for the image."""
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return settings.MEDIA_URL + str(obj.image)
        return None
    
class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'name', 'email']  # Explicit fields

class RegistrationSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(source='event.id', write_only=True)  # Accept event ID directly
    participant = ParticipantSerializer()  # Allows nested input for participant

    class Meta:
        model = Registration
        fields = ['id', 'event_id', 'participant', 'timestamp', 'status']  # Explicit fields

    def create(self, validated_data):
        participant_data = validated_data.pop('participant')
        event_id = validated_data.pop('event_id')  # Get event ID from validated data

        # Retrieve or create the participant instance
        participant, created = Participant.objects.get_or_create(**participant_data)

        # Retrieve the event instance by ID or raise an error
        event = get_object_or_404(Event, id=event_id)

        # Create the registration instance
        registration = Registration.objects.create(participant=participant, event=event, **validated_data)
        return registration

    def update(self, instance, validated_data):
        participant_data = validated_data.pop('participant', None)

        if participant_data:
            # Update participant instance
            for attr, value in participant_data.items():
                setattr(instance.participant, attr, value)
            instance.participant.save()

        # Update registration instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
    
class RSVPSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    participant = ParticipantSerializer()

    def validate_event_id(self, value):
        """Ensure the event exists and is in the future."""
        event = get_object_or_404(Event, id=value)
        
        # Check if the event date/time has passed
        event_datetime = timezone.make_aware(
            timezone.datetime.combine(event.date, event.time)
        )
        if event_datetime < timezone.now():
            raise serializers.ValidationError("Cannot RSVP to an event that has already passed.")
        
        return value

    def create(self, validated_data):
        """Handle RSVP creation."""
        event_id = validated_data['event_id']
        participant_data = validated_data['participant']

        # Retrieve or create the participant
        participant, created = Participant.objects.get_or_create(
            email=participant_data['email'],
            defaults=participant_data
        )

        # Retrieve the event instance by ID
        event = get_object_or_404(Event, id=event_id)

        # Retrieve or create the registration and set the status to 'rsvp'
        registration, created = Registration.objects.get_or_create(
            event=event,
            participant=participant,
            defaults={'status': 'rsvp'}
        )

        # If the registration already exists but isn't RSVP, update it
        if not created and registration.status != 'rsvp':
            registration.status = 'rsvp'
            registration.save()

        return registration