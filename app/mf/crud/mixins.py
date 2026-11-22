from django.contrib.auth.models import Group
from django.shortcuts import redirect
from datetime import datetime
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from crum import get_current_request

class IsSuperuserMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseRedirect(reverse_lazy('crud:dashboard'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_now'] = datetime.now()
        return context

class ValidatePermissionMixin(object):
    permission_required = ''
    url_redirect = None 

    def get_perms_required(self):
        perms = []
        if isinstance(self.permission_required, str):
            perms.append(self.permission_required)
        else:
            perms = list(self.permission_required)
        return perms

    def get_url_redirect(self):
        if self.url_redirect is None:
            return reverse_lazy('crud:dashboard')
        return self.url_redirect

    def dispatch(self, request, *args, **kwargs):
        group = request.user.groups.first()
        if group is None:
            messages.error(request, 'Acceso Denegado!')
            messages.error(request, 'No tiene permisos para entrar a ese módulo')
            return HttpResponseRedirect(self.get_url_redirect())

        for p in self.get_perms_required():
            if not group.permissions.filter(codename=p).exists():
                messages.error(request, 'Acceso Denegado!')
                messages.error(request, 'Acceso Denegado. No tiene permisos para entrar a ese módulo')
                return HttpResponseRedirect(self.get_url_redirect())
        return super().dispatch(request, *args, **kwargs)
