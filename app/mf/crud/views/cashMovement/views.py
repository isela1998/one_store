from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpRequest
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db import transaction
from datetime import date, datetime, timedelta
import json
from django.utils import timezone


from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from mf.crud.models import CashMovement
from mf.crud.forms import CashMovementForm
from mf.crud.functions import *
from django.db.models import Q

import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
# from django_xhtml2pdf.utils import pdf_decorator
from django.contrib.staticfiles import finders

from django.contrib import messages
import logging
logger = logging.getLogger(__name__)

class CashMovementView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    model = CashMovement
    template_name = 'cashMovement/list.html'
    permission_required = 'view_cashmovement'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        db = 'default'
        try:
            sede = 'default'
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                dl = get_dollar()
                dl_value = dl.get('dolar1')

                for i in CashMovement.objects.filter(date_time__date__gte=request.POST['start'],
                        date_time__date__lte=request.POST['end']):
                    item = i.toJSON()
                    item['dl'] = float(dl_value)
                    hora_local = timezone.localtime(i.date_time)
                    item['date_time'] = hora_local.strftime('%d-%m-%Y %I:%M %p')
                    data.append(item)
            elif action == 'delete':
                if not request.user.is_superuser:
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                else:
                    with transaction.atomic():
                        c = CashMovement.objects.get(pk=request.POST['id'])
                        c.status = 0
                        c.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            log_error(logger, e, '[%s] error en acción=%s usuario=%s', __name__, request.POST.get('action'), request.user)
            data['error'] = error_message(e)
        return JsonResponse(data, safe=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Movimientos de Caja'
        context['dl'] = get_dollar()
        context['month'] = date.today().month
        context['monthName'] = getMonthName(int(date.today().month))
        context['year'] = date.today().year
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context
