from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpRequest
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.db import transaction
from datetime import date, datetime, timedelta
import json
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP


from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from mf.crud.models import Credit, DetCredit, DetSale, Method_pay
from mf.crud.forms import DetCreditForm
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

def _det_credit_relations(qs):
    """Precarga las relaciones que usa DetCredit.toJSON() (evita consultas N+1)."""
    return qs.select_related(
        'method_pay', 'sale__client', 'sale__method_pay', 'sale__method_pay1', 'sale__method_pay2'
    ).prefetch_related(
        Prefetch('sale__detsale_set', queryset=DetSale.objects.select_related('prod__category', 'prod__type_product'))
    )


def _credit_relations(qs):
    """Precarga las relaciones que usa Credit.toJSON() (evita consultas N+1)."""
    return qs.select_related('client').prefetch_related(
        Prefetch('detcredit_set', queryset=_det_credit_relations(DetCredit.objects.all()))
    )


class CreditListView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    model = Credit
    template_name = 'credit/list.html'
    permission_required = 'view_credit'

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
                all = int(request.POST['all'])
                include = int(request.POST['include'])
                
                if all == 0:
                    if include == 0:
                        for i in _credit_relations(Credit.objects.filter(last_credit_date__gte=request.POST['start'], last_credit_date__lte=request.POST['end']).exclude(totalDebt__lte=0)):
                            item = i.toJSON()
                            item['dl'] = float(dl_value)
                            item['totalDebtBs'] = round(float(item['totalDebt']) * float(dl_value), 2)
                            data.append(item)
                    if include == 1:
                        for i in _credit_relations(Credit.objects.filter(last_credit_date__gte=request.POST['start'], last_credit_date__lte=request.POST['end'])):
                            item = i.toJSON()
                            item['dl'] = float(dl_value)
                            item['totalDebtBs'] = round(float(item['totalDebt']) * float(dl_value), 2)
                            data.append(item)
                if all == 1:
                    if include == 0:
                        for i in _credit_relations(Credit.objects.filter(totalDebt__gt=0)):
                            item = i.toJSON()
                            item['dl'] = float(dl_value)
                            item['totalDebtBs'] = round(float(item['totalDebt']) * float(dl_value), 2)
                            data.append(item)
                    if include == 1:
                         for i in _credit_relations(Credit.objects.all()):
                            item = i.toJSON()
                            item['dl'] = float(dl_value)
                            item['totalDebtBs'] = round(float(item['totalDebt']) * float(dl_value), 2)
                            data.append(item)
            elif action == 'searchdata2':
                data = []
                for i in _det_credit_relations(DetCredit.objects.filter(credit__id=request.POST['id']).exclude(status=0)):
                    item = i.toJSON()
                    data.append(item)
            elif action == 'payment':
                require_perm(request.user, 'change_credit')
                dateHour = timezone.localtime(timezone.now())
                date_joined_str = request.POST['datejoined']
                if date_joined_str:
                    date_obj = datetime.strptime(date_joined_str, '%Y-%m-%d')
                    datejoined = date_obj.strftime('%Y-%m-%d')

                    current_time = timezone.localtime(timezone.now()).time()
                    dateHour = datetime.combine(date_obj, current_time)
                else:
                    now = timezone.localtime(timezone.now())
                    datejoined = date.today().strftime('%Y-%m-%d')
                    dateHour = now

                dl = get_dollar()
                dl_value = dl.get('dolar1')

                with transaction.atomic():
                    credit = Credit.objects.select_for_update().get(pk=request.POST['idCredit'])
                    method = Method_pay.objects.get(pk=request.POST['method_pay'])
                    totalPayment = Decimal(request.POST['totalPayment'])
                    rate = Decimal(str(dl_value))
                    require_dollar_rate(rate)
                    cent = Decimal('0.01')
                    if method.type_symbol == '$':
                        amount = totalPayment
                        amountBs = (totalPayment * rate).quantize(cent, rounding=ROUND_HALF_UP)
                    elif method.type_symbol == 'Bs':
                        amountBs = totalPayment
                        amount = (totalPayment / rate).quantize(cent, rounding=ROUND_HALF_UP)
                    else:
                        raise UserError('La moneda del método de pago no es válida')
                    credit.totalDebt = credit.totalDebt - amount
                    credit.save()

                    newDetCredit = DetCredit()
                    newDetCredit.credit_id = credit.id
                    newDetCredit.last_credit_date = datejoined
                    newDetCredit.method_pay_id = method.id
                    newDetCredit.datehour = dateHour.strftime('%Y-%m-%d %I:%M %p')
                    newDetCredit.operation = '-'
                    newDetCredit.quantity = amount
                    newDetCredit.quantitybs = amountBs
                    newDetCredit.description = ' Método: ' + str(method.name) + '. ' + request.POST['description']
                    newDetCredit.save()

                    check_pay_all = request.POST.get('checkPayAll') == '1'
                    if check_pay_all and credit.totalDebt > 0:
                        residuo = credit.totalDebt

                        closeCredit = DetCredit()
                        closeCredit.credit_id = credit.id
                        closeCredit.last_credit_date = datejoined
                        closeCredit.method_pay_id = 1
                        closeCredit.datehour = dateHour.strftime('%Y-%m-%d %I:%M %p')
                        closeCredit.operation = '-'
                        closeCredit.quantity = residuo
                        closeCredit.quantitybs = (residuo * rate).quantize(cent, rounding=ROUND_HALF_UP)
                        closeCredit.description = 'Marcado manualmente como pagado'
                        closeCredit.status = 2
                        closeCredit.save()

                        credit.totalDebt = 0
                        credit.save()
            elif action == 'delete':
                group = request.user.groups.first()
                if group != 1:
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                else:
                    Credit.objects.using(db).get(pk=request.POST['id']).delete()
            elif action == 'deleteItem':
                if not request.user.is_superuser:
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                else:
                    with transaction.atomic():
                        d = DetCredit.objects.select_for_update().get(pk=request.POST['id'])
                        if d.status == 0:
                            raise UserError('Este abono ya fue eliminado')
                        if d.operation != '-':
                            raise UserError('Solo se pueden eliminar abonos')

                        c = Credit.objects.select_for_update().get(pk=d.credit_id)
                        c.totalDebt = c.totalDebt + d.quantity
                        c.save()

                        d.status = 0
                        d.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            log_error(logger, e, '[%s] error en acción=%s usuario=%s', __name__, request.POST.get('action'), request.user)
            data['error'] = error_message(e)
        return JsonResponse(data, safe=False)

    def get_methods_pay(self):
        data = []
        for i in Method_pay.objects.exclude(pk=1):
            data.append(i.toJSON())
        return data
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Creditos'
        context['dl'] = get_dollar()
        context['month'] = date.today().month
        context['monthName'] = getMonthName(int(date.today().month))
        context['year'] = date.today().year
        context['form'] = DetCreditForm()
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        context['methods'] = self.get_methods_pay()
        return context

class CreditReportPdfView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    permission_required = 'view_credit'

    def link_callback(self, uri, rel):
        return resolve_pdf_uri(uri)

    def getCredit(self, start, end):
        data = []
        try:
            allCredit = Credit.objects.filter(last_credit_date__gte=start, last_credit_date__lte=end)
            for c in allCredit:
                item = c.toJSON()
                item['dateformat'] = c.last_credit_date.strftime('%d/%m/%Y')
                data.append(item)
        except Exception:
            logger.exception('[%s] error armando datos del reporte', __name__)
        return data
    
    # @pdf_decorator(pdfname='new_filename.pdf')
    def get(self, request, *args, **kwargs):
        try:
            template = get_template('credit/reportCredit.html')

            allCredits = self.getCredit(self.kwargs['start'], self.kwargs['end'])
            quantity = 0
            total = 0

            try:
                for i in allCredits:
                    quantity += 1
                    total += float(i['totalDebt'])
            except:
                pass
            
            server_url = request.build_absolute_uri('/')
            dataCompany = getCompanyData()
            context = {
                'day': self.kwargs['start'] + ' - ' + self.kwargs['end'],
                'allCredits': allCredits,
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
        return HttpResponseRedirect(reverse_lazy('crud:credit_list'))

