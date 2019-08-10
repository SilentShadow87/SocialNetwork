from django.urls import path, include, re_path
from . import views


app_name = 'api'
urlpatterns = [
	path('user/list', views.UserListAPIView.as_view(), name='register'),
	path('user/create', views.UserCreateAPIView.as_view(), name='register'),
	path('post/list', views.PostListAPIView.as_view(), name='post_list'),
	path('post/create', views.PostCreateAPIView.as_view(), name='post_create')
]
