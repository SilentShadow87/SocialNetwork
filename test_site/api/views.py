from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer, PostListSerializer, PostCreateSerializer, ProfileSerializer
from .models import ProfileModel, PostModel


# Create your views here.
class ProfileCreateAPIView(CreateAPIView):
	permission_classes = [AllowAny]
	serializer_class = ProfileSerializer
	queryset = ProfileModel.objects.all()


class ProfileListAPIView(ListAPIView):
	permission_classes = [AllowAny]
	serializer_class = ProfileSerializer
	queryset = ProfileModel.objects.all()


class PostListAPIView(ListAPIView):
	permission_classes = [AllowAny]
	serializer_class = PostListSerializer
	queryset = PostModel.objects.all()


class PostDetailAPIView(RetrieveAPIView):
	permission_classes = [AllowAny]
	serializer_class = PostListSerializer
	queryset = PostModel.objects.all()


class PostCreateAPIView(CreateAPIView):
	serializer_class = PostCreateSerializer
	queryset = PostModel.objects.all()

	def perform_create(self, serializer):
		"""Add current user to the serializer."""
		profile = get_object_or_404(ProfileModel, user=self.request.user)
		serializer.save(author=profile)


class PostLikeAPIView(APIView):
	def get(self, request, pk):
		"""Method that perform like on the given post."""
		# get appropriate post and user
		post = get_object_or_404(PostModel, pk=pk)
		profile = get_object_or_404(ProfileModel, user=self.request.user)

		# ban on liking your own posts
		if post.author == profile:
			message = {'message': 'User can not likes his own post.'}
			return Response(message, status=status.HTTP_400_BAD_REQUEST)

		# check whether is post already liked by the current user
		if profile in post.likes.all():
			message = {'message': 'User already liked this post.'}
			return Response(message, status=status.HTTP_400_BAD_REQUEST)

		# update data and return
		post.likes.add(profile)
		data = {'success': True}
		return Response(data, status=status.HTTP_200_OK)


class PostUnlikeAPIView(APIView):
	def get(self, request, pk):
		"""Method that perform unlike on the given post."""
		# get appropriate post and user
		post = get_object_or_404(PostModel, pk=pk)
		profile = get_object_or_404(ProfileModel, user=self.request.user)

		# update data and return
		post.likes.remove(profile)
		data = {'success': True}
		return Response(data, status=status.HTTP_200_OK)

