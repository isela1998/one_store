from django.contrib import admin

# Register your models here.
from mf.user.models import User

admin.site.register(User)
