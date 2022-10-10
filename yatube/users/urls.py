"""URL's for auth."""
from django.contrib.auth.views import LogoutView

from django.contrib.auth.views import LoginView

from django.contrib.auth.views import PasswordResetView

from django.contrib.auth.views import PasswordChangeView

from django.contrib.auth.views import PasswordChangeDoneView

from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'password_change/',
        PasswordChangeView.as_view(),
        name='password_change'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(),
        name='password_change_done'
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(),
        name='password_reset'
    ),
]
