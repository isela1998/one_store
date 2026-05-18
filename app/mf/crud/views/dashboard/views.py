from django.views.generic import TemplateView
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from urllib import request
from django.utils import timezone
from django.db import transaction
from config.settings import MEDIA_URL

from django.contrib.auth.mixins import LoginRequiredMixin
from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin

from datetime import date
from datetime import datetime, timedelta

from mf.crud.models import Dolar, Product, Sale, DetSale, DetCredit, Credit
from django.db.models.functions import Coalesce
from django.db.models import Sum

from mf.crud.functions import *

import os
from pathlib import Path

class DashboardView(LoginRequiredMixin, ValidatePermissionMixin, TemplateView):
    template_name = 'dashboard.html'
    permission_required = 'view_sale'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            print(request)
            db = 'default'
            action = request.POST['action']
            if action == 'get_graph_sales':
                group = request.user.groups.first()
                if group.id == 1:
                    data = self.get_graph_sales(db)
            elif action == 'get_graph_products':
                group = request.user.groups.first()
                if group.id == 1:
                    data = {
                        'name': 'Ventas',
                        'text': 'Productos',
                        'colorByPoint': True,
                        'data': self.get_graph_products(db)
                    }
            elif action == 'upDolar':
                perms = ['change_dolar',]
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                if ',' in request.POST['dolar']:  
                    data['error'] = 'Por favor, utiliza punto (.) en lugar de coma (,)'
                elif(authorized == True):
                    generalRate = float(request.POST['dolar'])
                    with transaction.atomic():
                        dolar = Dolar.objects.get(pk=1)
                        dolar.dolar = float(request.POST['dolar'])
                        dolar.save()
                    self.update_prices(generalRate)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)
    
    
    def update_prices(self, dl):
        data = []
        product = Product.objects.using('default').all()
        for p in product:
            p.price_bs = float(p.price_dl) * float(dl)
            p.save()
        return data

    def get_graph_sales(self, db):
        data_contado = []
        data_credito = []
        data_abonos = []
        
        try:
            year = datetime.now().year
            for m in range(1, 13):
                # Ventas al contado (status=0)
                total_contado = Sale.objects.filter(
                    datejoined__year=year, 
                    datejoined__month=m, 
                    status=0
                ).aggregate(r=Coalesce(Sum('total'), 0.0)).get('r')
                data_contado.append(float(total_contado))
                
                # Ventas a crédito (status=1)
                total_credito = Sale.objects.filter(
                    datejoined__year=year, 
                    datejoined__month=m, 
                    status=1
                ).aggregate(r=Coalesce(Sum('total'), 0.0)).get('r')
                data_credito.append(float(total_credito))

                # Créditos cobrados (status=1)
                total_abonos = DetCredit.objects.filter(
                    last_credit_date__year=year, 
                    last_credit_date__month=m, 
                    status=1,
                    operation='-'
                ).aggregate(r=Coalesce(Sum('quantity'), 0.0)).get('r')
                data_abonos.append(float(total_abonos))

                
        except Exception as e:
            print(f"Error en la gráfica: {e}")
            
        return [
            {
                'name': 'Ventas al Contado',
                'data': data_contado,
                'color': '#2ecc71'
            },
            {
                'name': 'Ventas a Crédito',
                'data': data_credito,
                'color': '#f6c23e'
            },
            {
                'name': 'Abonos de Créditos',
                'data': data_abonos,
                'color': '#40e0d0'
            }
        ]

    def get_graph_products(self, db):
        data = []
        year = datetime.now().year
        month = datetime.now().month
        try:
            sales_data = DetSale.objects.using(db).filter(
                sale__datejoined__year=year,
                sale__datejoined__month=month,
                prod__status=1
            ).values(
                'prod__brand', 'prod__product'
            ).annotate(
                total_qty=Sum('quantity') 
            ).order_by('-total_qty')[:15]
            
            for item in sales_data:
                data.append({
                    'name': f"{item['prod__brand']} {item['prod__product']}",
                    'y': float(item['total_qty']) 
                })
        except Exception as e:
            print(f"Error en productos: {e}")
            
        return data

    def get_name_month(self):
        data = ''
        month = datetime.now().month
        if month == 1:
            data = 'Enero'
        elif month == 2:
            data = 'Febrero'
        elif month == 3:
            data = 'Marzo'
        elif month == 4:
            data = 'Abril'
        elif month == 5:
            data = 'Mayo'
        elif month == 6:
            data = 'Junio'
        elif month == 7:
            data = 'Julio'
        elif month == 8:
            data = 'Agosto'
        elif month == 9:
            data = 'Septiembre'
        elif month == 10:
            data = 'Octubre'
        elif month == 11:
            data = 'Noviembre'
        elif month == 12:
            data = 'Diciembre'
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['panel'] = 'PRINCIPAL'
        context['today'] = date.today()
        context['dl'] = get_dollar()
        context['month'] = self.get_name_month()
        context['year'] = datetime.now().year
        context['title_pag'] = 'Panel principal'
        context['title'] = 'INICIO'
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        context['data'] = getCompanyData()
        return context
