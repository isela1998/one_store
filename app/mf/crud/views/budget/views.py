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

from mf.crud.models import Budget, DetBudget
from mf.crud.functions import *
from django.db.models import Prefetch, Q

import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
# from django_xhtml2pdf.utils import pdf_decorator
from django.contrib.staticfiles import finders

from django.contrib import messages
import logging
logger = logging.getLogger(__name__)

class BudgetListView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    model = Budget
    template_name = 'budget/list.html'
    permission_required = 'view_sale'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        db = 'default'
        try:
            sede = request.POST['sede']
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                budgets_qs = Budget.objects.using(db).select_related('client').prefetch_related(
                    Prefetch('detbudget_set', queryset=DetBudget.objects.select_related('prod__category', 'prod__type_product'))
                )
                for i in budgets_qs:
                    item = i.toJSON()
                    data.append(item)
            elif action == 'delete':
                require_perm(request.user, 'delete_budget')
                Budget.objects.using(db).get(pk=request.POST['id']).delete()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            log_error(logger, e, '[%s] error en acción=%s usuario=%s', __name__, request.POST.get('action'), request.user)
            data['error'] = error_message(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de presupuestos'
        context['create_url'] = reverse_lazy('crud:sale_create')
        context['dl'] = get_dollar()
        context['list_url'] = reverse_lazy('crud:budget_list')
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context

class BudgetInvoicePdfView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    permission_required = 'view_sale'

    def link_callback(self, uri, rel):
        return resolve_pdf_uri(uri)

    # @pdf_decorator(pdfname='new_filename.pdf')
    def get(self, request, *args, **kwargs):
        try:
            db = 'default'
            template = get_template('budget/budget.html')
            direction = []
            
            budget = Budget.objects.get(pk=self.kwargs['s'])
            server_url = request.build_absolute_uri('/')

            dataCompany = getCompanyData()
            context = {
                'sale': budget,
                'comp': dataCompany,
                'url': getStaticUrl(),
                'icon': server_url + 'media/img/logo/logo.png',
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="/Users/Isela/Desktop/'+n_order+'.pdf"'
             
            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback    
            )
            return response
        except Exception as e:
            log_error(logger, e, '[%s] error generando PDF usuario=%s', __name__, request.user)
            messages.error(request, 'No se pudo generar el PDF. Intenta de nuevo o avisa al administrador.')
        return HttpResponseRedirect(reverse_lazy('crud:budget_list'))

