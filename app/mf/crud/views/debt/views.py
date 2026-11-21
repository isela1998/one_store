from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpRequest
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db import transaction
from datetime import date, datetime, timedelta
import json
from django.utils import timezone
from decimal import Decimal


from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from mf.crud.models import Debt, DetDebt
from mf.crud.forms import DebtForm
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

class DebtListView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    model = Debt
    template_name = 'debt/list.html'
    permission_required = 'view_debt'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        db = 'default'
        try:
            sede = ''
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Debt.objects.using(db).filter(last_credit_date__gte=request.POST['start'], last_credit_date__lte=request.POST['end']):
                    item = i.toJSON()
                    data.append(item)
            elif action == 'searchdata2':
                data = []
                for i in DetDebt.objects.filter(debt__id=request.POST['id']):
                    item = i.toJSON()
                    data.append(item)
            elif action == 'addDebt':
                require_perm(request.user, 'add_debt')
                dateHour = timezone.localtime(timezone.now())
                datejoined = date.today().strftime('%Y-%m-%d')

                newDebt = Debt()
                newDebt.name = request.POST['name']
                newDebt.last_credit_date = request.POST['last_credit_date']
                newDebt.datehour = dateHour.strftime('%Y-%m-%d %I:%M %p')
                newDebt.totalDebt = Decimal(request.POST['totalDebt'])
                newDebt.save()

                newDetDebt = DetDebt()
                newDetDebt.last_credit_date = request.POST['last_credit_date']
                newDetDebt.datehour = newDebt.datehour
                newDetDebt.debt_id = newDebt.id
                newDetDebt.operation = '+'
                newDetDebt.quantity = Decimal(request.POST['totalDebt'])
                newDetDebt.description = request.POST['description']
                newDetDebt.save()
            elif action == 'payment':
                require_perm(request.user, 'change_debt')
                dateHour = timezone.localtime(timezone.now())
                datejoined = date.today().strftime('%Y-%m-%d')
                with transaction.atomic():
                    debt = Debt.objects.select_for_update().get(pk=request.POST['idDebt'])
                    payment = Decimal(request.POST['totalPayment'])

                    if payment > debt.totalDebt:
                        raise UserError('El abono no puede ser mayor que la deuda')

                    debt.totalDebt = debt.totalDebt - payment
                    debt.save()

                    newDetDebt = DetDebt()
                    newDetDebt.debt_id = debt.id
                    newDetDebt.last_debt_date = datejoined
                    newDetDebt.datehour = dateHour.strftime('%Y-%m-%d %I:%M %p')
                    newDetDebt.operation = '-'
                    newDetDebt.quantity = payment
                    newDetDebt.description = request.POST['description']
                    newDetDebt.save()
            elif action == 'increase':
                require_perm(request.user, 'change_debt')
                dateHour = timezone.localtime(timezone.now())
                datejoined = date.today().strftime('%Y-%m-%d')
                with transaction.atomic():
                    debt = Debt.objects.select_for_update().get(pk=request.POST['idIncreaseDebt'])
                    amount = Decimal(request.POST['totalPayment'])

                    debt.totalDebt = debt.totalDebt + amount
                    debt.save()

                    newDetDebt = DetDebt()
                    newDetDebt.debt_id = debt.id
                    newDetDebt.last_debt_date = datejoined
                    newDetDebt.datehour = dateHour.strftime('%Y-%m-%d %I:%M %p')
                    newDetDebt.operation = '+'
                    newDetDebt.quantity = amount
                    newDetDebt.description = request.POST['description']
                    newDetDebt.save()
            elif action == 'delete':
                perms = ['delete_debt']
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):
                    Debt.objects.using(db).get(pk=request.POST['id']).delete()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            log_error(logger, e, '[%s] error en acción=%s usuario=%s', __name__, request.POST.get('action'), request.user)
            data['error'] = error_message(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de cuentas por pagar'
        context['form'] = DebtForm()
        context['dl'] = get_dollar()
        context['month'] = date.today().month
        context['monthName'] = getMonthName(int(date.today().month))
        context['year'] = date.today().year
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context

class DebtReportPdfView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    permission_required = 'view_debt'

    def link_callback(self, uri, rel):
        return resolve_pdf_uri(uri)

    def getDebt(self, start, end):
        data = []
        try:
            allDebt = Debt.objects.filter(last_credit_date__gte=start, last_credit_date__lte=end)
            for d in allDebt:
                item = d.toJSON()
                item['dateformat'] = d.last_credit_date.strftime('%d/%m/%Y')
                data.append(item)
        except Exception:
            logger.exception('[%s] error armando datos del reporte', __name__)
        return data
    
    # @pdf_decorator(pdfname='new_filename.pdf')
    def get(self, request, *args, **kwargs):
        try:
            template = get_template('debt/reportDebt.html')

            allDebts = self.getDebt(self.kwargs['start'], self.kwargs['end'])
            quantity = 0
            total = 0

            try:
                for i in allDebts:
                    quantity += 1
                    total += float(i['totalDebt'])
            except:
                pass
            
            server_url = request.build_absolute_uri('/')
            dataCompany = getCompanyData()
            context = {
                'day': self.kwargs['start'] + ' - ' + self.kwargs['end'],
                'allDebts': allDebts,
                'quantity': quantity,
                'total': total,
                'comp': dataCompany,
                'url': getStaticUrl(),
                'icon': server_url + 'media/img/logo/logo.png',
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            
            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback    
            )
            return response
        except Exception as e:
            log_error(logger, e, '[%s] error generando PDF usuario=%s', __name__, request.user)
            messages.error(request, 'No se pudo generar el PDF. Intenta de nuevo o avisa al administrador.')
        return HttpResponseRedirect(reverse_lazy('crud:debt_list'))

