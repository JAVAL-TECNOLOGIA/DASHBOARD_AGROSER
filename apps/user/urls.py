from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import HomeUser, CreateUser, ListUser, UpdateUser, UpdatePassword

urlpatterns = [
    path('home_user/', login_required(HomeUser.as_view()), name='home_user'),
    path('create_user/', login_required(CreateUser.as_view()), name='create_user'),
    path('list_user/', login_required(ListUser.as_view()), name='list_user'),
    path('update_user/<int:pk>/', login_required(UpdateUser.as_view()), name='update_user'),
    path('update_password/<int:pk>/', login_required(UpdatePassword.as_view()), name='update_password')
    
]