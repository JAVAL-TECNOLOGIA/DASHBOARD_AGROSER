from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    CreateUser,
    DeleteUser,
    HomeUser,
    ListUser,
    ToggleUserAccess,
    UpdatePassword,
    UpdateUser,
)

urlpatterns = [
    path('home_user/', login_required(HomeUser.as_view()), name='home_user'),
    path('create_user/', login_required(CreateUser.as_view()), name='create_user'),
    path('list_user/', login_required(ListUser.as_view()), name='list_user'),
    path('update_user/<int:pk>/', login_required(UpdateUser.as_view()), name='update_user'),
    path('update_password/<int:pk>/', login_required(UpdatePassword.as_view()), name='update_password'),
    path('toggle_access/<int:pk>/', login_required(ToggleUserAccess.as_view()), name='toggle_user_access'),
    path('delete_user/<int:pk>/', login_required(DeleteUser.as_view()), name='delete_user'),
    
]
