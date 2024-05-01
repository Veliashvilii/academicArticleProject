from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='show_main'),
  path('login', views.login, name='show_login'),
  path('signup/', views.index, name='show_signup'),
]