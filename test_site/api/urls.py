from django.urls import path, include, re_path
from . import views


app_name = 'api'
urlpatterns = [
	path('register', views.UserCreateAPIView.as_view(), name='register'),
	path('posts/', views.PostListAPIView.as_view(), name='post_list'),
	path('post/create', views.PostCreateAPIView.as_view(), name='post_create')
]
