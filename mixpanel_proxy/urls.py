from django.urls import path
from . import views

urlpatterns = [
    path('track/', views.track),
    path('decide/', views.decide),
    path('engage/', views.engage),
]