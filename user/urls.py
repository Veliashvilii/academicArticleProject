from django.urls import path
from . import views

urlpatterns = [
  path('', views.user_logout, name='show_logout'),
  path('profile', views.user_profile, name='show_profile'),
]