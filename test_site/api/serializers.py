from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
import requests
from rest_framework.validators import UniqueValidator

from .models import ProfileModel, PostModel


# get default user model
UserModel = get_user_model()

def validate_email(email):
	"""Validate email using hunter.io API."""
	result = False
	allowed_states = ['deliverable', 'risky'] # risky is set for testing purpose. In production mode, only deliverable state should be used.
	api_key = settings.EMAILHUNTER['API_KEY']
	endpoint = settings.EMAILHUNTER['ENDPOINT']

	# prepare request params
	params = {
		'email': email,
		'api_key': api_key
	}

	# send request to hunter.io API for email verification.
	try:
		response = requests.get(endpoint, params=params)
		response.raise_for_status()

	except requests.exceptions.HTTPError as error:
		# check if number of requests limit is reached
		if response.status_code == 429:
			if settings.DEBUG:
				# set result to true for testing purpose
				result = True

			else:
				raise serializers.ValidationError("The service is currently unable to check your data. Please try lather.")

	else:
		# extract email state from response
		data = response.json()['data']
		if data['result'] in allowed_states:
			result = True

	if not result:
		raise serializers.ValidationError("This email address can't be used.")

	return email


class PostListSerializer(serializers.ModelSerializer):
	"""
	    Class used for serializing posts.
	"""
	class Meta:
		model = PostModel
		fields = '__all__'


class PostCreateSerializer(serializers.ModelSerializer):
	"""
	    Class Used for deserializing post data.
	"""
	class Meta:
		model = PostModel
		fields = ['title', 'body']


class UserSerializer(serializers.ModelSerializer):
	"""
	    Class used for both, serializing and deserializing users data.
	"""
	# add custom validators for cheking email address
	email = serializers.EmailField(
		    validators=[
				UniqueValidator(queryset=UserModel.objects.all()),
				validate_email
			]
		)

	class Meta:
		model = UserModel
		fields = ['username', 'email', 'password']
		extra_kwargs = {
				'password': {'write_only': True}
			}

	def create(self, validated_data):
		"""Hash user password before saving user."""
		password = validated_data.pop('password')
		user = UserModel(**validated_data)

		# set hashed password
		user.set_password(password)
		user.save()

		return user


class ProfileSerializer(serializers.ModelSerializer):
	"""
	    Class used for both, serializing and deserializing profile data.
	"""
	# define fields custom serializers
	user = UserSerializer()
	blog_posts = PostListSerializer(many=True, read_only=True)

	class Meta:
		model = ProfileModel
		fields = ['id', 'user', 'blog_posts', 'liked_posts', 'company']
		read_only_fields = ['id', 'company', 'liked_posts', 'blog_posts']

	def create(self, validated_data):
		"""Create user first, and related profile after that."""
		# get additional data for profile
		user_data = validated_data.pop('user')
		additional_data = self.get_additional_data(user_data['email'])
		user_data.update(additional_data['user_data'])

		# create related instances of user and profile
		user = UserSerializer().create(validated_data=user_data)
		profile = ProfileModel.objects.create(user=user, **additional_data['other'])

		return profile

	def get_additional_data(self, email):
		"""Get additional data of the user using clearbit.com API."""
		result = {
				'user_data': {},
				'other': {}
			}

		# prepare request
		endpoint = settings.CLEARBIT['ENDPOINT']
		params = {'email': email}
		options = {'auth': (settings.CLEARBIT['API_KEY'], '')}

		# send request to clearbit.com API.
		try:
			response = requests.get(endpoint, params=params, **options)
			response.raise_for_status()

		except requests.exceptions.HTTPError:
			pass

		else:
			# get additional user data from response
			data = response.json()
			if data['person'] is not None:
				result['user_data']['first_name'] = data['person']['name']['givenName']
				result['user_data']['last_name'] = data['person']['name']['familyName']

			if data['company'] is not None:
				result['other']['company'] = data['company']['name']

		return result
