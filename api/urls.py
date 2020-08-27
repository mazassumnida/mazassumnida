from django.urls import path
from .views import generate_badge, generate_badge_v2

urlpatterns = [
    path('generate_badge', generate_badge),
    path('v2/generate_badge', generate_badge_v2)
]
