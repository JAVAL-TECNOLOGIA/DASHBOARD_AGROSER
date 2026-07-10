from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.base import TemplateView

# Create your views here.
class Inventory(PermissionRequiredMixin, TemplateView):
 
    permission_required = 'user.aei_inventory'
    template_name = 'inventory/inventory.html'
    