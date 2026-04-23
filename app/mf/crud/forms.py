from django.forms import *
from datetime import datetime
from mf.crud.models import *

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']
 
class PermisologyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Permisology
        fields = '__all__'
        widgets = {
            'name': TextInput(
                attrs={
                    'class': 'form-control UpperCase',
                    'placeholder': 'Título',
                    'autocomplete': 'off'
                }
            ),
            'description':Textarea(
                attrs={
                    'placeholder': 'Descripción del Permiso ó Evento',
                    'class': 'form-control',
                    'rows': 3,
                    'autocomplete': 'off'
                }
            ),
            'day': DateInput(format='%Y-%m-%d',
                attrs={
                    'value': datetime.now().strftime('%Y-%m-%d'),
                    'autocomplete': 'off',
                    'class': 'form-control datetimepicker-input',
                    'placeholder': 'YYYY-MM-DD',
                    'id': 'day',
                    'data-target': '#day',
                    'data-toggle': 'datetimepicker'
                }
            ),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class CompanyInfoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = CompanyInfo
        fields = '__all__'
        widgets = {
            'name':TextInput(
                attrs={
                    'placeholder': 'Razón social',
                    'class': 'form-control UpperCase',
                    'autocomplete': 'off',
                    'disabled': 'disabled',
                }
            ),
            'comercialName':TextInput(
                attrs={
                    'placeholder': 'Nombre Comercial',
                    'class': 'form-control UpperCase',
                    'autocomplete': 'off',
                    'disabled': 'disabled',
                }
            ),
            'nit':TextInput(
                attrs={
                    'placeholder': 'NIT de la empresa',
                    'class': 'form-control UpperCase',
                    'autocomplete': 'off',
                    'disabled': 'disabled',
                }
            ),
            'address':TextInput(
                attrs={
                    'placeholder': 'Ubicación de la sede',
                    'class': 'form-control UpperCase',
                    'autocomplete': 'off',
                    'disabled': 'disabled',
                }
            ),
            'city':TextInput(
                attrs={
                    'placeholder': 'Ciudad',
                    'class': 'form-control UpperCase',
                    'autocomplete': 'off',
                    'disabled': 'disabled',
                }
            ),
            'phone':TextInput(
                attrs={
                    'placeholder': 'Números de contacto',
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'disabled': 'disabled',
                }
            ),
            'email':TextInput(
                attrs={
                    'placeholder': 'Dirección de correo electronico',
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'disabled': 'disabled',
                }
            ),
            'services': Textarea(
                attrs={
                    'class': 'form-control',
                    'autocomplete': 'off',
                    'placeholder': 'Indique los detalles de servicios y productos que ofrece la empresa...',
                    'rows': 4,
                    'disabled': 'disabled',
                }
            ),
            'logo': FileInput(
                attrs={
                    'class': 'form-control',
                    'disabled': 'disabled',
                }
            ),

        }
        
    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class EventosForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Eventos
        fields = '__all__'
        widgets = {
            'name': TextInput(
                attrs={
                    'class': 'form-control UpperCase',
                    'placeholder': 'Título',
                    'autocomplete': 'off'
                }
            ),
            'description':Textarea(
                attrs={
                    'placeholder': 'Descripción del evento',
                    'class': 'form-control',
                    'rows': 3,
                    'autocomplete': 'off'
                }
            ),
            'day': DateInput(format='%Y-%m-%d',
                attrs={
                    'value': datetime.now().strftime('%Y-%m-%d'),
                    'autocomplete': 'off',
                    'class': 'form-control datetimepicker-input',
                    'placeholder': 'YYYY-MM-DD',
                    'id': 'day',
                    'type': 'date',
                    'data-target': '#day',
                    'data-toggle': 'datetimepicker'
                }
            ),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class CategoryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': TextInput(
                attrs={
                    'placeholder': 'Nombre de la categoría',
                    'class': 'form-control UpperCase',
                    'autocomplete': 'off'
                }
            )
        }
        exclude = ['user_updated', 'user_creation']

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class BrandForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Brand
        fields = '__all__'
        widgets = {
            'name': TextInput(
                attrs={
                    'placeholder': 'Nombre de la marca',
                    'class': 'form-control UpperCase',
                    'autocomplete': 'off'
                }
            )
        }
        exclude = ['user_updated', 'user_creation']

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class TypeProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Type_product
        fields = '__all__'
        widgets = {
            'name': TextInput(
                attrs={
                    'placeholder': 'Nombre del tipo de producto',
                    'class': 'form-control UpperCase',
                    'autocomplete': 'off'
                }
            )
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class ProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].widget.attrs['autofocus'] = True

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'code': TextInput(
                attrs={
                    'placeholder': 'Código del producto',
                    'class': 'form-control UpperCase',
                    'autocomplete': 'off'
                }
            ),
            'category': Select(
                attrs={
                    'autofocus': True,
                    'class': 'form-control medium',
            }),
            'type_product': Select(
                attrs={
                    'autofocus': True,
                    'class': 'form-control medium',
            }),
            'product': TextInput(
                attrs={
                    'placeholder': 'Nombre del producto',
                    'class': 'form-control UpperCase',
                    'autocomplete': 'off'
                }
            ),
            'brand':TextInput(
                attrs={
                    'placeholder': 'Marca del producto',
                    'class': 'form-control UpperCase',
                    'autocomplete': 'off'
                }
            ),
            'description':Textarea(
                attrs={
                    'placeholder': 'Descripción del producto',
                    'class': 'form-control',
                    'rows': 3,
                    'autocomplete': 'off'
                }
            ),
            'cost':TextInput(
                attrs={
                    'placeholder': 'Costo $',
                    'class': 'form-control text-center inputNumberFormat',
                    'autocomplete': 'off',
                    'min': 0
                }
            ),
            'price_dl':TextInput(
                attrs={
                    'placeholder': 'Venta $',
                    'class': 'form-control text-center inputNumberFormat',
                    'autocomplete': 'off',
                    'min': 0
                }
            ),
            'quantity':NumberInput(
                attrs={
                    'placeholder': 'Cantidad',
                    'class': 'form-control text-center',
                    'onclick': 'this.select()',
                    'autocomplete': 'off',
                    'min': '0.000',
                    'step': '0.001',  
                    'value': '0.000',
                }
            ),
        }
        exclude = ['price_bs', 'gain', 'price']

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class ProductUpForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs['autofocus'] = True

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'quantity': NumberInput(attrs={
                'placeholder': 'Cantidad',
                'class': 'form-control',
                'autocomplete': 'off',
                'onclick': 'this.select()',
                'min': '0.000',
                'step': '0.001',  
                'value': '0.000',
            }),
        }
        exclude = ['product', 'code', 'category', 'type_product', 'brand', 'description', 'price', 'cost', 'gain', 'price_dl', 'price_bs']

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class ClientForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['names'].widget.attrs['autofocus'] = True

    class Meta:
        model = Client
        fields = '__all__'
        widgets = {
            'names': TextInput(
                attrs={
                    'placeholder': 'Nombres o Razon Social del cliente',
                    'autocomplete': 'off',
                    'class': 'form-control medium UpperCase',
                }
            ),
            'identity':Select(
                attrs={
                    'autofocus': True,
                    'class': 'form-control medium',
                    'style': 'width: 100%; font-size: init!important;'
            }),
            'ci': TextInput(
                attrs={
                    'placeholder': 'Ej. 10203040 ó 10203040-5',
                    'autocomplete': 'off',
                    'class': 'form-control medium inputNumbers'
                }
            ),
            'address': TextInput(
                attrs={
                    'placeholder': 'Dirección de domicilio del cliente',
                    'autocomplete': 'off',
                    'class': 'form-control UpperCase medium'
                }
            ),
            'contact': TextInput(
                attrs={
                    'placeholder': 'Contacto del cliente',
                    'autocomplete': 'off',
                    'class': 'form-control medium inputNumbers'
                }
            ),
        }
        exclude = ['user_updated', 'user_creation']

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class MethodPayForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Method_pay
        fields = '__all__'
        widgets = {
            'name': TextInput(
                attrs={
                    'placeholder': 'Nombre del tipo pago',
                    'class': 'form-control UpperCase',
                    'autocomplete': 'off'
                }
            ),
            'type_symbol':Select(
                attrs={
                    'autofocus': True,
                    'class': 'form-control medium',
                    'style': 'width: 100%; font-size: init!important;'
            }),
        }

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class SaleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Sale
        fields = '__all__'
        widgets = {
            'client':Select(
                attrs={
                    'class': 'form-control larger select2',
                    'style': 'width: 100%'
            }),
            'datejoined': DateInput(format='%Y-%m-%d',
                attrs={
                    'value': datetime.now().strftime('%Y-%m-%d'),
                    'autocomplete': 'off',
                    'class': 'form-control datetimepicker-input',
                    'id': 'datejoined',
                    'data-target': '#datejoined',
                    'data-toggle': 'datetimepicker'
                }
            ),
            'subtotal': TextInput(attrs={
                'readonly': True,
                'class': 'form-control large',
                'autocomplete': 'off'
            }),
            'total': TextInput(attrs={
                'readonly': True,
                'class': 'form-control text-center em-25 height-auto',
                'autocomplete': 'off'
            }),
            'method_pay':Select(
                attrs={
                    'class': 'form-control larger',
                    'style': 'width: 100%',
                    'value': 2,
            }),
            'method_pay1':Select(
                attrs={
                    'class': 'form-control larger',
                    'style': 'width: 100%',
                    'value': 1,
            }),
            'method_pay2':Select(
                attrs={
                    'class': 'form-control larger',
                    'style': 'width: 100%',
                    'value': 1,
            }),
            'description': Textarea(
                attrs={
                'class': 'form-control large UpperCase',
                'autocomplete': 'off',
            }),
            'discount':TextInput(
                attrs={
                    'placeholder': 'Cantidad a Descontar',
                    'class': 'form-control large',
                    'autocomplete': 'off',
                    'value': '0,00',
                    'readonly': 'readonly',
                }
            ),
            'received':TextInput(
                attrs={
                    'placeholder': 'Cantidad',
                    'class': 'form-control larger text-center inputNumberFormat',
                    'autocomplete': 'off',
                    'value': '0,00',
                }
            ),
            'received1':TextInput(
                attrs={
                    'placeholder': 'Cantidad',
                    'class': 'form-control larger text-center inputNumberFormat',
                    'autocomplete': 'off',
                    'value': '0,00',
                }
            ),
            'received2':TextInput(
                attrs={
                    'placeholder': 'Cantidad',
                    'class': 'form-control larger text-center inputNumberFormat',
                    'autocomplete': 'off',
                    'value': '0,00',
                }
            ),
            'pendingChange':TextInput(
                attrs={
                    'class': 'form-control large text-center inputNumberFormat',
                    'placeholder': 'Pendiente por devolver...',
                    'autocomplete': 'off',
                    'value': '0,00',
                }
            ),
            'discountChange':TextInput(
                attrs={
                    'class': 'form-control large text-center inputNumberFormat',
                    'placeholder': 'Vuelto descontado...',
                    'autocomplete': 'off',
                    'value': '0,00',
                }
            ),
        }
        exclude = ['control_number']

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

class DebtForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Debt
        fields = '__all__'
        widgets = {
            'name': TextInput(
                attrs={
                    'placeholder': 'Nombres o Razon Social',
                    'autocomplete': 'off',
                    'class': 'form-control medium UpperCase',
                }
            ),
            'last_credit_date': DateInput(format='%Y-%m-%d',
                attrs={
                    'value': datetime.now().strftime('%Y-%m-%d'),
                    'autocomplete': 'off',
                    'class': 'form-control datetimepicker-input',
                    'id': 'last_credit_date',
                    'data-target': '#last_credit_date',
                    'placeholder': 'YYYY-MM-DD',
                    'data-toggle': 'datetimepicker',
                    'type': 'date'
                }
            ),
            'description': Textarea(
                attrs={
                'placeholder': 'Indique los detalles del abono',
                'class': 'form-control large UpperCase',
                'rows': 4,
                'autocomplete': 'off',
            }),
            'totalDebt':TextInput(
                attrs={
                    'placeholder': 'Total del abono',
                    'class': 'form-control larger text-center inputNumberFormat',
                    'autocomplete': 'off',
                    'value': '0,00',
                }
            ),
        }
        exclude = ['datehour']

    def save(self, commit=True):
        data = {}
        form = super()
        try:
            if form.is_valid():
                form.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data