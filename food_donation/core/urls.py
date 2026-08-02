"""
URL configuration for food_donation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from typing import Callable, Any, cast
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),   # Dashboard first
    path('add-event/', views.add_event, name='add_event'),
    path('events/', views.event_list, name='event_list'),
    path('accept/<int:event_id>/', views.accept_event, name='accept_event'),
    path('accepted/', views.accepted_events, name='accepted_events'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('distribute/<int:id>/', views.distribute_food, name='distribute'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('ngo/', views.ngo_dashboard, name='ngo_dashboard'),
    path('event-dashboard/',views.event_dashboard,name='event_dashboard'),
    path('map/',views.live_map,name='live_map'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('pickup/<int:id>/', views.pickup, name='pickup'),

    path('ontheway/<int:id>/', views.ontheway, name='ontheway'),

    path('delivered/<int:id>/', views.delivered, name='delivered'),
]    