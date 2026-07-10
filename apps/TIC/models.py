from django.db import models
from decimal import Decimal


class PDFFile(models.Model):
    file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


#tabla de presupuesto de  lubricantes y combustibles de Don Luis
class MaterialOficina(models.Model):
    id = models.AutoField(primary_key=True)
    idproducto = models.CharField(max_length=50, unique=True, verbose_name="ID Producto")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Unitario")
    
    # Campos para cada mes
    enero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Enero")
    enero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Enero")
    
    febrero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Febrero")
    febrero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Febrero")
    
    marzo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Marzo")
    marzo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Marzo")
    
    abril_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Abril")
    abril_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Abril")
    
    mayo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Mayo")
    mayo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Mayo")
    
    junio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Junio")
    junio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Junio")
    
    julio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Julio")
    julio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Julio")
    
    agosto_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Agosto")
    agosto_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Agosto")
    
    septiembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Septiembre")
    septiembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Septiembre")
    
    octubre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Octubre")
    octubre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Octubre")
    
    noviembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Noviembre")
    noviembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Noviembre")
    
    diciembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Diciembre")
    diciembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Diciembre")

        

    def __str__(self):
        return f"{self.idproducto} - {self.descripcion}"

    def total_mes(self, mes):
        cantidad = getattr(self, f'{mes}_cantidad')
        precio = getattr(self, f'{mes}_precio')
        return cantidad * precio

    def total_anual(self):
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return sum(self.total_mes(mes) for mes in meses)

    class Meta:
        managed = False 

        verbose_name = "Material de Oficina"
        verbose_name_plural = "Materiales de Oficina"
        ordering = ['idproducto']



#tabla de precios de productos de utiles de oficina de Don Luis

class UtilesOficina(models.Model):
    id = models.AutoField(primary_key=True)
    idproducto = models.CharField(max_length=50, unique=True, verbose_name="ID Producto")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Unitario")
    # Campos para cada mes
    enero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Enero")
    enero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Enero")
    
    febrero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Febrero")
    febrero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Febrero")
    
    marzo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Marzo")
    marzo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Marzo")
    
    abril_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Abril")
    abril_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Abril")
    
    mayo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Mayo")
    mayo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Mayo")
    
    junio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Junio")
    junio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Junio")
    
    julio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Julio")
    julio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Julio")
    
    agosto_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Agosto")
    agosto_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Agosto")
    
    septiembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Septiembre")
    septiembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Septiembre")
    
    octubre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Octubre")
    octubre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Octubre")
    
    noviembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Noviembre")
    noviembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Noviembre")
    
    diciembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Diciembre")
    diciembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Diciembre")

    
    def __str__(self):
        return f"{self.idproducto} - {self.descripcion}"

    def total_mes(self, mes):
        cantidad = getattr(self, f'{mes}_cantidad')
        precio = getattr(self, f'{mes}_precio')
        return cantidad * precio

    def total_anual(self):
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return sum(self.total_mes(mes) for mes in meses)

    class Meta:
        managed = False 
        verbose_name = "Útil de Oficina"
        verbose_name_plural = "Útiles de Oficina"
        ordering = ['idproducto']



#tabla de precios de Equipos de Computo de Don Luis

class EquiposComputo(models.Model):
    id = models.AutoField(primary_key=True)
    idproducto = models.CharField(max_length=50, unique=True, verbose_name="ID Producto")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Unitario")
    # Campos para cada mes
    enero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Enero")
    enero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Enero")
    
    febrero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Febrero")
    febrero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Febrero")
    
    marzo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Marzo")
    marzo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Marzo")
    
    abril_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Abril")
    abril_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Abril")
    
    mayo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Mayo")
    mayo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Mayo")
    
    junio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Junio")
    junio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Junio")
    
    julio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Julio")
    julio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Julio")
    
    agosto_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Agosto")
    agosto_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Agosto")
    
    septiembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Septiembre")
    septiembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Septiembre")
    
    octubre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Octubre")
    octubre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Octubre")
    
    noviembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Noviembre")
    noviembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Noviembre")
    
    diciembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Diciembre")
    diciembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Diciembre")

    
    def __str__(self):
        return f"{self.idproducto} - {self.descripcion}"

    def total_mes(self, mes):
        cantidad = getattr(self, f'{mes}_cantidad')
        precio = getattr(self, f'{mes}_precio')
        return cantidad * precio

    def total_anual(self):
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return sum(self.total_mes(mes) for mes in meses)

    class Meta:
        managed = False 
        verbose_name = "Equipo de Computo"
        verbose_name_plural = "Equipos de Computo"
        ordering = ['idproducto']


#tabla de precios de otros suministros de Don Luis

class OtrosSuministros(models.Model):
    id = models.AutoField(primary_key=True)
    idproducto = models.CharField(max_length=50, unique=True, verbose_name="ID Producto")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Unitario")
    # Campos para cada mes
    enero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Enero")
    enero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Enero")
    
    febrero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Febrero")
    febrero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Febrero")
    
    marzo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Marzo")
    marzo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Marzo")
    
    abril_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Abril")
    abril_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Abril")
    
    mayo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Mayo")
    mayo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Mayo")
    
    junio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Junio")
    junio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Junio")
    
    julio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Julio")
    julio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Julio")
    
    agosto_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Agosto")
    agosto_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Agosto")
    
    septiembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Septiembre")
    septiembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Septiembre")
    
    octubre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Octubre")
    octubre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Octubre")
    
    noviembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Noviembre")
    noviembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Noviembre")
    
    diciembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Diciembre")
    diciembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Diciembre")

    
    def __str__(self):
        return f"{self.idproducto} - {self.descripcion}"

    def total_mes(self, mes):
        cantidad = getattr(self, f'{mes}_cantidad')
        precio = getattr(self, f'{mes}_precio')
        return cantidad * precio

    def total_anual(self):
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return sum(self.total_mes(mes) for mes in meses)

    class Meta:
        managed = False 
        verbose_name = "Otros Suministros"
        verbose_name_plural = "Otros Suministros"
        ordering = ['idproducto']


#tabla de precios de materiales de construccion de Don Luis

class MaterialesConstruccion(models.Model):
    id = models.AutoField(primary_key=True)
    idproducto = models.CharField(max_length=50, unique=True, verbose_name="ID Producto")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Unitario")
    # Campos para cada mes
    enero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Enero")
    enero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Enero")
    
    febrero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Febrero")
    febrero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Febrero")
    
    marzo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Marzo")
    marzo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Marzo")
    
    abril_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Abril")
    abril_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Abril")
    
    mayo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Mayo")
    mayo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Mayo")
    
    junio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Junio")
    junio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Junio")
    
    julio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Julio")
    julio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Julio")
    
    agosto_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Agosto")
    agosto_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Agosto")
    
    septiembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Septiembre")
    septiembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Septiembre")
    
    octubre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Octubre")
    octubre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Octubre")
    
    noviembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Noviembre")
    noviembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Noviembre")
    
    diciembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Diciembre")
    diciembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Diciembre")

    
    def __str__(self):
        return f"{self.idproducto} - {self.descripcion}"

    def total_mes(self, mes):
        cantidad = getattr(self, f'{mes}_cantidad')
        precio = getattr(self, f'{mes}_precio')
        return cantidad * precio

    def total_anual(self):
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return sum(self.total_mes(mes) for mes in meses)

    class Meta:
        managed = False 
        verbose_name = "Materiales de Construccion"
        verbose_name_plural = "Materiales de Construccion"
        ordering = ['idproducto']


#tabla de precios de repuestos y accesorios de Don Luis

class RepuestosAccesorios(models.Model):
    id = models.AutoField(primary_key=True)
    idproducto = models.CharField(max_length=50, unique=True, verbose_name="ID Producto")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Unitario")
    # Campos para cada mes
    enero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Enero")
    enero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Enero")
    
    febrero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Febrero")
    febrero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Febrero")
    
    marzo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Marzo")
    marzo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Marzo")
    
    abril_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Abril")
    abril_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Abril")
    
    mayo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Mayo")
    mayo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Mayo")
    
    junio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Junio")
    junio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Junio")
    
    julio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Julio")
    julio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Julio")
    
    agosto_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Agosto")
    agosto_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Agosto")
    
    septiembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Septiembre")
    septiembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Septiembre")
    
    octubre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Octubre")
    octubre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Octubre")
    
    noviembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Noviembre")
    noviembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Noviembre")
    
    diciembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Diciembre")
    diciembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Diciembre")

    
    def __str__(self):
        return f"{self.idproducto} - {self.descripcion}"

    def total_mes(self, mes):
        cantidad = getattr(self, f'{mes}_cantidad')
        precio = getattr(self, f'{mes}_precio')
        return cantidad * precio

    def total_anual(self):
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return sum(self.total_mes(mes) for mes in meses)

    class Meta:
        managed = False 
        verbose_name = "Repuestos y Accesorios"
        verbose_name_plural = "Repuestos y Accesorios"
        ordering = ['idproducto']


#tabla de precios de materiales de agricultura de Don Luis

class MaterialesAgricultura(models.Model):
    id = models.AutoField(primary_key=True)
    idproducto = models.CharField(max_length=50, unique=True, verbose_name="ID Producto")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Unitario")
    # Campos para cada mes
    enero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Enero")
    enero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Enero")
    
    febrero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Febrero")
    febrero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Febrero")
    
    marzo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Marzo")
    marzo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Marzo")
    
    abril_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Abril")
    abril_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Abril")
    
    mayo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Mayo")
    mayo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Mayo")
    
    junio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Junio")
    junio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Junio")
    
    julio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Julio")
    julio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Julio")
    
    agosto_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Agosto")
    agosto_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Agosto")
    
    septiembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Septiembre")
    septiembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Septiembre")
    
    octubre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Octubre")
    octubre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Octubre")
    
    noviembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Noviembre")
    noviembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Noviembre")
    
    diciembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Diciembre")
    diciembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Diciembre")

    
    def __str__(self):
        return f"{self.idproducto} - {self.descripcion}"

    def total_mes(self, mes):
        cantidad = getattr(self, f'{mes}_cantidad')
        precio = getattr(self, f'{mes}_precio')
        return cantidad * precio

    def total_anual(self):
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return sum(self.total_mes(mes) for mes in meses)

    class Meta:
        managed = False 
        verbose_name = "Materiales de Agricultura"
        verbose_name_plural = "Materiales de Agricultura"
        ordering = ['idproducto']


#tabla de precios de equipos de protección de Don Luis

class EquiposProteccion(models.Model):
    id = models.AutoField(primary_key=True)
    idproducto = models.CharField(max_length=50, unique=True, verbose_name="ID Producto")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Unitario")

    # Campos para cada mes
    enero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Enero")
    enero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Enero")
    
    febrero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Febrero")
    febrero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Febrero")
    
    marzo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Marzo")
    marzo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Marzo")
    
    abril_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Abril")
    abril_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Abril")
    
    mayo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Mayo")
    mayo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Mayo")
    
    junio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Junio")
    junio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Junio")
    
    julio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Julio")
    julio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Julio")
    
    agosto_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Agosto")
    agosto_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Agosto")
    
    septiembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Septiembre")
    septiembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Septiembre")
    
    octubre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Octubre")
    octubre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Octubre")
    
    noviembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Noviembre")
    noviembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Noviembre")
    
    diciembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Diciembre")
    diciembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Diciembre")

    
    def __str__(self):
        return f"{self.idproducto} - {self.descripcion}"

    def total_mes(self, mes):
        cantidad = getattr(self, f'{mes}_cantidad')
        precio = getattr(self, f'{mes}_precio')
        return cantidad * precio

    def total_anual(self):
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return sum(self.total_mes(mes) for mes in meses)

    class Meta:
        managed = False 
        verbose_name = "Equipos de Protección"
        verbose_name_plural = "Equipos de Protección"
        ordering = ['idproducto']


#tabla de precios de equipos de UIT de Don Luis

class EquiposUIT(models.Model):
    id = models.AutoField(primary_key=True)
    idproducto = models.CharField(max_length=50, unique=True, verbose_name="ID Producto")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Unitario")
    
    # Campos para cada mes
    enero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Enero")
    enero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Enero")
    
    febrero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Febrero")
    febrero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Febrero")
    
    marzo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Marzo")
    marzo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Marzo")
    
    abril_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Abril")
    abril_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Abril")
    
    mayo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Mayo")
    mayo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Mayo")
    
    junio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Junio")
    junio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Junio")
    
    julio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Julio")
    julio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Julio")
    
    agosto_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Agosto")
    agosto_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Agosto")
    
    septiembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Septiembre")
    septiembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Septiembre")
    
    octubre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Octubre")
    octubre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Octubre")
    
    noviembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Noviembre")
    noviembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Noviembre")
    
    diciembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Diciembre")
    diciembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Diciembre")

    
    def __str__(self):
        return f"{self.idproducto} - {self.descripcion}"

    def total_mes(self, mes):
        cantidad = getattr(self, f'{mes}_cantidad')
        precio = getattr(self, f'{mes}_precio')
        return cantidad * precio

    def total_anual(self):
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return sum(self.total_mes(mes) for mes in meses)

    class Meta:
        managed = False 
        verbose_name = "Equipos de UIT"
        verbose_name_plural = "Equipos de UIT"
        ordering = ['idproducto']



#tabla de precios de sueldos y salarios de Don Luis
class Sueldo(models.Model):

    id = models.AutoField(primary_key=True)
    dni = models.CharField(max_length=8, verbose_name="DNI")
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    regimen_laboral = models.CharField(max_length=50, verbose_name="Régimen Laboral")
    cargo = models.CharField(max_length=100, verbose_name="Cargo")
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso")
    
    # Campos para sueldos mensuales
    enero = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Enero")
    febrero = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Febrero")
    marzo = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Marzo")
    abril = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Abril")
    mayo = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Mayo")
    junio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Junio")
    julio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Julio")
    agosto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Agosto")
    septiembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Septiembre")
    octubre = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Octubre")
    noviembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Noviembre")
    diciembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Diciembre")
    
    # Campos adicionales solicitados
    usuario = models.CharField(max_length=50, verbose_name="Usuario")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    asignacion = models.CharField(max_length=1, default='0', verbose_name="Asignación Familiar")
    def __str__(self):
        return f"{self.dni} - {self.nombre}"

    def total_anual(self):
        return sum([
            self.enero, self.febrero, self.marzo, self.abril, 
            self.mayo, self.junio, self.julio, self.agosto,
            self.septiembre, self.octubre, self.noviembre, self.diciembre
        ])

    class Meta:
        managed = False 
        db_table = 'sueldo'  # Especifica el nombre exacto de la tabla en la base de datos
        verbose_name = "Sueldo"
        verbose_name_plural = "Sueldos"
        ordering = ['dni']

class Salarios(models.Model):

    id = models.AutoField(primary_key=True)
    dni = models.CharField(max_length=8, verbose_name="DNI")
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    regimen_laboral = models.CharField(max_length=50, verbose_name="Régimen Laboral")
    cargo = models.CharField(max_length=100, verbose_name="Cargo")
    fecha_ingreso = models.DateField(verbose_name="Fecha de Ingreso")
    
    # Campos para sueldos mensuales
    enero = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Enero")
    febrero = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Febrero")
    marzo = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Marzo")
    abril = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Abril")
    mayo = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Mayo")
    junio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Junio")
    julio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Julio")
    agosto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Agosto")
    septiembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Septiembre")
    octubre = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Octubre")
    noviembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Noviembre")
    diciembre = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Diciembre")
    
    # Campos adicionales solicitados
    usuario = models.CharField(max_length=50, verbose_name="Usuario")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    asignacion = models.CharField(max_length=1, default='0', verbose_name="Asignación Familiar")

    def __str__(self):
        return f"{self.dni} - {self.nombre}"

    def total_anual(self):
        return sum([
            self.enero, self.febrero, self.marzo, self.abril, 
            self.mayo, self.junio, self.julio, self.agosto,
            self.septiembre, self.octubre, self.noviembre, self.diciembre
        ])

    class Meta:
        managed = False 
        db_table = 'salario'  # Especifica el nombre exacto de la tabla en la base de datos
        verbose_name = "Salario"
        verbose_name_plural = "Salarios"
        ordering = ['dni']

class ConfiguracionesSueldosSalarios(models.Model):

    tasa_carga_social_sueldo = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0.4430,
        verbose_name="Tasa de Carga Social - Sueldos"
    )
    
    tasa_carga_social_salario = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0.4430,
        verbose_name="Tasa de Carga Social - Salarios"
    )

    sueldo_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1025.00,
        verbose_name="Sueldo Mínimo"
    )

    monto_transporte = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Monto de Transporte"
    )
    
    monto_alimentacion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Monto de Alimentación"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )
    
    usuario_actualizacion = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Usuario que actualizó"
    )

    class Meta:
        managed = False 
        verbose_name = "Configuración Sueldos y Salarios"
        verbose_name_plural = "Configuraciones Sueldos y Salarios"

    def __str__(self):
        return f"Configuración (Última actualización: {self.fecha_actualizacion})"
    
#==============================================================================================
#CAPEX
#==============================================================================================
class Capex(models.Model):
    id = models.AutoField(primary_key=True)
    idproducto = models.CharField(max_length=50, unique=True, verbose_name="ID Producto")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Unitario")
    
    # Campos para cada mes
    enero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Enero")
    enero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Enero")
    
    febrero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Febrero")
    febrero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Febrero")
    
    marzo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Marzo")
    marzo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Marzo")
    
    abril_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Abril")
    abril_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Abril")
    
    mayo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Mayo")
    mayo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Mayo")
    
    junio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Junio")
    junio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Junio")
    
    julio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Julio")
    julio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Julio")
    
    agosto_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Agosto")
    agosto_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Agosto")
    
    septiembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Septiembre")
    septiembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Septiembre")
    
    octubre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Octubre")
    octubre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Octubre")
    
    noviembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Noviembre")
    noviembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Noviembre")
    
    diciembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Diciembre")
    diciembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Diciembre")

    USUARIO = models.CharField(max_length=50, verbose_name="usuario")
    FECHA = models.DateTimeField(auto_now_add=True, verbose_name="fecha")

    def __str__(self):
        return f"{self.idproducto} - {self.descripcion}"

    def total_mes(self, mes):
        cantidad = getattr(self, f'{mes}_cantidad')
        precio = getattr(self, f'{mes}_precio')
        return cantidad * precio

    def total_anual(self):
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return sum(self.total_mes(mes) for mes in meses)

    class Meta:
        managed = False 
        verbose_name = "CAPEX"
        verbose_name_plural = "CAPEX"
        ordering = ['idproducto']



#=======================================================================================================
# SERVICIOS DE TERCEROS
#=======================================================================================================

class Servicios(models.Model):
    id = models.AutoField(primary_key=True)
    idproducto = models.CharField(max_length=50, unique=True, verbose_name="ID Producto")
    grupo_servicio = models.CharField(max_length=50, verbose_name="grupo_sevicio")
    subgrupo_servicio = models.CharField(max_length=10, verbose_name="subgrupo_servicio")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Unitario")
    observacion = models.TextField(blank=True, null=True, verbose_name="Observación")
    # Campos para cada mes
    enero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Enero")
    enero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Enero")
    
    febrero_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Febrero")
    febrero_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Febrero")
    
    marzo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Marzo")
    marzo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Marzo")
    
    abril_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Abril")
    abril_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Abril")
    
    mayo_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Mayo")
    mayo_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Mayo")
    
    junio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Junio")
    junio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Junio")
    
    julio_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Julio")
    julio_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Julio")
    
    agosto_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Agosto")
    agosto_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Agosto")
    
    septiembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Septiembre")
    septiembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Septiembre")
    
    octubre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Octubre")
    octubre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Octubre")
    
    noviembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Noviembre")
    noviembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Noviembre")
    
    diciembre_cantidad = models.IntegerField(default=0, verbose_name="Cantidad Diciembre")
    diciembre_precio = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Precio Diciembre")

    usuario = models.CharField(max_length=50, verbose_name="usuario")
    fecha = models.DateTimeField(auto_now_add=True, verbose_name="fecha")


    def __str__(self):
        return f"{self.idproducto} - {self.descripcion}"

    def total_mes(self, mes):
        cantidad = getattr(self, f'{mes}_cantidad')
        precio = getattr(self, f'{mes}_precio')
        return cantidad * precio

    def total_anual(self):
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return sum(self.total_mes(mes) for mes in meses)

    class Meta:
        managed = False 
        verbose_name = "SERVICIOS"
        verbose_name_plural = "SERVICIOS"
        ordering = ['idproducto']



class TICPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        permissions = [
            #PERMISSIONS PARA EL TIC
                       
            ('ver_tic', 'ver_tic'),

            #PERMISOS PARA VISUALIZAR LAS EMPRESAS
            ('tic_dl', 'tic_dl'),
            ('tic_cv', 'tic_cv'),
            ('tic_ajs', 'tic_ajs'),

            #PERMISO DE ACCESO ESTANDAR AL MODULO TIC
            ('tic_item','tic_item'),

            #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
            ('tic_costos', 'tic_costos'),
            ('view_josep', 'view_josep'),

            #PERMISO SECCION PRESUPUESTO 
            ('tic_presupuesto','tic_presupuesto'),
            
            
            # MODULO DE REPORTES 
            
            ('modulo_reportes_generales','modulo_reportes_generales'),
            # ALMACEN
            ('modulo_reportes_generales_almacen','modulo_reportes_generales_almacen'),
            ('reportes_rotacion_productos','reportes_rotacion_productos'),

           
]
        
        
        
        