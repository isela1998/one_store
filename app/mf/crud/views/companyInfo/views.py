from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.urls import reverse_lazy

from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from mf.crud.models import CompanyInfo
from mf.crud.forms import CompanyInfoForm
from mf.user.models import User
from mf.crud.functions import *
from config.settings import MEDIA_URL
from django.conf import settings

import logging
logger = logging.getLogger(__name__)


class CompanyInfoView(LoginRequiredMixin, ValidatePermissionMixin, TemplateView):
    template_name = 'companyInfo/list.html'
    permission_required = 'view_companyinfo'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            db = 'default'
            action = request.POST['action']
            if action == 'searchdata':
                data = getCompanyData()
            elif action == 'edit':
                perms = ['change_companyinfo', ]
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):
                    c = CompanyInfo.objects.get(pk=1)
                    c.name = request.POST['name']
                    c.comercialName = request.POST['comercialName']
                    c.nit = request.POST['nit']
                    c.address = request.POST['address']
                    c.phone = request.POST['phone']
                    c.city = request.POST['city']
                    c.email = request.POST['email']
                    c.services = request.POST['services']
                    if request.FILES:
                        c.logo = request.FILES['logo']
                    c.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            log_error(logger, e, '[%s] error en acción=%s usuario=%s', __name__, request.POST.get('action'), request.user)
            data['error'] = error_message(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Empresa'
        context['list_url'] = reverse_lazy('crud:companyinfo')
        context['form'] = CompanyInfoForm()
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['dl'] = get_dollar()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context
