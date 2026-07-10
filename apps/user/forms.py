from django import forms
from django.forms import fields
from .models import User

class FormUser(forms.ModelForm):

    password1= forms.CharField(label='Contraseña', widget = forms.PasswordInput(
        attrs= {
            'class' : 'form-control',
            'placeholder' : 'Contraseña',
            'id' : 'idPassword',
            'required' : 'required'
        }
    ))

    password2 = forms.CharField(label='Confirmar Contraseña', widget = forms.PasswordInput(
         attrs= {
            'class' : 'form-control',
            'placeholder' : 'Repetir contraseña',
            'id' : 'idPasswordConfirm',
            'required' : 'required'
        }
    ))


    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder' : 'Correo'
                }
            ),
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder' : 'Usuario'
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder' : 'Nombre'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder' : 'Apellido'
                }
            ),
        }
    
    def clean_password2(self):
        print(self.cleaned_data)
        password1= self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')   
        
        if password1!= password2 :
            raise forms.ValidationError('Las contraseñas no coinciden')
        return password2
    
    def save(self, commit = True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
        return user


class FormUserUpdate(forms.ModelForm):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder' : 'Correo'
                }
            ),
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder' : 'Usuario'
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder' : 'Nombre'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder' : 'Apellido'
                }
            ),
        }


class FormUpdatePassword(forms.ModelForm):

    password1= forms.CharField(label='Contraseña', widget = forms.PasswordInput(
        attrs= {
            'class' : 'form-control',
            'placeholder' : 'Nueva contraseña',
            'id' : 'idPassword1',
            'required' : 'required',
        }
    ))

    password2 = forms.CharField(label='Confirmar Contraseña', widget = forms.PasswordInput(
         attrs= {
            'class' : 'form-control',
            'placeholder' : 'Repetir contraseña',
            'id' : 'idPassword2',
            'required' : 'required',
        }
    ))

    class Meta:
        model = User
        fields = ('username',)
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder' : 'Usuario',
                    'readonly' : 'readonly'
                }
            )
        }
          

    def clean_password2(self):
        password1= self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')   
        
        if password1 != password2 :
            raise forms.ValidationError('Las contraseñas no coinciden')
        return password2

    def save(self, commit = True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
        return user
    