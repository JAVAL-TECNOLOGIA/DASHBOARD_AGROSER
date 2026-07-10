from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy


class ValidatePermissionMixin(object):
    premission_required = ''
    url_redirect = None

    def get_perms(self):
        if isinstance(self.premission_required,str): return(self.premission_required)
        else : return self.premission_required

    def get_url_redirect(self):
        if self.url_redirect is None:
            return reverse_lazy('script')

    def dispatch(self, request, *args, **kwargs):
        if request.user.has_perms(self.get_perms()):
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, "No tiene permisos para realziar esta operación")
        return  redirect(self.get_url_redirect())