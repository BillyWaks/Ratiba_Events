# base/models.py

from django.db import models
from django.utils import timezone

class Event(models.Model):
    CHARGE_CHOICES = [
        ('free', 'Free'),
        ('pay', 'Pay'),
    ]

    id = models.AutoField(primary_key=True)  # Explicit primary key
    title = models.CharField(max_length=100)  # Renamed from name to title
    description = models.TextField()
    image = models.ImageField(upload_to='event_images/', max_length=500, blank=True, null=True)
    date = models.DateField(default=timezone.localdate)  # Gets today's date without time
    time = models.TimeField(default=timezone.now)  # Gets current time
    venue = models.CharField(max_length=255, blank=True)  # Replaces location
    charge = models.CharField(max_length=4, choices=CHARGE_CHOICES, default='free')  # Free or Pay option

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['date', 'time']


class Participant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  # Enforce unique email addresses

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Registration(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('rsvp', 'RSVP'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('event', 'participant')
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.participant} registered for {self.event}"
    
class Booking(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    booked = models.BooleanField(default=False)  # Whether the participant has booked their spot

    def __str__(self):
        return f"{self.participant} booked for {self.event}"

