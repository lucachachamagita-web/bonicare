from django.urls import path
from loginmodule.views import auth_view
from django.contrib.auth import views as auth_views
from django.urls import re_path as url

urlpatterns = [
	path('auth', auth_view),
]
