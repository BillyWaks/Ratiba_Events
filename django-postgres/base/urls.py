from django.urls import path
from .views import (
    EventList, EventDetail, RegisterEvent, CreateEvent,
    ListParticipants, PastEventList, FutureEventList,
    DeleteEvent, DeleteParticipant, RSVPEvent, EventImageUploadView
)

urlpatterns = [
    path('events/', EventList.as_view(), name='event-list'),  # List all events
    path('events/<int:pk>/', EventDetail.as_view(), name='event-detail'),  # Retrieve a specific event
    path('register/', RegisterEvent.as_view(), name='register-event'),  # Register a participant for an event
    path('events/create/', CreateEvent.as_view(), name='create-event'),  # Create a new event
    path('events/<int:event_id>/upload-image/', EventImageUploadView.as_view(), name='event-image-upload'),  # Upload image for a specific event
    path('events/<int:pk>/participants/', ListParticipants.as_view(), name='list-participants'),  # List participants of a specific event
    path('events/past/', PastEventList.as_view(), name='past-event-list'),  # List past events
    path('events/future/', FutureEventList.as_view(), name='future-event-list'),  # List future events
    path('events/<int:pk>/delete/', DeleteEvent.as_view(), name='delete-event'),  # Delete an event
    path('participants/<int:pk>/delete/', DeleteParticipant.as_view(), name='delete-participant'),  # Delete a participant
    path('events/rsvp/', RSVPEvent.as_view(), name='rsvp-event'),
    # path('events/book/', BookEvent.as_view(), name='book-event'),
]
