from django.contrib import admin
from .models import UserProfile, EventManager, Event, NGO, Collection

admin.site.register(UserProfile)
admin.site.register(EventManager)
admin.site.register(Event)
admin.site.register(NGO)
admin.site.register(Collection)