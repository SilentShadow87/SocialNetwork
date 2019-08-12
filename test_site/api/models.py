from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver


# Create your models here.
class ProfileModel(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	company = models.CharField(max_length=30, blank=True)


class PostModel(models.Model):
	title = models.CharField(max_length=250)
	slug = models.SlugField(max_length=250, unique_for_date='publish')
	author = models.ForeignKey(ProfileModel, related_name='blog_posts', on_delete=models.CASCADE)
	body = models.TextField()
	likes = models.ManyToManyField(ProfileModel, related_name='liked_posts', blank=True)
	publish = models.DateTimeField(default=timezone.now)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.title
