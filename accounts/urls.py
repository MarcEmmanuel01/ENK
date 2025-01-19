from django.urls import path
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, 
    PasswordResetCompleteView, LoginView
)
from django.shortcuts import redirect
from .views import (
    profile,
    profile_update,
    change_password,
    registration_page,
    logout_view,
)
from .forms import EmailValidationOnForgotPassword

urlpatterns = [
    # Profile URLs
    path('profile/', profile, name='profile'),
    path('profile/edit/', profile_update, name='edit_profile'),
    path('profile/change-password/', change_password, name='change_password'),

    # Registration & Authentication URLs
    path('registration/', registration_page, name='register'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),  # Utilise la vue personnalisée logout_view

    # Redirect /accounts/ to /accounts/profile/
    path('', lambda request: redirect('profile'), name='accounts_home'),

    # Password reset URLs
    path('password-reset/', PasswordResetView.as_view(
        form_class=EmailValidationOnForgotPassword,
        template_name='accounts/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]
