from django.urls import path, include, re_path
from . import views


app_name = 'api'
urlpatterns = [
	path('register', views.UserCreateAPIView.as_view(), name='register'),
]
