from django.core.files.storage import FileSystemStorage
from crum import get_current_user, get_current_request
from mf.user.models import User
from django.db import models
from datetime import datetime
from django.utils import timezone 
from datetime import date
from django.forms import model_to_dict
from config.settings import MEDIA_URL, STATIC_URL
from mf.models import BaseModel
from django.utils.dateparse import parse_datetime
import pytz

IDENTITY_CHOICES = [
    ('V', 'V'),
    ('J', 'J'),
    ('E', 'E'),
    ('G', 'G'),
    ('FP', 'FP'),
]

SYMBOL_CHOICES = [
    ('Bs', 'Bs'),
    ('$', '$'),
]

STATUS_CHOICES = [
    ('ACTIVO', 'ACTIVO'),
    ('INACTIVO', 'INACTIVO'),
]

class Permisology(models.Model):
    name = models.CharField(max_length=255, verbose_name='Permiso')
    description = models.CharField(max_length=255, verbose_name='Descripción')
    day = models.DateField(max_length=50, default=date.today().strftime('%Y-%m-%d'), verbose_name='Fecha de pago')
    color = models.CharField(max_length=250, default='#007bff', verbose_name='Color')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Permisos y Eventos'
        verbose_name_plural = 'Permisos y Eventos'
        ordering = ['id']

class CompanyInfo(models.Model):
    name = models.CharField(max_length=225, verbose_name="Razón Social")
    comercialName = models.CharField(max_length=225, verbose_name="Nombre Comercial")
    nit = models.CharField(max_length=225, verbose_name="NIT")
    address = models.CharField(max_length=225, verbose_name="Dirección Fiscal")
    city = models.CharField(max_length=225, verbose_name="Ciudad")
    phone = models.CharField(max_length=255, verbose_name="Telefono(s)")
    email = models.CharField(max_length=255, verbose_name="Correo")
    services = models.TextField(verbose_name="Servicios")
    logo = models.ImageField(upload_to='img/logo', null=True, blank=True)
    logoInvoice = models.ImageField(upload_to='img/logo', null=True, blank=True)

    def __str__(self):
        return '{}.{}'.format(self.name, self.nit)
    
    def toJSON(self):
        item = model_to_dict(self)
        item['logo'] = str(self.logo)
        item['logoInvoice'] = str(self.logoInvoice)
        return item
    
    class Meta:
        verbose_name = "Información de la Empresa"
        ordering = ['id']

class Eventos(models.Model):
    name = models.CharField(max_length=255, verbose_name='Evento')
    description = models.CharField(max_length=255, verbose_name='Descripción')
    day = models.DateField(max_length=50, default=date.today().strftime('%Y-%m-%d'), verbose_name='Fecha')
    color = models.CharField(max_length=250, default='#007bff', verbose_name='Color')

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Eventos'
        verbose_name_plural = 'Eventos'
        ordering = ['id']

# NEW MODELS
class Dolar(models.Model):
    dolar = models.DecimalField(default=0.00, max_digits=30, decimal_places=2)

    def __str__(self):
        return self.dolar
    
    def toJSON(self):
        item = model_to_dict(self)
        item['dolar'] = format(self.dolar, '.2f')
        return item

class Category(models.Model):
    name = models.CharField(max_length=150, verbose_name='Categoría', unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['id']

class Brand(models.Model):
    name = models.CharField(max_length=150, verbose_name='Marca', unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['id']

class Type_product(models.Model):
    name = models.CharField(max_length=150, verbose_name='Tipo', unique=True)

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Tipo'
        verbose_name_plural = 'Tipos'
        ordering = ['id']

class Product(models.Model):
    code = models.CharField(max_length=150, verbose_name='Código', unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Categoría")
    type_product = models.ForeignKey(Type_product, on_delete=models.PROTECT, verbose_name="Tipo")
    product = models.CharField(max_length=150, verbose_name='Producto')
    brand = models.CharField(max_length=150, verbose_name='Marca')
    description = models.TextField(max_length=9999, verbose_name='Descripción', null=True, blank=True)
    price = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Precio sin IVA")
    cost = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Precio costo")
    price_dl = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Precio venta")
    price_bs = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Precio bolivares")
    gain = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Ganancia")
    quantity = models.DecimalField(default=0, max_digits=30, decimal_places=3, verbose_name="Cantidad")

    def __str__(self):
        return '{}.{}.{}'.format(self.brand, self.product, self.type_product.name)
    
    def toJSON(self):
        item = model_to_dict(self)
        item['category'] = self.category.toJSON()
        item['type_product'] = self.type_product.toJSON()
        # item['quantity'] = format(self.quantity, '.3f')
        item['quantity'] = float(self.quantity) if self.quantity % 1 != 0 else int(self.quantity)
        item['cost'] = format(self.cost, '.2f')
        item['price'] = format(self.price, '.2f')
        item['price_dl'] = format(self.price_dl, '.2f')
        item['price_bs'] = format(self.price_bs, '.2f')
        item['gain'] = format(self.gain, '.2f')
        return item
    
    class Meta:
        verbose_name = 'Producto (Ventas)'
        verbose_name_plural = 'Productos (Ventas)'
        ordering = ['id']

class Client(models.Model):
    names = models.CharField(max_length=150, verbose_name='Cliente')
    identity = models.CharField(max_length=3, choices=IDENTITY_CHOICES, default='V', verbose_name="Identificación")
    ci = models.CharField(max_length=50, unique=True, verbose_name='CI/RIF')
    address = models.CharField(max_length=180, verbose_name='Dirección')
    contact = models.CharField(max_length=50, verbose_name='Teléfono')

    def __str__(self):
        client = self.names + ' ' + self.identity.identity + '-' + self.ci
        return client

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['id']
    
class Method_pay(models.Model):
    name = models.CharField(max_length=150, verbose_name='Método de Pago', unique=True)
    type_symbol = models.CharField(max_length=3, choices=SYMBOL_CHOICES, default='$', verbose_name="Moneda")

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de pago'
        ordering = ['id']

class Sale(models.Model):
    user = models.CharField(max_length=255, default='NA', verbose_name="Vendedor")
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    datejoined = models.DateField(max_length=10, default=date.today().strftime('%Y-%m-%d'), verbose_name="Fecha")
    datehour = models.CharField(default=date.today().strftime('%Y-%m-%d'), max_length=30, verbose_name="Fecha")
    invoice_number = models.CharField(max_length=255, default='00000000', verbose_name="Nº Factura")
    control_number = models.CharField(max_length=255, default='00000000', verbose_name="Nº de Control")
    subtotal = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Subtotal $")
    discount = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Descuento $")
    iva = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="IVA 16%")
    total = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Total $")
    totalBs = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Total Bs")
    type_sale = models.CharField(max_length=25, verbose_name='Método')
    method_pay = models.ForeignKey(Method_pay, on_delete=models.PROTECT, blank=True, null=True, related_name='method_pays', verbose_name="Método de pago (1)")
    method_pay1 = models.ForeignKey(Method_pay, on_delete=models.PROTECT, blank=True, null=True, related_name='method_pays1', verbose_name="Método de pago (2)")
    method_pay2 = models.ForeignKey(Method_pay, on_delete=models.PROTECT, blank=True, null=True, related_name='method_pays2', verbose_name="Método de pago (3)")
    received = models.DecimalField(default=0, max_digits=100, decimal_places=2, verbose_name='Entrada (1)')
    received1 = models.DecimalField(default=0, max_digits=100, decimal_places=2, verbose_name='Entrada (2)')
    received2 = models.DecimalField(default=0, max_digits=100, decimal_places=2, verbose_name='Entrada (3)')
    description = models.CharField(max_length=255, verbose_name='Notas')
    rate = models.DecimalField(default=0.00, max_digits=30, decimal_places=2)
    status = models.IntegerField(default=0)

    def __str__(self):
        return '{}.{}'.format(self.client.names, self.client.ci)

    def toJSON(self):
        item = model_to_dict(self)
        item['client'] = self.client.toJSON()
        item['subtotal'] = format(self.subtotal, '.2f')
        item['discount'] = format(self.discount, '.2f')
        item['iva'] = format(self.iva, '.2f')
        item['total'] = format(self.total, '.2f')
        item['totalBs'] = format(self.totalBs, '.2f')
        item['method_pay'] = self.method_pay.toJSON()
        item['method_pay1'] = self.method_pay1.toJSON()
        item['method_pay2'] = self.method_pay2.toJSON()
        item['received'] = format(self.received, '.2f')
        item['received1'] = format(self.received1, '.2f')
        item['received2'] = format(self.received2, '.2f')
        item['rate'] = format(self.rate, '.2f')
        item['det'] = [i.toJSON() for i in self.detsale_set.all()]
        return item
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['id']

class DetSale(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    prod = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name='Precio Producto $')
    quantity = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name='Cantidad')
    total = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name='Total')
    rate = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name='Tasa $')

    def __str__(self):
        return self.prod.name
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['sale'])
        item['prod'] = self.prod.toJSON()
        item['price'] = format(self.price, '.2f')
        item['quantity'] = format(self.quantity, '.0f')
        item['total'] = format(self.total, '.2f')
        item['rate'] = format(self.rate, '.2f')
        return item

    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalle de Ventas'
        ordering = ['id']

class Credit(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    last_credit_date = models.DateField(max_length=10, default=date.today().strftime('%Y-%m-%d'), verbose_name="Fecha")
    datehour = models.CharField(default=date.today().strftime('%Y-%m-%d'), max_length=30, verbose_name="Fecha")
    totalDebt = models.DecimalField(default=0.00, max_digits=30, decimal_places=2)

    def __str__(self):
        return self.client.names

    def toJSON(self):
        item = model_to_dict(self)
        item['client'] = self.client.toJSON()
        item['totalDebt'] = format(self.totalDebt, '.2f')
        item['det'] = [i.toJSON() for i in self.detcredit_set.all()]
        return item

    class Meta:
        verbose_name = 'Venta a Crédito'
        verbose_name_plural = 'Ventas a Crédito'
        ordering = ['id']

class DetCredit(models.Model):
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE)
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, null=True, blank=True)
    last_credit_date = models.DateField(max_length=10, default=date.today().strftime('%Y-%m-%d'), verbose_name="Fecha")
    datehour = models.CharField(default=date.today().strftime('%Y-%m-%d'), max_length=30, verbose_name="Fecha y Hora")
    operation = models.CharField(max_length=2, default="+", verbose_name='Operación')
    quantity = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name='Cantidad')
    description = models.CharField(max_length=255, verbose_name='Descripción')

    def __str__(self):
        return self.credit.id
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['credit'])
        if self.sale:
            item['sale'] = self.sale.toJSON()
        item['quantity'] = format(self.quantity, '.2f')
        return item

    class Meta:
        verbose_name = 'Detalle del Crédito'
        verbose_name_plural = 'Detalle de Créditos'
        ordering = ['id']

class Budget(models.Model):
    user = models.CharField(max_length=255, default='NA', verbose_name="Vendedor")
    budget_number = models.CharField(max_length=255, default='00000000', verbose_name="Presupuesto Nº")
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    datejoined = models.DateField(max_length=10, default=date.today().strftime('%Y-%m-%d'), verbose_name="Fecha")
    subtotal = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Subtotal $")
    discount = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Descuento $")
    iva = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="IVA 16%")
    total = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Total $")
    type_sale = models.CharField(max_length=25, verbose_name='Presupuesto')
    description = models.CharField(max_length=250, verbose_name='Nota')
    rate = models.DecimalField(default=0.00, max_digits=30, decimal_places=2)

    def __str__(self):
        return self.budget_number

    def toJSON(self):
        item = model_to_dict(self)
        item['client'] = self.client.toJSON()
        item['subtotal'] = format(self.subtotal, '.2f')
        item['discount'] = format(self.discount, '.2f')
        item['iva'] = format(self.iva, '.2f')
        item['total'] = format(self.total, '.2f')
        item['rate'] = format(self.rate, '.2f')
        item['det'] = [i.toJSON() for i in self.detbudget_set.all()]
        return item
    
    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        ordering = ['id']

class DetBudget(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    prod = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name='Precio Producto $')
    quantity = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name='Cantidad')
    total = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name='Total')
    rate = models.DecimalField(default=0.00, max_digits=30, decimal_places=22, verbose_name='Tasa $ Calculada')

    def __str__(self):
        return self.prod.name
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['budget'])
        item['prod'] = self.prod.toJSON()
        item['price'] = format(self.price, '.2f')
        item['quantity'] = format(self.quantity, '.0f')
        item['total'] = format(self.total, '.2f')
        item['rate'] = format(self.rate, '.2f')
        return item

    class Meta:
        verbose_name = 'Detalle de Presupuesto'
        verbose_name_plural = 'Detalle de Presupuestos'
        ordering = ['id']

class Debt(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre/Razón Social")
    description = models.CharField(max_length=255, verbose_name='Descripción')
    last_credit_date = models.DateField(max_length=10, default=date.today().strftime('%Y-%m-%d'), verbose_name="Fecha")
    datehour = models.CharField(default=date.today().strftime('%Y-%m-%d'), max_length=30, verbose_name="Fecha")
    totalDebt = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name="Total $")

    def __str__(self):
        return self.name

    def toJSON(self):
        item = model_to_dict(self)
        item['totalDebt'] = format(self.totalDebt, '.2f')
        item['det'] = [i.toJSON() for i in self.detdebt_set.all()]
        return item

    class Meta:
        verbose_name = 'Cuenta por pagar'
        verbose_name_plural = 'Cuentas por pagar'
        ordering = ['id']

class DetDebt(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE)
    last_debt_date = models.DateField(max_length=10, default=date.today().strftime('%Y-%m-%d'), verbose_name="Fecha")
    datehour = models.CharField(default=date.today().strftime('%Y-%m-%d'), max_length=30, verbose_name="Fecha y Hora")
    operation = models.CharField(max_length=2, default="+", verbose_name='Operación')
    quantity = models.DecimalField(default=0.00, max_digits=30, decimal_places=2, verbose_name='Cantidad')
    description = models.CharField(max_length=255, verbose_name='Descripción')

    def __str__(self):
        return self.debt.name
    
    def toJSON(self):
        item = model_to_dict(self, exclude=['debt'])
        item['quantity'] = format(self.quantity, '.2f')
        return item

    class Meta:
        verbose_name = 'Detalle de cuenta por pagar'
        verbose_name_plural = 'Detalle de cuentas por pagar'
        ordering = ['id']