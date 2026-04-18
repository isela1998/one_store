## Esta es la tabla de los productos de venta
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpRequest
from django.views.generic import TemplateView, ListView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.db import transaction
import json
from decimal import Decimal
from django.db.models import IntegerField
from django.db.models.functions import Cast

from mf.crud.mixins import IsSuperuserMixin, ValidatePermissionMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from mf.crud.forms import ProductForm, CategoryForm, TypeProductForm, ProductUpForm
from mf.crud.models import Product, Category, Type_product, Dolar, CompanyInfo
from mf.crud.functions import *

import os
from django.template.loader import get_template
from django.contrib.staticfiles import finders
from django.conf import settings
from xhtml2pdf import pisa
from datetime import date

class ProductListView(LoginRequiredMixin, ValidatePermissionMixin, TemplateView):
    template_name = 'product/list.html'
    permission_required = 'view_product'

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
                for i in Product.objects.using(db).all():
                    item = i.toJSON()
                    try:
                        if(i.quantity < 5):
                            css = 'badge color1 fill-available text-light pointer-1'
                        elif(i.quantity > 5):
                            css = 'badge color2 fill-available text-light pointer-1'
                        item['css'] = css
                        data.append(item)
                    except Exception as e:
                        data['error'] = str(e)            
            elif action == 'add':
                perms = ['add_product']
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):
                    dolar = Dolar.objects.using(db).get(pk=1)
                    iva = float(1.16)

                    # cost = float(request.POST['cost'])
                    # gain_margin = price_dl - cost

                    price_dl = float(request.POST['price_dl'])
                    price_bs = price_dl * float(dolar.dolar)
                    cost = float(request.POST['cost'])
                    price = price_bs / iva
                    
                    quantity = float(request.POST['quantity'])
                    
                    with transaction.atomic():
                        p = Product()
                        p.category_id = request.POST['category']
                        p.type_product_id = request.POST['type_product']
                        p.product = request.POST['product']
                        p.code = request.POST['code']
                        p.brand = request.POST['brand']
                        p.description = request.POST['description']
                        p.quantity = quantity
                        p.cost = cost
                        p.price_dl = price_dl
                        p.price = price
                        p.price_bs = price_bs
                        p.save()     
            elif action == 'addCategory':
                perms = ['add_category']
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):
                    ctg = Category()
                    ctg.name = request.POST['name']
                    ctg.save(using='default')
            elif action == 'addType':
                perms = ['add_type_product']
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):
                    type_p = Type_product()
                    type_p.name = request.POST['name']
                    type_p.save(using='default')
            elif action == 'edit':
                perms = ['change_product']
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):                       
                    dolar = Dolar.objects.using(db).get(pk=1)
                    iva = float(1.16)

                    cost = float(request.POST['cost'])
                    price_dl = float(request.POST['price_dl'])
                    price_bs = price_dl * float(dolar.dolar)
                    price = price_bs / iva
                    
                    with transaction.atomic():
                        p = Product.objects.using(db).get(pk=request.POST['id'])
                        p.category_id = request.POST['category']
                        p.type_product_id = request.POST['type_product']
                        p.product = request.POST['product']
                        p.code = request.POST['code']
                        p.brand = request.POST['brand']
                        p.description = request.POST['description']
                        p.quantity = float(request.POST['quantity'])
                        p.cost = cost
                        p.price_dl = price_dl
                        p.price = price
                        p.price_bs = price_bs
                        p.save()
            elif action == 'IncreaseProduct':
                perms = ['change_product']
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):
                    data =  []
                    p = Product.objects.get(pk=request.POST['id'])
                    p.quantity = float(p.quantity) + float(request.POST['quantity'])
                    p.save()
            elif action == 'delete':
                perms = ['delete_product']
                group = request.user.groups.first()
                authorized = ValidatePermissions(perms, group)
                if(authorized == False):
                    data['error'] = 'Disculpe, usted no tiene permisos para ejecutar esta acción'
                elif(authorized == True):
                    product = Product.objects.using(db).get(pk=request.POST['id']).delete()
            else:
                data['error'] = "Ha ocurrido un error"
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Productos'
        context['dl'] = get_dollar()
        context['formProduct'] = ProductForm()
        context['formUpProduct'] = ProductUpForm()
        context['formCategory'] = CategoryForm()
        context['formType'] = TypeProductForm()
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context

class InventaryPdfView(LoginRequiredMixin, ValidatePermissionMixin, TemplateView):
    permission_required = 'view_product'

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

    def get(self, request, *args, **kwargs):
        data = []
        try:
            template = get_template('product/report.html')
            direction = []

            today = date.today().strftime('%d-%m-%Y')
            dataCompany = getCompanyData()
            totalInventary = 0
            
            for i in Product.objects.all().order_by('category'):
                totalInventary += i.quantity
                data.append(i.toJSON())

            server_url = request.build_absolute_uri('/')
            context = {
                'data': data,
                'today': today,
                'comp': dataCompany,
                'totalInventary': int(totalInventary),
                'url': getStaticUrl(),
                'icon': 'https://jeantren-86cc3b8c232c.herokuapp.com/media/img/logo/logo.png',
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
            pisa_status = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback    
            )
            return response
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('crud:products_list'))
