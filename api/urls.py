from django.urls import path
from .views import generate_badge

urlpatterns = [
    path('generate_badge', generate_badge)
]