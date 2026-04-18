from django.forms import *
from datetime import datetime
from mf.user.models import User

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['autofocus'] = True

    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'first_name': TextInput(
                attrs={
                    'class': 'form-control UpperCase',
                    'placeholder': 'Indique sus nombres',
                    'autocomplete': 'off',
                }
            ),
            'last_name': TextInput(
                attrs={
                    'class': 'form-control UpperCase',
                    'placeholder': 'Indique sus apellidos',
                    'autocomplete': 'off',
                }
            ),
            'username': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Indique su nombre de usuario',
                    'autocomplete': 'off',
                }
            ),
            'email': TextInput(
                attrs={
                    'class': 'form-control UpperCase',
                    'placeholder': 'Indique su correo electrónico',
                    'autocomplete': 'off',
                }
            ),
            'password': PasswordInput(render_value=True,
                attrs={
                    'class': 'form-control pointer-1',
                    'placeholder': 'Ingrese su contraseña',
                    'autocomplete': 'off',
                }
            ),
        }
        exclude = ['groups', 'user_permissions','last_login', 'date_joined','is_superuser', 'is_staff', 'is_active']

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