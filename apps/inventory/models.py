from django.db import models

# Create your models here.
class Sucursal(models.Model):
    descripcion = models.CharField('Descripcion', max_length=50)
    fecha_creacion = models.DateTimeField('Fecha creacion', auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha actualización', auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"

    def __str__(self):
        return self.descripcion





class Area(models.Model):
    descripcion = models.CharField('Descripcion', max_length=50)
    fecha_creacion = models.DateTimeField('Fecha creacion', auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha actualización', auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"

    def __str__(self):
        return self.descripcion





class Usuario(models.Model):
    nombres = models.CharField('Nombres', max_length=50)
    apellidos = models.CharField('Apellidos', max_length=50)
    correo = models.EmailField('Correo', max_length=50)
    celular = models.CharField('Celular', max_length=20)
    fecha_creacion = models.DateTimeField('Fecha creacion', auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha actualización', auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.nombres, ' ', self.apellidos





class Categoria(models.Model):
    descripcion = models.CharField('Descripción', max_length=50)
    fecha_creacion = models.DateTimeField('Fecha creacion', auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha actualización', auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.descripcion





class Marca(models.Model):
    descripcion = models.CharField('Descripcion', max_length=50)
    fecha_creacion = models.DateTimeField('Fecha creacion', auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha actualización', auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"

    def __str__(self):
        return self.descripcion





class Modelo(models.Model):
    descripcion = models.CharField('Descripcion', max_length=50)
    fecha_creacion = models.DateTimeField('Fecha creacion', auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha actualización', auto_now=True, auto_now_add=False)
    
    class Meta:
        verbose_name = "Modelo"
        verbose_name_plural = "Modelos"

    def __str__(self):
        return self.descripcion
        



class Procesador(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    serie = models.CharField('Serie', max_length=50)
    gama = models.CharField('Gama', max_length=50)
    generacion = models.CharField('Generación', max_length=50)
    frecuencia = models.CharField('Frecuencia', max_length=50)
    fecha_creacion = models.DateTimeField('Fecha creacion', auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha actualización', auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = "Procesador"
        verbose_name_plural = "Procesadores"

    def __str__(self):
        return self.componente, ' ', self.gama, ' ', self.generacion, ' ', self.frecuencia




class Ram(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    serie = models.CharField('Serie', max_length=50)
    tamaño = models.SmallIntegerField('Tamaño (GB)')
    fecha_creacion = models.DateTimeField('Fecha creacion', auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha actualización', auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = "Ram"
        verbose_name_plural = "Ram"

    def __str__(self):
        return self.marca +' ' +self.modelo+' '+ self.serie



    
    
class Disco(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    serie = models.CharField('Serie', max_length=50)
    tamaño = models.SmallIntegerField('Tamaño (GB)')
    tipo = models.CharField('Tipo', max_length=50)
    fecha_creacion = models.DateTimeField('Fecha creacion', auto_now=False, auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha actualización', auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = "Disco"
        verbose_name_plural = "Disco"

    def __str__(self):
        return self.marca, ' ', self.modelo, ' ', self.serie, ' ', self.tipo, ' ', self.tamaño





class CPU(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    serie = models.CharField('Serie', max_length=50)
    procesador = models.ForeignKey(Procesador, on_delete=models.CASCADE)
    ram = models.ForeignKey(Ram, on_delete=models.CASCADE)
    disco = models.ForeignKey(Disco, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "CPU"
        verbose_name_plural = "CPU"

    def __str__(self):
        return self.marca +' ' +self.modelo+' '+ self.serie





class Monitor(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    serie = models.CharField('Serie', max_length=50)
    tipo =  models.CharField('Tipo', max_length=50)
    tamaño = models.CharField('Tamaño', max_length=50)
    cableado = models.CharField('Cableado', max_length=50)

    class Meta:
        verbose_name = "Monitor"
        verbose_name_plural = "Monitors"

    def __str__(self):
        return self.marca +' ' +self.modelo+' '+ self.serie




class Mouse(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    serie = models.CharField('Serie', max_length=50)
    tipo =  models.CharField('Tipo', max_length=50)

    class Meta:
        verbose_name = "Mouse"
        verbose_name_plural = "Mouse"

    def __str__(self):
        return self.marca +' ' +self.modelo+' '+ self.serie





class Teclado(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    serie = models.CharField('Serie', max_length=50)
    tipo =  models.CharField('Tipo', max_length=50)

    class Meta:
        verbose_name = "Teclado"
        verbose_name_plural = "Teclado"

    def __str__(self):
        return self.marca +' ' +self.modelo+' '+ self.serie




class Audifonos(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    serie = models.CharField('Serie', max_length=50)

    class Meta:
        verbose_name = "Teclado"
        verbose_name_plural = "Teclado"

    def __str__(self):
        return self.marca +' ' +self.modelo+' '+ self.serie






class CamaraWeb():
    pass





class Celular():
    pass



class PDA():
    pass



class Lectores():
    pass



class Camaras():
    pass