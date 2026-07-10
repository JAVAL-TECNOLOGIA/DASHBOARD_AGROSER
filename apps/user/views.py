from django.contrib.messages.api import success
from django.db.models import fields
from django.http import response
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.urls import reverse_lazy
from django.views.generic import View, CreateView, UpdateView, ListView, DeleteView
from django.views.generic.base import TemplateView
from .forms import FormUser, FormUserUpdate, FormUpdatePassword
from .models import User
# Create your views here.

class HomeUser(TemplateView):
    template_name = 'user/list_user.html'



class ListUser(View):
    model = User

    def get_queryset(self):
        return self.model.objects.all().order_by('id').reverse()

    def get(self, request,*args, **kwargs):
        data_json = []
        for data in self.get_queryset():
            data_json.append({'pk':data.pk, 'email':data.email, 'username':data.username, 'first_name':data.first_name, 'last_name':data.last_name,'active':data.active})
        print(data_json)
        return JsonResponse(data_json, safe=False)


class CreateUser(CreateView):
    model = User
    form_class = FormUser
    template_name = 'user/create_user.html'
    
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = self.form_class(request.POST)
            if form.is_valid():
                new_user = User(
                    email = form.cleaned_data.get('email'),
                    username = form.cleaned_data.get('username'),
                    first_name = form.cleaned_data.get('first_name'),
                    last_name = form.cleaned_data.get('last_name')
                )
                new_user.set_password(form.cleaned_data.get('password1'))
                new_user.save()
                mensaje = f'{self.model.__name__} registrado correctamente'
                error  = 'No hubo error al momento de registrar un usuario'
                response = JsonResponse({'mensaje':mensaje, 'error':error})
                response.status_code = 201
                return response
            else :
                mensaje = f'{self.model.__name__} no se ha podido registrar'
                error  = form.errors
                response = JsonResponse({'mensaje':mensaje, 'error':error})
                response.status_code = 400
                return response
        else:
            return redirect('home_user')


class UpdateUser(UpdateView):
    model = User
    form_class = FormUserUpdate
    template_name = 'user/update_user.html'

    def post(self, request, *args, **kwargs) :
        if request.is_ajax():
            form = self.form_class(request.POST, instance = self.get_object())
            if form.is_valid():
                form.save()
                mensaje = f'{self.model.__name__} actualizado correctamente'
                error  = 'No hubo error al momento de registrar un usuario'
                response = JsonResponse({'mensaje':mensaje, 'error':error})
                response.status_code = 201
                return response
            else :
                mensaje = f'{self.model.__name__} no se ha podido actualizar'
                error  = form.errors
                response = JsonResponse({'mensaje':mensaje, 'error':error})
                response.status_code = 400
                return response
        else:
            return redirect('home_user')

class UpdatePassword(UpdateView):

    model = User
    form_class = FormUpdatePassword
    template_name = 'user/update_password.html'

    def post(self, request, *args, **kwargs) :
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = self.form_class(request.POST, instance = self.get_object())
            if form.is_valid():
                form.save()
                mensaje = f'{self.model.__name__} actualizado correctamente'
                error  = 'No hubo error al momento de registrar un usuario'
                response = JsonResponse({'mensaje':mensaje, 'error':error})
                response.status_code = 201
                return response
            else :
                mensaje = f'{self.model.__name__} no se ha podido actualizar'
                error  = form.errors
                response = JsonResponse({'mensaje':mensaje, 'error':error})
                response.status_code = 400
                return response
        else:
            return redirect('home')