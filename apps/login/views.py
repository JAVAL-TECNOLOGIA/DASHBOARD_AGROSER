from django.forms.forms import Form
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import LoginForm




class LoginView(FormView):
    template_name = 'login/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(LoginView, self).dispatch(request, *args, **kwargs)
    

    def form_valid(self, form):
        login(self.request, form.get_user())
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return redirect(next_url)
        return super(LoginView, self).form_valid(form)
    

def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/accounts/login/')
