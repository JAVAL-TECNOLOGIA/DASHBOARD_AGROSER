from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import *

urlpatterns = [
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('logout/', login_required(logoutUser) , name='logout'),
] 
