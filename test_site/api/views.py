from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer, PostListSerializer, PostCreateSerializer
from .models import Post

UserModel = get_user_model()

# Create your views here.
class UserCreateAPIView(CreateAPIView):
	permission_classes = [AllowAny]
	serializer_class = UserSerializer
	queryset = UserModel.objects.all()


class UserListAPIView(ListAPIView):
	serializer_class = UserSerializer
	queryset = UserModel.objects.all()


class PostListAPIView(ListAPIView):
	serializer_class = PostListSerializer
	queryset = Post.objects.all()


class PostDetailAPIView(RetrieveAPIView):
	serializer_class = PostListSerializer
	queryset = Post.objects.all()


class PostCreateAPIView(CreateAPIView):
	serializer_class = PostCreateSerializer
	queryset = Post.objects.all()

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)


class PostLikeAPIView(APIView):
	def get(self, request, pk):
		post = get_object_or_404(Post, pk=pk)
		user = self.request.user

		if user in post.likes.all():
			message = {'message': 'User already liked this post.'}
			return Response(message, status=status.HTTP_400_BAD_REQUEST)

		post.likes.add(user)
		return Response(status=status.HTTP_200_OK)


class PostUnlikeAPIView(APIView):
	def get(self, request, pk):
		post = get_object_or_404(Post, pk=pk)
		user = self.request.user

		post.likes.remove(user)
		return Response(status=status.HTTP_200_OK)

