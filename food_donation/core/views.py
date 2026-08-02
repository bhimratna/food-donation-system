from django.shortcuts import render, redirect
from django.contrib import messages
from geopy.distance import geodesic
from .models import Event, EventManager, Collection, NGO
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from datetime import datetime, timedelta
import json
import requests
from django.http import JsonResponse
from .models import Collection
from django.views.decorators.csrf import csrf_exempt

#-----------------------------MAP 
def live_map(request):

    events = Event.objects.all()

    return render(request, 'map.html', {
        'events': events
    })

def pickup(request, id):

    collection = Collection.objects.get(id=id)

    collection.status = "Pickup Started"

    collection.save()

    return redirect('accepted_events')


def ontheway(request, id):

    collection = Collection.objects.get(id=id)

    collection.status = "On The Way"

    collection.save()

    return redirect('accepted_events')


def delivered(request, id):

    collection = Collection.objects.get(id=id)

    collection.status = "Delivered"

    collection.save()

    return redirect('accepted_events')

#-------------------------------
# AI CHATBOT
#------------------------------- 

@csrf_exempt
def ai_chat(request):

    if request.method == "POST":

        data = json.loads(request.body)
        message = data.get("message")

        headers = {
            "Authorization": "Bearer YOUR_OPENROUTER_API_KEY",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant for Food Donation System."
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )

        result = response.json()

        reply = result['choices'][0]['message']['content']

        return JsonResponse({
            "response": reply
        })
# -----------------------------
# ADD FOOD EVENT
# -----------------------------
@login_required
def add_event(request):

    profile = UserProfile.objects.get(user=request.user)

    if profile.role != 'event_manager':
        return redirect('dashboard')

    if request.method == 'POST':

        expiry_time = request.POST['expiry_time']
        event_name = request.POST['event_name']
        location = request.POST['location']
        food_items = request.POST['food_items']
        quantity = request.POST['quantity']

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if latitude == "":
            latitude = None

        if longitude == "":
            longitude = None

        image = request.FILES.get('image')

        manager, created = EventManager.objects.get_or_create(

            name=request.user.username,

            defaults={
                'email': f'{request.user.username}@foodbridge.com',
                'phone': '9999999999'
            }
        )

        # CREATE EVENT

        event = Event.objects.create(

            manager=manager,

            event_name=event_name,

            location=location,

            food_items=food_items,

            quantity=quantity,

            latitude=latitude,

            longitude=longitude,

            expiry_time=expiry_time,

            image=image
        )

        # FIND NEAREST NGO

        nearest_ngo = None
        minimum_distance = 999999

        if latitude and longitude:

            event_location = (
                float(latitude),
                float(longitude)
            )

            ngos = NGO.objects.exclude(
                latitude=None
            ).exclude(
                longitude=None
            )

            for ngo in ngos:

                ngo_location = (
                    ngo.latitude,
                    ngo.longitude
                )

                distance = geodesic(
                    event_location,
                    ngo_location
                ).km

                if distance < minimum_distance:

                    minimum_distance = distance
                    nearest_ngo = ngo

        # AUTO ASSIGN NGO

        if nearest_ngo:

            Collection.objects.create(

                event=event,

                ngo=nearest_ngo,

                status="Accepted",
                
                distance=round(minimum_distance, 2)
            )
            messages.success(request,f"Donation successfully assigned to {nearest_ngo.name}")

        return redirect('home')

    return render(request, 'add_event.html')
# -----------------------------
# SHOW EVENTS
# -----------------------------
@login_required
def event_list(request):
    events = Event.objects.all()

    scored_events = []

    for event in events:
        score = 0

        # Expiry priority
        try:
            hours = int(event.expiry_time.split()[0])
            score += (10 - hours) * 5
        except:
            pass

        # Quantity priority
        score += int(event.quantity) / 10

        # Add to list
        scored_events.append((score, event))

    # sort highest priority first
    scored_events.sort(reverse=True, key=lambda x: x[0])

    # remove score
    events = [e[1] for e in scored_events]

    return render(request, 'event_list.html', {'events': events})


# -----------------------------
# NGO ACCEPT EVENT
# -----------------------------
@login_required
def accept_event(request, event_id):

    event = Event.objects.get(id=event_id)

    # prevent duplicate accept
    if Collection.objects.filter(event=event).exists():
        return redirect('event_list')

    # get NGO
    ngo = NGO.objects.first()

    Collection.objects.create(
        event=event,
        ngo=ngo,
        status="Accepted"
    )

    return redirect('accepted_events')


# -----------------------------
# ACCEPTED EVENTS
# -----------------------------
@login_required
def accepted_events(request):
    accepted = Collection.objects.all()
    return render(request, 'accepted.html', {'accepted': accepted})


# -----------------------------
# DISTRIBUTE FOOD
# -----------------------------
@login_required
def distribute_food(request, id):
    # allow only NGO
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'ngo':
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        return redirect('dashboard')

    item = Collection.objects.get(id=id)

    # prevent re-completing
    if item.status == "Delivered":
        return redirect('accepted_events')

    item.status = "Delivered"
    item.save()

    return redirect('accepted_events')


# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
@login_required
def dashboard(request):
    total_events = Event.objects.count()
    accepted = Collection.objects.filter(status="Accepted").count()
    completed = Collection.objects.filter(status="Delivered").count()

    context = {
        'total_events': total_events,
        'accepted': accepted,
        'completed': completed
    }

    return render(request, 'dashboard.html', context)


# -----------------------------
# NGO DASHBOARD
# -----------------------------
def ngo_dashboard(request):
    user = request.user
 
    ngo = NGO.objects.get(user=request.user)
    donations = Collection.objects.filter(ngo=ngo,distance__lte=10)
    

    total = donations.count()
    accepted = donations.filter(status="Accepted").count()
    completed = donations.filter(status="Delivered").count()

    # urgent logic
    urgent = 0
    for d in donations:
        if d.event.expiry_time:
            try:
                hours = int(d.event.expiry_time.split()[0])
                if hours <= 2:
                    urgent += 1
            except:
                pass

    return render(request, 'ngo_dashboard.html', {
        'total': total,
        'accepted': accepted,
        'completed': completed,
        'urgent': urgent,
        'donations': donations
    })


@login_required
def event_dashboard(request):

    return render(request, 'event_dashboard.html')



# -----------------------------
# LOGIN (ROLE BASED)
# -----------------------------
def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            profile = UserProfile.objects.get(user=user)

            # ADMIN
            if profile.role == 'admin':
                return redirect('dashboard')

            # NGO
            elif profile.role == 'ngo':
                return redirect('ngo_dashboard')

            # EVENT MANAGER
            elif profile.role == 'event_manager':
                return redirect('event_dashboard')

    return render(request, 'login.html')


# -----------------------------
# LOGOUT
# -----------------------------
def user_logout(request):
    logout(request)
    return redirect('login')
