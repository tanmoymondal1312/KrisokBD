from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('profiles/', views.profile_list, name='profile_list'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),
    path('profile/<str:username>/rate/', views.rate_user, name='rate_user'),
]
