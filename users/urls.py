from django.urls import path
from users.views import user_register

urlpatterns = [
    path('register/', user_register, name='user_register'),
]