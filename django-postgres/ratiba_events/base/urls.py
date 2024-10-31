# base/urls.py
from django.urls import path
from .views import EventList, EventDetail, RegisterEvent, CreateEvent, ListParticipants

urlpatterns = [
    path('events/', EventList.as_view(), name='event-list'),  # List all events
    path('events/<int:pk>/', EventDetail.as_view(), name='event-detail'),  # Retrieve a specific event
    path('register/', RegisterEvent.as_view(), name='register-event'),  # Register a participant for an event
    path('events/create/', CreateEvent.as_view(), name='create-event'),  # Create a new event
    path('events/<int:event_id>/participants/', ListParticipants.as_view(), name='list-participants'),  # List participants of a specific event
]