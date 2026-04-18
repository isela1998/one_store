from django.urls import path
from mf.user.views import *
# from mf.crud.views.tests.views import TestView

app_name = 'user'

urlpatterns = [
    # Users
    path('list/', UserListView.as_view(), name='users_list'),
]