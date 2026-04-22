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
    path('api/tickets/', views.api_tickets_list, name='api_tickets'),
    path('api/tickets/creer/', views.api_creer_ticket, name='api_creer_ticket'),
    path('api/tickets/<int:pk>/', views.api_ticket_detail, name='api_ticket_detail'),
    path('api/tickets/<int:pk>/modifier/', views.api_modifier_ticket, name='api_modifier_ticket'),
    path('api/tickets/<int:pk>/supprimer/', views.api_supprimer_ticket, name='api_supprimer_ticket'),
    path('api/stats/', views.api_stats, name='api_stats'),
]
