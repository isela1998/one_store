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

from mf.crud.models import Product, Sale, Credit, DetCredit, Budget, DetSale, DetBudget, Client, Method_pay, Dolar, CashMovement
from mf.crud.forms import SaleForm, ClientForm, MethodPayForm, ProductForm, CashMovementForm
from mf.crud.functions import *
from django.db.models import Q

import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
# from django_xhtml2pdf.utils import pdf_decorator
from django.contrib.staticfiles import finders

class SaleListView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    model = Sale
    template_name = 'sale/list.html'
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
                for i in Sale.objects.using(db).filter(datejoined__gte=request.POST['start'], datejoined__lte=request.POST['end']):
                    item = i.toJSON()
                    if(i.status == 0):
                        css = 'badge badge-success text-dark pointer-1'
                        status = 'Pagada'
                    elif(i.status == 1):
                        css = 'badge badge-warning text-dark pointer-1'
                        status = 'Crédito'
                    elif(i.status == 2):
                        css = 'badge badge-danger text-dark pointer-1'
                        status = 'Anulada'
                    item['statusName'] = status
                    item['css'] = css
                    data.append(item)
            elif action == 'return':
                datejoined = date.today().strftime('%Y-%m-%d')
                sale = Sale.objects.using(db).get(pk=request.POST['id'])
                
                if sale.status == 2:
                    data['error'] = 'Ya esta venta fue anulada anteriormente'
                else:
                    with transaction.atomic(using=db):
                        det = DetSale.objects.using(db).filter(sale_id=request.POST['id'])
                        for i in det:
                            pw = Product.objects.using(db).get(pk=i.prod_id)
                            pw.quantity = float(pw.quantity) + float(i.quantity)
                            pw.save(using=db)
                            
                        if sale.type_sale == 'Crédito':
                            det_credits = DetCredit.objects.using(db).filter(sale=sale)
                                
                            for dc in det_credits:
                                credit_header = dc.credit
                                credit_header.totalDebt -= dc.quantity
                                credit_header.save(using=db)
                                    
                                dc.delete(using=db)

                        sale.status = 2
                        sale.save(using=db)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Ventas'
        context['create_url'] = reverse_lazy('crud:sale_create')
        context['dl'] = get_dollar()
        context['list_url'] = reverse_lazy('crud:sale_list')
        context['month'] = date.today().month
        context['monthName'] = getMonthName(int(date.today().month))
        context['year'] = date.today().year
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context

class SaleCreateView(CreateView, LoginRequiredMixin, ValidatePermissionMixin):
    model = Sale
    form_class = SaleForm
    template_name = 'sale/create.html'
    permission_required = 'add_sale'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        db = 'default'
        try:
            sede = request.POST['sede']
            action = request.POST['action']
            if action == 'search_products':
                data = []

                term = request.POST.get('term', '').strip()
                if not term:
                    return JsonResponse(data, safe=False)

                code = Product.objects.using(db).filter(code__icontains=term).exclude(quantity__lte=0).exclude(status=0)[0:10]
                products = Product.objects.using(db).filter(product__icontains=term).exclude(quantity__lte=0).exclude(status=0)[0:10]
                brand = Product.objects.using(db).filter(brand__icontains=term).exclude(quantity__lte=0).exclude(status=0)[0:10]
                for i in code:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = '||'+ i.code +'||' + ' - ' + i.brand + ' ' + i.product + ' (' + i.type_product.name + ') - ' + '$: ' + item['price_dl'] + ' / Bs: ' + item['price_bs']
                    item['initial'] = i.quantity
                    for d in data:
                        if d['id'] == i.id:
                            exist = 1
                    if exist == 0:
                        data.append(item)
                for i in brand:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = '||'+ i.code +'|| ' + ' - ' + i.brand + ' ' + i.product + ' (' + i.type_product.name + ') - ' + '$: ' + item['price_dl'] + ' / Bs: ' + item['price_bs']
                    item['initial'] = i.quantity
                    for d in data:
                        if d['id'] == i.id:
                            exist = 1
                    if exist == 0:
                        data.append(item)
                for i in products:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = '||'+ i.code +'|| ' + ' - ' + i.brand + ' ' + i.product + ' (' + i.type_product.name + ') - ' + '$: ' + item['price_dl'] + ' / Bs: ' + item['price_bs']
                    item['initial'] = i.quantity
                    for d in data:
                        if d['id'] == i.id:
                            exist = 1
                    if exist == 0:
                        data.append(item)
            elif action == 'search_client':
                data = []
                term = request.POST['term']
                client = Client.objects.using(db).filter(names__icontains=term)[0:10]
                ci = Client.objects.using(db).filter(ci__icontains=term)[0:10]
                for i in client:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = i.names + ' ' + i.identity + '-' + i.ci
                    for d in data:
                        if d['id'] == i.id:
                            exist = 1
                    if exist == 0:
                        data.append(item)
                for i in ci:
                    exist = 0
                    item = i.toJSON()
                    item['text'] = i.names + ' ' + i.identity + '-' + i.ci
                    for d in data:
                        if d['id'] == i.id:
                            exist = 1
                    if exist == 0:
                        data.append(item)
            elif action == 'add':
                data = self.addSale(db, request.POST, request.user)
            elif action == 'cashMovement':
                dolar = Dolar.objects.using(db).get(pk=1)
                dl = float(dolar.dolar)

                method = Method_pay.objects.get(pk=request.POST['method_pay'])
                type_symbol = method.type_symbol

                c = CashMovement()
                c.user_id = request.user.id
                c.tipo = request.POST['tipo']
                c.method_pay_id = method.id

                if type_symbol == 'Bs':
                    c.amount_bs = Decimal(request.POST['amount_bs'])
                    c.amount_dl = Decimal(request.POST['amount_bs']) / Decimal(dl)  
                else:
                    c.amount_dl = Decimal(request.POST['amount_bs'])
                    c.amount_bs = Decimal(request.POST['amount_bs']) * Decimal(dl)  

                c.description = request.POST['description']
                c.save()
            elif action == 'addBudget':
                datejoined = date.today().strftime('%Y-%m-%d')
                dolar = Dolar.objects.using(db).get(pk=1)
                dl = float(dolar.dolar)
                
                try:
                    with transaction.atomic():
                        sales = json.loads(request.POST['sales'])
                        sale = Budget()
                        sale.user = request.user.username
                        sale.datejoined = datejoined
                        sale.client_id = int(request.POST['searchClient'])
                        sale.subtotal = float(request.POST['quantity_dolars']) + float(sales['discount'])
                        sale.discount = float(sales['discount'])
                        sale.total = float(request.POST['quantity_dolars'])
                        sale.description = request.POST['description']
                        sale.rate = float(dl)
                        sale.budget_number = self.get_lastet_budget()
                        sale.save(using=db)              

                        for i in sales['products']:
                            det = DetBudget()
                            det.budget_id = sale.id
                            det.prod_id = i['id']
                            det.quantity = float(i['quantity'])
                            det.price = float(i['price_dl'])
                            det.total = float(i['quantity']) * float(i['price_dl'])
                            det.rate = float(dl)
                            det.save(using=db)
                        data = {
                            'id': sale.id,
                        }
                except Exception as e:
                    data = {
                        'error': str(e)
                    }
            elif action == 'addClient':
                cli = Client()
                cli.names = request.POST['names']
                cli.identity = request.POST['identity']
                cli.ci = request.POST['ci']
                cli.address = request.POST['address']
                cli.contact = request.POST['contact']
                cli.save(using='default')
                data = {
                    'id': cli.pk,
                    'names': cli.names,
                    'ci': cli.identity + '-' + cli.ci
                }
            elif action == 'addProduct':
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
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            print(e)
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def addSale(self, db, requestPOST, requestUser):
        data = {}
        datejoined = date.today().strftime('%Y-%m-%d')
        
        dolar_obj = Dolar.objects.using(db).get(pk=1)
        dl = Decimal(str(dolar_obj.dolar)) 

        clientId = int(requestPOST['searchClient'])
        sales = json.loads(requestPOST['sales'])

        saveCreditDetail = False
        
        try:
            with transaction.atomic(using=db):
                sale = Sale()
                dateHour = timezone.localtime(timezone.now())
                
                discount = Decimal(str(sales['discount']))
                subtotal = Decimal(str(sales['total'])) + discount
                total = subtotal - discount
                
                sale.user = requestUser.username
                sale.datejoined = datejoined
                sale.datehour = dateHour.strftime('%Y-%m-%d %I:%M %p')
                sale.client_id = clientId
                sale.subtotal = subtotal
                sale.discount = discount
                sale.total = total
                sale.totalBs = total * dl
                sale.rate = dl
                sale.description = requestPOST.get('description', '')
                sale.invoice_number = self.get_lastet_invoice(db)
                
                type_sale = requestPOST['inlineRadioOptions']
                
                if type_sale == 'option1':
                    sale.type_sale = 'Al Contado'
                    sale.method_pay_id = requestPOST['method_pay']
                    sale.received = Decimal(str(requestPOST.get('received', '0.00')))
                    sale.method_pay1_id = requestPOST['method_pay1']
                    sale.received1 = Decimal(str(requestPOST.get('received1', '0.00')))
                    sale.method_pay2_id = requestPOST['method_pay2']
                    sale.received2 = Decimal(str(requestPOST.get('received2', '0.00')))
                elif type_sale == 'option2':
                    saveCreditDetail = True
                    sale.type_sale = 'Crédito'
                    sale.method_pay_id = 1
                    sale.received = Decimal('0.00')
                    sale.exchange = Decimal('0.00')
                    sale.method_pay1_id = 1
                    sale.received1 = Decimal('0.00')
                    sale.exchange1 = Decimal('0.00')
                    sale.method_pay2_id = 1
                    sale.received2 = Decimal('0.00')
                    sale.exchange2 = Decimal('0.00')
                    sale.status = 1
                    
                sale.save(using=db)

                if saveCreditDetail:
                    try:
                        updateCredit = Credit.objects.using(db).get(client__id=clientId)
                        updateCredit.last_credit_date = datejoined
                        updateCredit.datehour = sale.datehour
                        updateCredit.totalDebt = Decimal(str(updateCredit.totalDebt)) + total
                        updateCredit.save(using=db)
                        credit_id = updateCredit.id
                    except Credit.DoesNotExist:
                        newCredit = Credit()
                        newCredit.client_id = clientId
                        newCredit.last_credit_date = datejoined
                        newCredit.datehour = sale.datehour
                        newCredit.totalDebt = total
                        newCredit.save(using=db)
                        credit_id = newCredit.id

                    newDet = DetCredit()
                    newDet.last_credit_date = datejoined
                    newDet.datehour = sale.datehour
                    newDet.credit_id = credit_id
                    newDet.method_pay_id = 1
                    newDet.sale_id = sale.id
                    newDet.operation = '+'
                    newDet.quantity = total
                    newDet.quantitybs = total * dl
                    newDet.description = f"Factura # {sale.invoice_number}"
                    newDet.save(using=db)

                for i in sales['products']:
                    pw = Product.objects.using(db).select_for_update().get(pk=i['id'])
                    cantidad_vendida = Decimal(str(i['quantity']))

                    if cantidad_vendida <= 0:
                        raise Exception(f"Se detectó una cantidad inválida ({cantidad_vendida}) para el producto '{pw.category.name} - {pw.product} ({pw.type_product.name})'. Por favor, verifique e intente de nuevo.")

                    stock_actual = Decimal(str(pw.quantity))

                    if stock_actual < cantidad_vendida:
                        stock_formateado = int(stock_actual) if stock_actual % 1 == 0 else float(stock_actual)
                        cant_formateada = int(cantidad_vendida) if cantidad_vendida % 1 == 0 else float(cantidad_vendida)        
                        raise Exception(f"Stock insuficiente para '{pw.category.name} - {pw.product} ({pw.type_product.name})'. Disponible: {stock_formateado}, Solicitado: {cant_formateada}")
                    
                    pw.quantity = stock_actual - cantidad_vendida
                    pw.save(using=db)

                    det = DetSale()
                    det.sale_id = sale.id
                    det.prod_id = i['id']
                    det.quantity = cantidad_vendida
                    det.price = Decimal(str(pw.price_dl))
                    det.total = Decimal(str(pw.price_dl)) * cantidad_vendida
                    det.rate = dl
                    det.save(using=db)
                    
            data = { 'id': sale.id }

        except Exception as e:
            data = {
                'error': str(e)
            }

        return data

    def get_methods_pay(self):
        data = []
        for i in Method_pay.objects.all():
            data.append(i.toJSON())
        return data

    def get_lastet_invoice(self, db):
        try:
            lastSale = Sale.objects.using(db).last()
            last_invoice = lastSale.invoice_number
            new_invoice = int(last_invoice) + 1
        except:
            new_invoice = 1
        n_invoice = f"{new_invoice:0>8}"
        return n_invoice

    def get_lastet_budget(self):
        try:
            budget = Budget.objects.last()
            last_budget = budget.budget_number
            new_budget = int(last_budget) + 1
            n_budget = f"{new_budget:0>8}"
        except:
            new_budget = 1
            n_budget = f"{new_budget:0>8}"
        return n_budget

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'MÓDULO DE FACTURACIÓN - NUEVA VENTA'
        context['formClient'] = ClientForm()
        context['formMethod'] = MethodPayForm()
        context['formProduct'] = ProductForm()
        context['formCashMovement'] = CashMovementForm()
        context['methods'] = self.get_methods_pay()
        context['action'] = 'add'
        context['dl1'] = get_dollar()
        context['det'] = []
        context['cli'] = []
        context['data'] = getCompanyData()
        context['today'] = date.today()
        context['events'] = get_events_today()
        context['q_events'] = get_q_events_today()
        return context

class SaleInvoicePdfView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    permission_required = 'add_sale'

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
            template = get_template('sale/invoice.html')
            direction = []
            
            sale = Sale.objects.using(db).get(pk=self.kwargs['s'])

            server_url = request.build_absolute_uri('/')
            print('URL ESSS' + server_url)

            dataCompany = getCompanyData()
            context = {
                'sale': sale,
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
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('crud:sale_list'))

class SalesPdfView(LoginRequiredMixin, ValidatePermissionMixin, ListView):
    permission_required = 'add_sale'

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

    def getByPayMethod(self, start, end, exchange_rate=1.0):
        data = []
        grand_total_usd = 0.0 
        
        try:
            # Traemos las consultas nativas (filtramos una sola vez para velocidad)
            sales = Sale.objects.filter(datejoined__gte=start, datejoined__lte=end).exclude(status=2)
            credits = DetCredit.objects.filter(last_credit_date__gte=start, last_credit_date__lte=end).exclude(operation='+').exclude(status=0)
            
            for m in Method_pay.objects.all().exclude(pk=1):
                idMethodPay = m.id
                name = m.name
                type_total = m.type_symbol  # '$' or 'Bs'
                
                sales_amount = 0.0
                payments_amount = 0.0
                cash_in = 0.0
                cash_out = 0.0
                quantity = 0  # <--- Tu contador de transacciones
                
                # --- CONTAR Y SUMAR VENTAS ---
                for s in sales:
                    # Comparamos usando los IDs directos del ORM (Evita el fallo del toJSON)
                    if s.method_pay_id == idMethodPay and float(s.received) > 0:
                        sales_amount += float(s.received)
                        quantity += 1  # Suma operación
                        
                    if s.method_pay1_id == idMethodPay and float(s.received1) > 0:
                        sales_amount += float(s.received1)
                        quantity += 1  # Suma operación
                        
                    if s.method_pay2_id == idMethodPay and float(s.received2) > 0:
                        sales_amount += float(s.received2)
                        quantity += 1  # Suma operación

                # --- CONTAR Y SUMAR ABONOS DE CRÉDITOS ---
                for c in credits:
                    if c.method_pay_id == idMethodPay:
                        quantity += 1  # Suma operación abono
                        if type_total == '$':
                            payments_amount += float(c.quantity)
                        elif type_total == 'Bs':
                            payments_amount += float(c.quantitybs)

                # --- CONTAR Y SUMAR MOVIMIENTOS DE CAJA ---
                movements = CashMovement.objects.filter(
                    date_time__date__gte=start, 
                    date_time__date__lte=end,
                    method_pay_id=idMethodPay, 
                    status=1
                )
                for mov in movements:
                    quantity += 1  # Suma operación movimiento manual
                    if mov.tipo == 'INGRESO':
                        if type_total == '$': cash_in += float(mov.amount_dl)
                        elif type_total == 'Bs': cash_in += float(mov.amount_bs)
                    elif mov.tipo == 'EGRESO':
                        if type_total == '$': cash_out += float(mov.amount_dl)
                        elif type_total == 'Bs': cash_out += float(mov.amount_bs)

                # --- MATEMÁTICA DE CIERRE ---
                net_final = (sales_amount + payments_amount + cash_in) - cash_out
                net_final = round(net_final, 2)
                
                if type_total == '$':
                    grand_total_usd += net_final
                elif type_total == 'Bs':
                    if float(exchange_rate) > 0:
                        grand_total_usd += round(net_final / float(exchange_rate), 2)

                result = {
                    'id': idMethodPay,
                    'method': name,
                    'currency': type_total,
                    'quantity': quantity,  # <--- Agregado al diccionario para tu HTML
                    'sales_amount': round(sales_amount, 2),
                    'payments_amount': round(payments_amount, 2),
                    'cash_in': round(cash_in, 2),
                    'cash_out': round(cash_out, 2),
                    'net_final': round(net_final, 2),
                }
                data.append(result)
                
        except Exception as e:
            print(f"Error generando payment methods report: {e}")
            pass

        return data, round(grand_total_usd, 2)

    def getByTypeSales(self, start, end, exchange_rate):
        data = {}
        cash = credit = payments = 0
        acumulado_usd = acumulado_bs = totalCredit = totalPayments = 0.0

        try:
            allPayments = DetCredit.objects.filter(last_credit_date__gte=start, last_credit_date__lte=end).exclude(operation='+').exclude(status=0)
            allSales = Sale.objects.filter(datejoined__gte=start, datejoined__lte=end).exclude(status=2)
            
            for a in allSales:
                if a.type_sale == 'Al Contado':
                    cash += 1
                    if a.method_pay and a.received > 0:
                        if str(a.method_pay.type_symbol).strip() == 'Bs': acumulado_bs += float(a.received)
                        else: acumulado_usd += float(a.received)
                    
                    if a.method_pay1 and a.received1 > 0:
                        if str(a.method_pay1.type_symbol).strip() == 'Bs': acumulado_bs += float(a.received1)
                        else: acumulado_usd += float(a.received1)
                            
                    if a.method_pay2 and a.received2 > 0:
                        if str(a.method_pay2.type_symbol).strip() == 'Bs': acumulado_bs += float(a.received2)
                        else: acumulado_usd += float(a.received2)
                    
                elif a.type_sale == 'Crédito':
                    credit += 1
                    totalCredit += float(a.total)
                    
            for a in allPayments:
                payments += 1
                totalPayments += float(a.quantity)
                
            totalCash = acumulado_usd + round(acumulado_bs / float(exchange_rate), 2)
                
            data = {
                'cash': cash, 'credit': credit, 'payments': payments,
                'totalCash': round(totalCash, 2),
                'totalCredit': round(totalCredit, 2),
                'totalPayments': round(totalPayments, 2),
            }
        except Exception as e:
            print(f"Error: {e}")
            
        return data

    def getDiscountSales(self, start, end):
        data = []
        try:
            sales = Sale.objects.filter(datejoined__gte=start, datejoined__lte=end, discount__gt=0).exclude(status=2)
            for s in sales:
                info = {
                    'date': s.datejoined.strftime('%d/%m/%Y'),
                    'client': s.client.names + ' ' + s.client.ci,
                    'invoice': '#' + s.invoice_number,
                    'discount': float(s.discount)
                }
                data.append(info)
        except:
            pass
        return data

    def getPayments(self, start, end):
        data = []
        try:
            allPayment = DetCredit.objects.filter(last_credit_date__gte=start, last_credit_date__lte=end, operation='-').exclude(status=0)
            for p in allPayment:
                quantity = 0
                quantityBs = 0
                item = p.toJSON()
                typeSimbol = p.method_pay.type_symbol
                credit = Credit.objects.get(pk=p.credit.id)
                client = credit.client.names + ' ' + ' ' + credit.client.identity + '' + credit.client.ci
                if typeSimbol == '$':
                    quantity += float(item['quantity'])
                elif typeSimbol == 'Bs':
                    quantityBs += float(item['quantitybs'])
                detail = {
                    'date': item['last_credit_date'].strftime('%d/%m/%Y'),
                    'client': client,
                    'method': p.method_pay.name,
                    'quantity': quantity,
                    'quantityBs': quantityBs
                }
                data.append(detail)
        except:
            pass
        return data
    
    def getCashMovements(self, start, end, exchange_rate):
        data = []
        try:
            todos = CashMovement.objects.all().values('tipo', 'amount_bs', 'status', 'date_time__date')
            print("LO QUE REALMENTE HAY EN CAJA:", list(todos))

            allMovements = CashMovement.objects.filter(
                date_time__date__gte=start, 
                date_time__date__lte=end, 
                status=1
            ).order_by('-date_time')
            
            total_ingresos = 0
            total_egresos = 0
            total_ingresos_dl = 0
            total_egresos_dl = 0
            
            for m in allMovements:
                item = m.toJSON()
                
                amount = 0
                amount_bs = float(item['amount_bs'])
                amount_dl = float(item['amount_dl'])

                method = Method_pay.objects.get(pk=m.method_pay.id)

                if(method.type_symbol == 'Bs'):
                    amount = amount_bs
                    if(m.tipo == 'INGRESO'):
                        total_ingresos += amount
                    else:
                        total_egresos += amount
                else:
                    amount = amount_dl
                    if(m.tipo == 'INGRESO'):
                        total_ingresos_dl += amount
                    else:
                        total_egresos_dl += amount
                
                hora_local = timezone.localtime(m.date_time)
                date_formatted = hora_local.strftime('%d/%m/%Y %I:%M %p')
                
                detail = {
                    'date': date_formatted,
                    'user': m.user.username,
                    'tipo': m.tipo,
                    'method': m.method_pay.name,
                    'description': m.description.capitalize(),
                    'amount': amount,
                    'symbol': method.type_symbol
                }
                data.append(detail)

            if float(exchange_rate) > 0:
                ingresos_convertidos_bs = total_ingresos / float(exchange_rate)
                egresos_convertidos_bs = total_egresos / float(exchange_rate)
            else:
                ingresos_convertidos_bs = 0.0
                egresos_convertidos_bs = 0.0
                
            gran_total_ingresos_usd = total_ingresos_dl + ingresos_convertidos_bs
            gran_total_egresos_usd = total_egresos_dl + egresos_convertidos_bs
                
            total_neto_global_usd = gran_total_ingresos_usd - gran_total_egresos_usd
                
            return {
                'movements': data,
                'total_mov_caja': round(total_neto_global_usd, 2)
            }
            
        except Exception as e:
            print(f"Error en getCashMovementsReport: {e}")
            return {'movements': [], 'totals': {}}
    
    def getByProducts(self, start, end):
        data = []
        try:
            allSales = DetSale.objects.filter(sale__datejoined__gte=start, sale__datejoined__lte=end).exclude(sale__status=2)
            
            codes = []
            for i in allSales:
                item = i.toJSON()
                code = {
                    'code': item['prod']['code']
                }
                if not code in codes:
                    codes.append(code)

            totalGeneral = 0
            quantityGeneral = 0
            for i in codes:
                quantity = 0
                prod = 'details'
                price = 0
                total = 0
                for sale in allSales:
                    s = sale.toJSON()
                    if s['prod']['code'] == i['code']:
                        quantity += float(s['quantity'])
                        prod = s['prod']['product'] + ' ' + s['prod']['type_product']['name']
                        price = float(s['prod']['price_dl'])
                        cost = float(s['prod']['cost'])
                        gain = float(s['prod']['price_dl']) - float(s['prod']['cost'])
                        totalQuantity = float(price) * float(s['quantity'])
                        total += totalQuantity
                    else:
                        pass
                product = {
                    'code': i['code'],
                    'quantity': quantity,
                    'prod': prod,
                    'cost': cost,
                    'price': price,
                    'total_dl': price * quantity,
                    'gain': (price - cost) * quantity,
                    'total': total,
                }
                data.append(product)
        except:
            pass
        return data
    
    # @pdf_decorator(pdfname='new_filename.pdf')
    def get(self, request, *args, **kwargs):
        try:
            payMethod = []
            typeSales = []
            byProducts = []
            discountSales = []
            payments = []

            dolar = Dolar.objects.get(pk=1)
            dl = float(dolar.dolar)

            if self.kwargs['type'] == 1: 
                template = get_template('sale/reportSales.html')
                payMethod, grand_total = self.getByPayMethod(self.kwargs['start'], self.kwargs['end'], exchange_rate=dl)
                typeSales = self.getByTypeSales(self.kwargs['start'], self.kwargs['end'], exchange_rate=dl)
                discountSales = self.getDiscountSales(self.kwargs['start'], self.kwargs['end'])
                payments = self.getPayments(self.kwargs['start'], self.kwargs['end'])
                movements = self.getCashMovements(self.kwargs['start'], self.kwargs['end'], exchange_rate=dl)
            elif self.kwargs['type'] == 2:
                template = get_template('sale/reportProducts.html')
                byProducts = self.getByProducts(self.kwargs['start'], self.kwargs['end'])

            print(movements)

            totals = 0
            totalsBs = 0
            try:
                for i in payMethod:
                    totals = float(totals) + float(i['total'])
                    totalsBs = float(totalsBs) + float(i['total_bs'])
            except:
                pass

            totalDiscounts = 0
            try:
                for i in discountSales:
                    totalDiscounts += float(i['discount'])
            except:
                pass

            totalPayments = 0
            totalPaymentsBs = 0
            try:
                for i in payments:
                    totalPayments += float(i['quantity'])
                    totalPaymentsBs += float(i['quantityBs'])
            except:
                pass

            totalsByProducts = 0
            totalProducts = 0
            totalPSales = 0
            try:
                for i in byProducts:
                    totalsByProducts += float(i['total'])
                    totalProducts += float(i['gain'])
                    totalPSales += float(i['total_dl'])
            except:
                pass

            totalIncome = 0
            totalTypeSales = 0
            try:
                totalIncome = float(typeSales['totalCash']) + float(typeSales['totalPayments'])
                totalTypeSales = float(typeSales['totalCash']) + float(typeSales['totalCredit']) + float(typeSales['totalPayments'])
            except:
                pass

            server_url = request.build_absolute_uri('/')
            dataCompany = getCompanyData()
            context = {
                'day': self.kwargs['start'] + ' - ' + self.kwargs['end'],
                'detTypeSales': typeSales,
                'payMethod': payMethod,
                'grand_total_usd': grand_total,
                'totalTypeSales': totalTypeSales,
                'totalIncome': totalIncome,
                'discountSales': discountSales,
                'totalDiscounts': totalDiscounts,
                'totalPayments': totalPayments,
                'totalPaymentsBs': totalPaymentsBs,
                'payments': payments,
                'movements': movements,
                'totals': round(totals, 2),
                'totalsBs': round(totalsBs, 2),
                'byProducts': byProducts,
                'totalsByProducts': totalsByProducts,
                'totalProducts': totalProducts,
                'totalPSales': totalPSales,
                'comp': dataCompany,
                'url': getStaticUrl(),
                'icon': server_url + '/media/img/logo/logo.png',
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
        return HttpResponseRedirect(reverse_lazy('crud:sale_list'))

