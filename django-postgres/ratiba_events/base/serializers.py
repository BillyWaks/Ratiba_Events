# base/serializers.py
from rest_framework import serializers
from .models import Event, Participant, Registration

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'image', 'date', 'time', 'venue', 'charge']  # Added image field

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'name', 'email']  # Explicit fields

class RegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer()  # Nested serializer
    participant = ParticipantSerializer()  # Nested serializer

    class Meta:
        model = Registration
        fields = ['id', 'event', 'participant', 'timestamp', 'status']  # Explicit fields

    def create(self, validated_data):
        event_data = validated_data.pop('event')
        participant_data = validated_data.pop('participant')

        # Create or get the participant instance
        participant, created = Participant.objects.get_or_create(**participant_data)

        # Create the registration instance
        registration = Registration.objects.create(participant=participant, event=event_data, **validated_data)
        return registration

    def update(self, instance, validated_data):
        # Handle nested update if necessary
        event_data = validated_data.pop('event', None)
        participant_data = validated_data.pop('participant', None)

        if participant_data:
            # Update participant instance
            for attr, value in participant_data.items():
                setattr(instance.participant, attr, value)
            instance.participant.save()

        if event_data:
            # Update event instance
            for attr, value in event_data.items():
                setattr(instance.event, attr, value)
            instance.event.save()

        # Update registration instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
