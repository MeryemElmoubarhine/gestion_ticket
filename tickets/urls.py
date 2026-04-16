from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_tickets, name='liste_tickets'),
]
