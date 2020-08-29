from django.urls import path
from .views import generate_badge, generate_badge_v2, generate_badge_mini

urlpatterns = [
    path('generate_badge', generate_badge),
    path('v2/generate_badge', generate_badge_v2),
    path('mini/generate_badge', generate_badge_mini)
]
