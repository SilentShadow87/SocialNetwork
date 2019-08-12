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

		self.create_users(self._config['number_of_users'])
		self.create_posts()
		self.perform_posts_likes()

	def create_random_string(self, size=16, chars=string.ascii_letters + string.digits):
		return ''.join(random.choice(chars) for _ in range(size))

	def create_random_email(self):
		return self.create_random_string(size=8) + '@testingpurpose.com'

	def create_random_password(self):
		chars=string.ascii_letters + string.digits + string.punctuation
		return self.create_random_string(chars=chars)

	def create_random_title(self):
		chars=string.ascii_letters + string.digits + ' '
		return self.create_random_string(size=12, chars=chars)

	def create_random_text(self):
		return lorem.text()

	def send_request(self, path, method='get', params=None, headers=None):
		result = None
		request_kwargs = {}
		endpoint = self._config['server']['domain'] + path

		if params:
			if method == 'get':
				request_kwargs['params'] = params

			elif method == 'post':
				request_kwargs['data'] = params

		request_kwargs['headers'] = {'Content-type': 'application/json'}
		if headers:
			request_kwargs['headers'].update(headers)

		try:
			response = getattr(requests, method)(endpoint, **request_kwargs)
			response.raise_for_status()

		except requests.exceptions.HTTPError as error:
			print(error)

		else:
			result = response.json()

		return result

	def login_user(self, username, password):
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
		user_credentials = self._credentials[username]

		access_key = user_credentials.get('access_key')
		if access_key is None:
			password = user_credentials['password']
			access_key = self.login_user(username, password)
			user_credentials['access_key'] = access_key

		return access_key

	def get_users(self):
		path = self._config['server']['api_paths']['user_list']

		return self.send_request(path)

	def create_users(self, number_of_users):
		path = self._config['server']['api_paths']['user_create']

		for _ in range(number_of_users):
			username = self.create_random_string()
			password = self.create_random_password()
			email = self.create_random_email()

			data = {
				'user': {
					'username': username,
					'email': email,
					'password': password
				}
			}

			user_data = self.send_request(path, method='post', params=json.dumps(data))
			if user_data is not None:
				self._credentials[username] = {'password': password}

	def create_posts(self):
		path = self._config['server']['api_paths']['post_create']
		for username in self._credentials:
			access_key = self.get_access_key(username)
			if access_key is None:
				continue

			headers = {'Authorization': 'Bearer {}'.format(access_key)}

			number_of_posts = random.randrange(1, self._config['max_posts_per_user'] + 1)

			for _ in range(number_of_posts):
				post_title = self.create_random_title()
				post_text = self.create_random_text()

				data = {
					'title': post_title,
					'body': post_text
				}

				self.send_request(path, method='post', params=json.dumps(data), headers=headers)

	def like_post(self, user, post):
		path = self._config['server']['api_paths']['post_like'].format(post['id'])
		access_key = self.get_access_key(user['user']['username'])
		if access_key is None:
				return

		headers = {'Authorization': 'Bearer {}'.format(access_key)}
		self.send_request(path, headers=headers)

	def filter_user(self, user):
		return not all(post['likes'] for post in user['blog_posts'])

	def perform_posts_likes(self):
		max_likes_per_user = self._config['max_likes_per_user']
		all_users = self.get_users()
		stop = False

		sort_user_list = sorted(all_users, key=lambda user: len(user['blog_posts']))

		for next_user in sort_user_list:
			likes_count = len(next_user['liked_posts'])

			while likes_count < max_likes_per_user:
				allowed_authors = list(filter(self.filter_user, all_users))

				if not allowed_authors:
					return

				for author in allowed_authors:
					if author['id'] == next_user['id']:
						allowed_authors.remove(author)

				if not allowed_authors:
					all_users = self.get_users()
					break

				author = None
				while not author:
					random_author = random.choice(allowed_authors)
					blog_posts = random_author['blog_posts']
					blog_posts = list(filter(lambda post: next_user['id'] not in post['likes'], blog_posts))

					if not blog_posts:
						allowed_authors.remove(random_author)
						continue

					author = random_author

				random_post = random.choice(blog_posts)

				self.like_post(next_user, random_post)

				all_users = self.get_users()
				likes_count = len([user for user in all_users if user['id'] == next_user['id']][0]['liked_posts'])

if __name__ == '__main__':
	Bot()
