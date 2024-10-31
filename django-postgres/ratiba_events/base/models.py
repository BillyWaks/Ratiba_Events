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
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)  # Optional image field
    date = models.DateField(default=timezone.now)  # Separate date field
    time = models.TimeField(default=timezone.now)  # Separate time field
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
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Status field

    class Meta:
        unique_together = ('event', 'participant')
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.participant} registered for {self.event}"














# User = get_user_model()
# # devfest_participant = models.BooleanField(default=True, null=True)

# class Event(models.Model):
#     name = models.CharField(max_length=200)
#     description = models.TextField(null=True, blank=True)
#     participants = models.ManyToManyField(User, blank=True)
#     date = models.DateField()
#     updated = models.DateTimeField(auto_now=True)
#     created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name

#     class Meta:
#         ordering = ['date']


# class Submission(models.Model):
#     participant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
#     details = models.TextField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.event} --- {self.participant}"

#     class Meta:
#         ordering = ['event']
