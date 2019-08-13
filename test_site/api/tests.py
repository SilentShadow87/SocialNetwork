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

	def _test_user_register(self, username, password, email, status_code=status.HTTP_201_CREATED):
		"""Test whether user can be register through API."""
		data = {
			'user': {
				'username': username,
				'password': password,
				'email': email
			}
		}

		response = self.client.post(reverse('api:user_register'), data, format='json')
		self.assertEqual(response.status_code, status_code)

	def _test_user_list(self):
		response = self.client.get(reverse('api:user_list'))
		user_list = response.json()
		self.assertEqual(len(user_list), ProfileModel.objects.count())

		for user in user_list:
			user_id = user['id']
			self.assertTrue(ProfileModel.objects.filter(pk=user_id).exists())

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

	def _test_post_list(self):
		response = self.client.get(reverse('api:post_list'))
		post_list = response.json()
		self.assertEqual(len(post_list), PostModel.objects.count())

		for post in post_list:
			post_id = post['id']
			self.assertTrue(PostModel.objects.filter(pk=post_id).exists())

		return post_id

	def _test_post_like(self, access_key, post_id, status_code=status.HTTP_200_OK):
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_key)
		response = self.client.get(reverse('api:post_like', args=[post_id,]))
		self.assertEqual(response.status_code, status_code)

	def _test_post_unlike(self, access_key, post_id, status_code=status.HTTP_200_OK):
		self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_key)
		response = self.client.get(reverse('api:post_unlike', args=[post_id,]))
		self.assertEqual(response.status_code, status_code)

	def test_all(self):
		# generate data for users
		username1 = create_random_string()
		password1 = create_random_password()
		email1 = create_random_email()
		username2 = create_random_string()
		password2 = create_random_password()
		email2 = create_random_email()

		# register and login user1
		self._test_user_register(username1, password1, email1)
		access_key1 = self._test_user_login(username1, password1)

		# try to register user1 again
		self._test_user_register(username1, password1, email1, status_code=status.HTTP_400_BAD_REQUEST)

		# register and login user2
		self._test_user_register(username2, password2, email2)
		access_key2 = self._test_user_login(username2, password2)

		# test user list
		self._test_user_list()

		# test post create
		self._test_post_create(access_key1)

		# test post list
		post_id = self._test_post_list()

		# user1 try to like their own post
		self._test_post_like(access_key1, post_id, status_code=status.HTTP_400_BAD_REQUEST)

		# user1 try to unlike their own post
		self._test_post_unlike(access_key1, post_id, status_code=status.HTTP_400_BAD_REQUEST)

		# reset client credentials
		self.client.credentials()

		# test user2 like user1 post
		self._test_post_like(access_key2, post_id)

		# test user2 tries to like same post again
		self._test_post_like(access_key2, post_id, status_code=status.HTTP_400_BAD_REQUEST)

		# test user2 unlike user1 post
		self._test_post_unlike(access_key2, post_id)

