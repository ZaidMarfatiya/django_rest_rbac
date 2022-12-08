from django.urls import path
from rest_app.views import UserRegistrationView, UserLoginView, UserChangePasswordView, EditedProfileView


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('edited-profile/', EditedProfileView.as_view(), name='edited-profile')
]