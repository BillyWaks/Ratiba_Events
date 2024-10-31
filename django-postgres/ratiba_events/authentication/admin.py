from django.contrib import admin
from base.models import Event, Participant, Registration
#Category
# Submission
from .models import User

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'auth_provider', 'created_at']


admin.site.register(User, UserAdmin)
admin.site.register(Event)
admin.site.register(Participant)
admin.site.register(Registration)
# admin.site.register(Submission)