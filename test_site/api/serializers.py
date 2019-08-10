from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import Post

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = ['username', 'email', 'password']
		write_only_fields = ['password']

	def create(self, validated_data):
		user = UserModel(
		    email=validated_data['email'],
			username=validated_data['username']
		)
		user.set_password(validated_data['password'])
		user.save()
		return user


class PostListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Post
		fields = '__all__'

class PostCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Post
		fields = ['title', 'body']

