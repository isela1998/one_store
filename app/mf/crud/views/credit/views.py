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

from mf.crud.models import Credit, DetCredit, Method_pay
from mf.crud.forms import DetCreditForm
from mf.crud.functions import *
from django.db.models import Q

import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
# from django_xhtml2pdf.utils import pdf_decorator
from django.contrib.staticfiles import finders

class CreditListView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    model = Credit
    template_name = 'credit/list.html'
    permission_required = 'view_credit'

    @method_decorator(csrf_exempt)
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
                dl = get_dollar()
                dl_value = dl.get('dolar1')
                all = int(request.POST['all'])

                print('all es',all)

                if all == 0:
                    for i in Credit.objects.filter(last_credit_date__gte=request.POST['start'], last_credit_date__lte=request.POST['end']).exclude(totalDebt__lte=0):
                        item = i.toJSON()
                        item['dl'] = float(dl_value)
                        item['totalDebtBs'] = round(float(item['totalDebt']) * float(dl_value), 2)
                        data.append(item)
                if all == 1:
                    for i in Credit.objects.filter(last_credit_date__gte=request.POST['start'], last_credit_date__lte=request.POST['end']):
                        item = i.toJSON()
                        item['dl'] = float(dl_value)
                        item['totalDebtBs'] = round(float(item['totalDebt']) * float(dl_value), 2)
                        data.append(item)
            elif action == 'searchdata2':
                data = []
                for i in DetCredit.objects.filter(credit__id=request.POST['id']).exclude(status=0):
                    item = i.toJSON()
                    data.append(item)
            elif action == 'payment':
                dateHour = timezone.localtime(timezone.now())
                datejoined = date.today().strftime('%Y-%m-%d')
                credit = Credit.objects.get(pk=request.POST['idCredit'])

                dl = get_dollar()
                dl_value = dl.get('dolar1')

                with transaction.atomic():
                    method = Method_pay.objects.get(pk=request.POST['method_pay'])
                    totalPayment = request.POST['totalPayment']
                    amount = 0
                    amountBs = 0
                    if method.type_symbol == '$':
                        amount = float(totalPayment)
                        amountBs = round((float(totalPayment) * float(dl_value)), 2)
                        totalDebt = float(credit.totalDebt) - float(totalPayment)
                    elif method.type_symbol == 'Bs':
                        amountBs = float(totalPayment)
                        amount = round((float(totalPayment) / float(dl_value)), 2)
                        totalDebt = float(credit.totalDebt) - float(amount)
                    credit.totalDebt = totalDebt
                    credit.save()

                    newDetCredit = DetCredit()
                    newDetCredit.credit_id = credit.id
                    newDetCredit.last_credit_date = datejoined
                    newDetCredit.method_pay_id = request.POST['method_pay']
                    newDetCredit.datehour = dateHour.strftime('%Y-%m-%d %I:%M %p')
                    newDetCredit.operation = '-'
                    newDetCredit.quantity = float(amount)
                    newDetCredit.quantitybs = float(amountBs)
                    newDetCredit.description = request.POST['description']
                    newDetCredit.save()
            elif action == 'delete':
                group = request.user.groups.first()
                if group != 1:
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                else:
                    Credit.objects.using(db).get(pk=request.POST['id']).delete()
            elif action == 'deleteItem':
                print('Entro en el delelte', request.POST)
                group = request.user.groups.first()
                if group.id != 1:
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                else:
                    with transaction.atomic():
                        d = DetCredit.objects.get(pk=request.POST['id'])

                        c = Credit.objects.get(pk=d.credit.id)
                        c.totalDebt = float(c.totalDebt) + float(d.quantity)
                        c.save()

                        d.status = 0
                        d.save()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
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
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    sUrl = settings.STATIC_URL        # Typically /static/
                    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    mUrl = settings.MEDIA_URL         # Typically /media/
                    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(mUrl):
                            path = os.path.join(mRoot, uri.replace(mUrl, ""))
                    elif uri.startswith(sUrl):
                            path = os.path.join(sRoot, uri.replace(sUrl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise Exception(
                            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )
            return path

    def getCredit(self, start, end):
        data = []
        try:
            allCredit = Credit.objects.filter(last_credit_date__gte=start, last_credit_date__lte=end)
            for c in allCredit:
                item = c.toJSON()
                item['dateformat'] = c.last_credit_date.strftime('%d/%m/%Y')
                data.append(item)
        except:
            pass
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
                'icon': 'http://127.0.0.1:8000/media/img/logo/logo.png',
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            
            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback    
            )
            return response
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('crud:credit_list'))

