from django.urls import path
from mf.login.views import *

urlpatterns = [
    path('', LoginFormView.as_view(), name='login'),
    path('logout/', LogoutRedirectView.as_view(), name='logout')
]