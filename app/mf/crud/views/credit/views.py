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

from mf.crud.models import Credit, DetCredit
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
                for i in Credit.objects.using(db).filter(last_credit_date__gte=request.POST['start'], last_credit_date__lte=request.POST['end']):
                    item = i.toJSON()
                    data.append(item)
            elif action == 'searchdata2':
                data = []
                for i in DetCredit.objects.filter(credit__id=request.POST['id']):
                    item = i.toJSON()
                    data.append(item)
            elif action == 'payment':
                dateHour = timezone.localtime(timezone.now())
                datejoined = date.today().strftime('%Y-%m-%d')
                credit = Credit.objects.get(pk=request.POST['idCredit'])

                if(float(request.POST['totalPayment']) > float(credit.totalDebt)):
                    data['error'] = 'El abono no puede ser mayor que la deuda'
                else:
                    with transaction.atomic():
                        credit.totalDebt = float(credit.totalDebt) - float(request.POST['totalPayment'])
                        credit.save()

                        newDetCredit = DetCredit()
                        newDetCredit.credit_id = credit.id
                        newDetCredit.last_credit_date = datejoined
                        newDetCredit.datehour = dateHour.strftime('%Y-%m-%d %I:%M %p')
                        newDetCredit.operation = '-'
                        newDetCredit.quantity = float(request.POST['totalPayment'])
                        newDetCredit.description = request.POST['description']
                        newDetCredit.save()
            elif action == 'delete':
                perms = ['delete_product']
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):
                    Credit.objects.using(db).get(pk=request.POST['id']).delete()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Creditos'
        context['dl'] = get_dollar()
        context['month'] = date.today().month
        context['monthName'] = getMonthName(int(date.today().month))
        context['year'] = date.today().year
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
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
                'icon': server_url + '/media/img/logo/logo_.png',
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

