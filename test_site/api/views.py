from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView

from .serializers import UserCreateSerializer


UserModel = get_user_model()

# Create your views here.
class UserCreateAPIView(CreateAPIView):
	serializer_class = UserCreateSerializer
	queryset = UserModel.objects.all()
