from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tickets/', views.liste_tickets, name='liste_tickets'),
    path('tickets/creer/', views.creer_ticket, name='creer_ticket'),
    path('tickets/<int:pk>/', views.detail_ticket, name='detail_ticket'),
    path('tickets/<int:pk>/modifier/', views.modifier_ticket, name='modifier_ticket'),
    path('tickets/<int:pk>/supprimer/', views.supprimer_ticket, name='supprimer_ticket'),
]
