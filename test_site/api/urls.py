from django.urls import path, include, re_path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


app_name = 'api'
urlpatterns = [
	path('user/list', views.ProfileListAPIView.as_view(), name='register'),
	path('user/create', views.ProfileCreateAPIView.as_view(), name='register'),
	path('post/list', views.PostListAPIView.as_view(), name='post_list'),
	path('post/create', views.PostCreateAPIView.as_view(), name='post_create'),
	re_path('^post/(?P<pk>\d+)/$', views.PostDetailAPIView.as_view(), name='post_detail'),
	re_path('^post/like/(?P<pk>\d+)/$', views.PostLikeAPIView.as_view(), name='post_like'),
	re_path('^post/unlike/(?P<pk>\d+)/$', views.PostUnlikeAPIView.as_view(), name='post_unlike'),
	path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
