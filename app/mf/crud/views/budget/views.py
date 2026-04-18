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
from django.db.models import Q

import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
# from django_xhtml2pdf.utils import pdf_decorator
from django.contrib.staticfiles import finders

class BudgetListView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    model = Budget
    template_name = 'budget/list.html'
    permission_required = 'view_sale'

    @method_decorator(csrf_exempt)
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
                for i in Budget.objects.using(db).all():
                    item = i.toJSON()
                    data.append(item)
            elif action == 'delete':
                Budget.objects.using(db).get(pk=request.POST['id']).delete()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
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
                'icon': 'https://jeantren-86cc3b8c232c.herokuapp.com/media/img/logo/logo.png',
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="/Users/Isela/Desktop/'+n_order+'.pdf"'
             
            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback    
            )
            return response
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('crud:budget_list'))

