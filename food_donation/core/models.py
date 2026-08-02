from django.db import models
from django.contrib.auth.models import User


# -----------------------------
# USER PROFILE (ROLE BASED)
# -----------------------------
class UserProfile(models.Model):

    ROLE_CHOICES = (

        ('admin', 'Admin'),

        ('ngo', 'NGO'),

        ('event_manager', 'Event Manager'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    def __str__(self):
        return self.user.username
    
    
# -----------------------------
# EVENT MANAGER (DONOR)
# -----------------------------
class EventManager(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField(null=True, blank=True)  # ✅ NEW

    def __str__(self):
        return self.name


# -----------------------------
# NGO MODEL
# -----------------------------
class NGO(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    name = models.CharField(max_length=100)

    contact = models.CharField(max_length=15)

    location = models.CharField(max_length=200)

    latitude = models.FloatField(null=True, blank=True)

    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

# -----------------------------
# FOOD EVENT
# -----------------------------
class Event(models.Model):
    manager = models.ForeignKey(EventManager, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    food_items = models.CharField(max_length=200)
    quantity = models.IntegerField()
    expiry_time = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to='food_images/', null=True, blank=True)  # ✅ NEW
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # ✅ NEW

    def __str__(self):
        return self.event_name


# -----------------------------
# COLLECTION / ACCEPT
# -----------------------------
class Collection(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, null=True, blank=True)  # ✅ FIXED (no string)
    STATUS_CHOICES = (

        ('Accepted', 'Accepted'),

        ('Pickup Started', 'Pickup Started'),

        ('On The Way', 'On The Way'),

        ('Delivered', 'Delivered'),
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )

    ngo = models.ForeignKey(
        NGO,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Accepted'
    )

    distance = models.FloatField(
        null=True,
        blank=True
    )

    priority_score = models.FloatField(
        null=True,
        blank=True
    )

    def __str__(self):

        return f"{self.event} -> {self.ngo}"
   