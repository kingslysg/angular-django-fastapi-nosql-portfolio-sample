from django.urls import path
from .views import health, projects

urlpatterns = [path('health/', health), path('projects/', projects)]
