from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views.generic import View, TemplateView

# Create your views here.
class Advance(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_reports_pbi_gerencia'
    template_name = 'powerbi/advance.html'

# Create your views here.
class Billing(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_reports_pbi_gerencia'
    template_name = 'powerbi/billing.html'

class gre(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.gre'
    template_name = 'powerbi/gre.html'

# Create your views here.
class Costs(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_reports_pbi_gerencia'
    template_name = 'powerbi/costs.html'

# Create your views here.
class Thirds(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_reports_pbi_fundo'
    template_name = 'powerbi/thirds.html'

class Operations(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_reports_pbi_fundo'
    template_name = 'powerbi/operations.html'

class Prodplant(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_reports_pbi_fundo'
    template_name = 'powerbi/prodplant.html'


class manual( TemplateView):

    permission_required = 'manualti'
    template_name = 'powerbi/manual.html'
