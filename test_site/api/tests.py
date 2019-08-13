import random
import string
import lorem

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from .models import PostModel, ProfileModel


UserModel = get_user_model()

def create_random_string(size=16, chars=string.ascii_letters + string.digits):
	"""Create random string of the given size."""
	return ''.join(random.choice(chars) for _ in range(size))

def create_random_email():
	"""Create random email."""
	return create_random_string(size=8) + '@example.com'

def create_random_password():
	"""Create random password."""
	chars=string.ascii_letters + string.digits + string.punctuation
	return create_random_string(chars=chars)

def create_random_title():
	"""Create random post title."""
	chars=string.ascii_letters + string.digits + ' '
	return create_random_string(size=12, chars=chars)

def create_random_text():
	"""Generate random lorem ipsum text."""
	return lorem.text()


class ModelTestCase(TestCase):
	def setUp(self):
		"""Define test variables."""
		self.username = create_random_string()
		self.password = create_random_password()
		self.email = create_random_email()
		self.post_title = create_random_title()
		self.post_text = create_random_text()

	def test_model_can_create(self):
		"""Test whether models can create instances."""
		user = UserModel(username=self.username, password=self.password, email=self.email)
		user.save()

		profile = ProfileModel(user=user)

		profile_old_count = ProfileModel.objects.count()
		profile.save()
		profile_new_count = ProfileModel.objects.count()

		post = PostModel(author=profile, title=self.post_title, body=self.post_text)

		post_old_count = PostModel.objects.count()
		post.save()
		post_new_count = PostModel.objects.count()

		# check if instances are created
		self.assertNotEqual(profile_old_count, profile_new_count)
		self.assertNotEqual(post_old_count, post_new_count)


@override_settings(DEBUG=True)
class APITestCase(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.users = {}

	def _test_user_register(self):
		"""Test whether user can be register through API."""
		username = create_random_string()
		password = create_random_password()
		email = create_random_email()

		data = {
			'user': {
				'username': username,
				'password': password,
				'email': email
			}
		}

		response = self.client.post(reverse('api:user_register'), data, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		return username, password

	def _test_user_login(self, username, password):
		data = {
			'username': username,
			'password': password
		}

		response = self.client.post(reverse('api:user_login'), data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		return response.json()['access']

	def _test_post_create(self, access_key):
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_key)

		data = {
			'title': create_random_title(),
			'body': create_random_text()
		}

		response = self.client.post(reverse('api:post_create'), data, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_all(self):
		username, password = self._test_user_register()
		access_key = self._test_user_login(username, password)
		self._test_post_create(access_key)
