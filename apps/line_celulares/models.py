from django.db import models

class lineas_celulares(models.Model):
    item = models.CharField(max_length=50)
    nrocelular = models.CharField(max_length=15)
    nombres = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)

    def __str__(self):
        return self.nombres
