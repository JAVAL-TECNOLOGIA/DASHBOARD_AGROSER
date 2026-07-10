from django.urls import path
from .views import  Inventory

urlpatterns = [    

	path('inventory/', Inventory.as_view(), name='inventory'),

]