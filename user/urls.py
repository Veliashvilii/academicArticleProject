from django.urls import path
from . import views

urlpatterns = [
  path('', views.user_logout, name='show_logout'),
  path('profile', views.user_profile, name='show_profile'),
  path('like_article/', views.like_article, name='like_article'),
  path('dislike_article/', views.dislike_article, name='dislike_article'),
  path('search/', views.user_search, name='user_search'),
]