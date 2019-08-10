from django.shortcuts import render
from django.contrib.auth import get_user_model

from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .serializers import UserCreateSerializer, PostListSerializer, PostCreateSerializer
from .models import Post

UserModel = get_user_model()

# Create your views here.
class UserCreateAPIView(CreateAPIView):
	permission_classes = [AllowAny]
	serializer_class = UserCreateSerializer
	queryset = UserModel.objects.all()

class PostListAPIView(ListAPIView):
	serializer_class = PostListSerializer
	queryset = Post.objects.all()

class PostCreateAPIView(CreateAPIView):
	serializer_class = PostCreateSerializer
	queryset = Post.objects.all()

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)
