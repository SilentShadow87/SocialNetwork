from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
import requests
from rest_framework.validators import UniqueValidator

from .models import ProfileModel, PostModel


UserModel = get_user_model()

def validate_email(email):
	result = False
	allowed_states = ['deliverable', 'risky']
	api_key = settings.EMAILHUNTER['API_KEY']
	endpoint = settings.EMAILHUNTER['ENDPOINT']

	params = {
			'email': email,
			'api_key': api_key
		}

	try:
		response = requests.get(endpoint, params=params)
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
		password = validated_data.pop('password')
		user = UserModel(**validated_data)

		user.set_password(password)
		user.save()

		return user


class ProfileSerializer(serializers.ModelSerializer):
	user = UserSerializer()

	class Meta:
		model = ProfileModel
		fields = ['user', 'company']
		read_only_fields = ['company',]

	def create(self, validated_data):
		user_data = validated_data.pop('user')
		additional_data = self.get_additional_data(user_data['email'])
		user_data.update(additional_data['user_data'])

		user = UserSerializer().create(validated_data=user_data)
		profile = ProfileModel.objects.create(user=user, **additional_data['other'])

		return profile

	def get_additional_data(self, email):
		result = {
				'user_data': {},
				'other': {}
			}

		endpoint = settings.CLEARBIT['ENDPOINT']
		params = {'email': email}
		options = {'auth': (settings.CLEARBIT['API_KEY'], '')}

		try:
		    response = requests.get(endpoint, params=params, **options)
		    response.raise_for_status()

		except requests.exceptions.HTTPError:
			pass

		else:
			data = response.json()
			if 'person' in data:
				result['user_data']['first_name'] = data['person']['name']['givenName']
				result['user_data']['last_name'] = data['person']['name']['familyName']

			if 'company' in response:
				result['other']['company_name'] = data['company']['name']

		return result


class PostListSerializer(serializers.ModelSerializer):
	class Meta:
		model = PostModel
		fields = '__all__'


class PostCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = PostModel
		fields = ['title', 'body']

