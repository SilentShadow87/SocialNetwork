from django.contrib import admin
from .models import PostModel, ProfileModel

# Register your models here.
admin.site.register(ProfileModel)
admin.site.register(PostModel)
