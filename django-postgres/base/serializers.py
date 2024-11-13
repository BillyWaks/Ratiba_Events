# base/serializers.py
from rest_framework import serializers
from .models import Event, Participant, Registration, Booking
from django.shortcuts import get_object_or_404

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'image', 'date', 'time', 'venue', 'charge']  # Added image field

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'name', 'email']  # Explicit fields

class RegistrationSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(source='event.id', write_only=True)  # Accept event ID directly
    participant = ParticipantSerializer()  # Still allows nested input for participant

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
        event_data = validated_data.pop('event', None)
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


class BookingSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(source='event.id', write_only=True)  # Accept event ID directly
    participant = ParticipantSerializer()  # Still allows nested input for participant

    class Meta:
        model = Booking
        fields = ['id', 'event_id', 'participant', 'timestamp', 'status']

    def create(self, validated_data):
        participant_data = validated_data.pop('participant')
        event_id = validated_data.pop('event_id')  # Get event ID from validated data

        # Retrieve or create the participant instance
        participant, created = Participant.objects.get_or_create(**participant_data)

        # Retrieve the event instance by ID or raise an error
        event = get_object_or_404(Event, id=event_id)

        # Create the booking instance
        booking = Booking.objects.create(participant=participant, event=event, **validated_data)
        return booking

    def update(self, instance, validated_data):
        event_data = validated_data.pop('event', None)
        participant_data = validated_data.pop('participant', None)

        if participant_data:
            # Update participant instance
            for attr, value in participant_data.items():
                setattr(instance.participant, attr, value)
            instance.participant.save()

        # Update booking instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance