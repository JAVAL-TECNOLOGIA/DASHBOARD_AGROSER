from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import  BaseUserManager, AbstractBaseUser, PermissionsMixin



class UserManager(BaseUserManager):

    def create_user(self, username, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('El usuario debe un correo electrónico')
        
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, first_name, last_name, password):
        user = self.create_user(
            email = email, 
            username = username,
            first_name = first_name,
            last_name = last_name, 
            password = password
        )
        user.admin = True
        user.save()
        return user




class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField('Username', max_length=50, unique=True)
    first_name = models.CharField('First name', max_length=50)
    last_name = models.CharField('Last name', max_length=50)
    email = models.EmailField('Email', max_length=100, unique=True)
    active = models.BooleanField(default=True)
    admin = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','first_name','last_name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' '

    @property
    def is_staff(self):
        return self.admin



