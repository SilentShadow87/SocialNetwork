from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
import requests
from rest_framework.validators import UniqueValidator

from .models import Post

UserModel = get_user_model()

def validate_email(email):
	result = False
	allowed_states = ['deliverable', 'risky']
	api_key = settings.EMAILHUNTER_KEY
	url = 'https://api.hunter.io/v2/email-verifier'

	params = {
			'email': email,
			'api_key': api_key
		}

	try:
		response = requests.get(url, params=params)
		response.raise_for_status()

	except requests.exceptions.HTTPError:
		pass

	else:
		data = response.json()['data']
		if data['result'] in allowed_states:
			result = True

	if not result:
		raise serializers.ValidationError("This email address can't be used.")

	return email


class UserSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(validators=[
									UniqueValidator(queryset=UserModel.objects.all()),
									validate_email
								])
	class Meta:
		model = UserModel
		fields = ['username', 'email', 'password']
		extra_kwargs = {
				'password': {'write_only': True}
			}

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

