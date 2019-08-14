import os
import sys
import json
import lorem
import requests
import string
import random


class Bot:
	def __init__(self):
		self._path = os.path.abspath(os.path.dirname(__file__))
		self._credentials = {}

		# load configuration file
		with open(os.path.join(self._path, 'config.json'), 'r') as raw_file:
			try:
				self._config = json.load(raw_file)

			except json.decoder.JSONDecodeError:
				sys.exit('Malformed config file.')

		self.register_users(self._config['number_of_users'])
		self.create_posts()
		self.perform_posts_likes()

	def create_random_string(self, size=16, chars=string.ascii_letters + string.digits):
		"""Create random string of the given size."""
		return ''.join(random.choice(chars) for _ in range(size))

	def create_random_email(self):
		"""Create random email."""
		return self.create_random_string(size=8) + '@example.com'

	def create_random_password(self):
		"""Create random password."""
		chars=string.ascii_letters + string.digits + string.punctuation
		return self.create_random_string(chars=chars)

	def create_random_title(self):
		"""Create random post title."""
		chars=string.ascii_letters + string.digits + ' '
		return self.create_random_string(size=12, chars=chars)

	def create_random_text(self):
		"""Generate random lorem ipsum text."""
		return lorem.text()

	def send_request(self, path, method='get', params=None, headers=None):
		"""Method that performs request of the given type to the specified path."""
		result = None
		request_kwargs = {}
		endpoint = self._config['server']['domain'] + path

		# prepare request
		if params:
			if method == 'get':
				request_kwargs['params'] = params

			elif method == 'post':
				request_kwargs['data'] = params

		request_kwargs['headers'] = {'Content-type': 'application/json'}
		if headers:
			request_kwargs['headers'].update(headers)

		# send request and catch response
		try:
			response = getattr(requests, method)(endpoint, **request_kwargs)
			response.raise_for_status()

		except requests.exceptions.HTTPError as error:
			print(error)

		else:
			result = response.json()

		return result

	def login_user(self, username, password):
		"""Login user and return access key"""
		result = None
		path = self._config['server']['api_paths']['user_login']
		data = {
			'username': username,
			'password': password
		}

		response = self.send_request(path, method='post', params=json.dumps(data))
		if response is not None:
			result = response['access']

		return result

	def get_access_key(self, username):
		"""Get access key from internal cache. If key not in cache, send login request."""
		# get access_key from cache
		user_credentials = self._credentials[username]
		access_key = user_credentials.get('access_key')

		if access_key is None:
			# login user and get access key
			password = user_credentials['password']
			access_key = self.login_user(username, password)

			# preserve access key
			user_credentials['access_key'] = access_key

		return access_key

	def get_users(self):
		"""Send reuest for the list of all users to the API."""
		# get appropriate path from the config
		path = self._config['server']['api_paths']['user_list']

		# send request and return response data
		return self.send_request(path)

	def register_users(self, number_of_users):
		"""Register users based on number specified in the configuration file."""
		print('Register users....')
		# get appropriate path from the config
		path = self._config['server']['api_paths']['user_register']

		# perform users registration
		for _ in range(number_of_users):
			# generate random user data
			username = self.create_random_string()
			password = self.create_random_password()
			email = self.create_random_email()

			# prepare data for request
			data = {
				'user': {
					'username': username,
					'email': email,
					'password': password
				}
			}

			# send request and return response data
			user_data = self.send_request(path, method='post', params=json.dumps(data))
			if user_data is not None:
				# save credentials
				self._credentials[username] = {'password': password}

		print('Register users done.')

	def create_posts(self):
		"""Performcreation of the posts."""
		print('Create posts...')
		# get appropriate path from the config
		path = self._config['server']['api_paths']['post_create']

		# perform post creation per user
		for username in self._credentials:
			# get access key
			access_key = self.get_access_key(username)
			if access_key is None:
				continue

			# prepare authorization header
			headers = {'Authorization': 'Bearer {}'.format(access_key)}

			# determine the number of post to be created
			number_of_posts = random.randrange(1, self._config['max_posts_per_user'] + 1)

			for _ in range(number_of_posts):
				# generate random post title and text
				post_title = self.create_random_title()
				post_text = self.create_random_text()

				# prepare data for request
				data = {
					'title': post_title,
					'body': post_text
				}

				# send request
				self.send_request(path, method='post', params=json.dumps(data), headers=headers)

		print('Create posts done.')

	def like_post(self, user, post):
		"""Perform post like."""
		# get appropriate path from the config
		path = self._config['server']['api_paths']['post_like'].format(post['id'])

		# get access key
		access_key = self.get_access_key(user['user']['username'])
		if access_key is None:
				return

		# prepare authorization header
		headers = {'Authorization': 'Bearer {}'.format(access_key)}

		# send request
		self.send_request(path, headers=headers)

	def has_unliked_posts(self, user):
		"""Method that determines if there are user posts that have not yet been liked."""
		return not all(post['likes'] for post in user['blog_posts'])

	def perform_posts_likes(self):
		"""Method that performs post liking."""
		print('Perform posts likes...')

		stop = False
		max_likes_per_user = self._config['max_likes_per_user']

		# get list of all users and sort it based on the number of the created posts
		all_users = self.get_users()
		sort_user_list = sorted(all_users, key=lambda user: len(user['blog_posts']))

		# determine next user
		for next_user in sort_user_list:
			likes_count = len(next_user['liked_posts'])

			while likes_count < max_likes_per_user:
				# determine users which posts can be liked
				allowed_authors = list(filter(self.has_unliked_posts, all_users))
				if not allowed_authors:
					stop = True
					break

				# disable the user to like his own post
				for author in allowed_authors:
					if author['id'] == next_user['id']:
						allowed_authors.remove(author)

				if not allowed_authors:
					# skip to the next user
					all_users = self.get_users()
					break

				# chouse random author
				random_author = random.choice(allowed_authors)
				blog_posts = random_author['blog_posts']

				# filter posts that next user can likes
				blog_posts = list(filter(lambda post: next_user['id'] not in post['likes'], blog_posts))

				# chouse random post
				random_post = random.choice(blog_posts)

				# perform post like
				self.like_post(next_user, random_post)

				# determine data for the nest iteration
				all_users = self.get_users()
				likes_count = len([user for user in all_users if user['id'] == next_user['id']][0]['liked_posts'])

			# check if bot should stop
			if stop:
				break

		print('Perform posts likes done.')

if __name__ == '__main__':
	Bot()
