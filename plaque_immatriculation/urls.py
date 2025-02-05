"""
URL configuration for plaque_immatriculation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from rootvibe import views
from django.contrib.auth import views as auth_views
     
urlpatterns = [
    # URLs de base
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    # URLs pour l'administrateur
    path('admine/users/', views.user_management, name='user_management'),
    path('admine/users/add/', views.add_user, name='add_user'),
    path('admine/users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('admine/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admine/reports/', views.reports, name='reports'),

    # URLs pour l'agent de terrain
    path('agent/search/', views.search_vehicle, name='search_vehicle'),
    path('agent/vehicle/<int:vehicle_id>/', views.vehicle_details, name='vehicle_details'),
    path('agent/vehicle/<int:vehicle_id>/add-infraction/', views.add_infraction, name='add_infraction'),
    path('agent/vehicle/<int:vehicle_id>/add-photo/', views.add_photo, name='add_photo'),
    path('agent/infractions/', views.list_infractions, name='list_infractions'),

    # URLs pour le propriétaire
    path('owner/', views.owner_portal, name='owner_portal'),
    path('owner/vehicle/<int:vehicle_id>/', views.owner_vehicle_details, name='owner_vehicle_details'),
    path('owner/infractions/', views.owner_infractions, name='owner_infractions'),

    # URLs supplémentaires
    path('contact/', views.contact, name='contact'),
    path('photos/', views.list_photos, name='list_photos'),
    path('photos/delete/<int:photo_id>/', views.delete_photo, name='delete_photo'),
    
    # URLs pour la plaque
    path("demande-plaque/", views.demander_plaque, name="demander_plaque"),
    path("demandes/", views.liste_demandes, name="liste_demandes"),
    path("approuver-demande/<int:demande_id>/", views.approuver_demande, name="approuver_demande"),

]

